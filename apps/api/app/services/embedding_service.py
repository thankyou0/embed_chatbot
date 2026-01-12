import asyncio
import gc
from typing import List, Dict, Any
from uuid import UUID
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from huggingface_hub import InferenceClient
from app.models.knowledge import KnowledgeSource, CrawledPage, Embedding, KnowledgeSourceStatus, KnowledgeSourceType, QAPair
from app.core.database import get_session_factory
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Batch size for embedding generation
EMBEDDING_BATCH_SIZE = 32

# Initialize HuggingFace Inference Client (handles endpoint changes automatically)
_hf_client = None

def get_hf_client() -> InferenceClient:
    """Get or create HuggingFace Inference Client."""
    global _hf_client
    if _hf_client is None:
        api_key = settings.HF_API_KEY
        if not api_key:
            raise ValueError("HF_API_KEY is not set in environment variables")
        _hf_client = InferenceClient(token=api_key)
    return _hf_client


async def get_embeddings_from_api(texts: List[str]) -> List[List[float]]:
    """
    Get embeddings from HuggingFace Inference API using the official SDK.
    Uses the sentence-transformers/all-MiniLM-L6-v2 model which produces 384-dimensional embeddings.
    """
    client = get_hf_client()
    model = settings.EMBEDDING_MODEL
    
    # Run in thread pool since huggingface_hub is synchronous
    loop = asyncio.get_event_loop()
    
    try:
        # Use feature_extraction for sentence-transformers models
        result = await loop.run_in_executor(
            None,
            lambda: client.feature_extraction(
                text=texts,
                model=model
            )
        )
        
        # Handle the result format
        import numpy as np
        embeddings = []
        
        # result can be a list of embeddings or nested arrays
        for item in result:
            if isinstance(item, list) and len(item) > 0:
                if isinstance(item[0], list):
                    # Token-level embeddings - perform mean pooling
                    token_embeddings = np.array(item)
                    pooled = np.mean(token_embeddings, axis=0).tolist()
                    embeddings.append(pooled)
                else:
                    # Already pooled embedding
                    embeddings.append(item)
            else:
                # Single embedding vector
                embeddings.append(list(item) if hasattr(item, '__iter__') else [item])
        
        logger.info(f"Successfully got {len(embeddings)} embeddings from HuggingFace")
        return embeddings
        
    except Exception as e:
        logger.error(f"HuggingFace API error: {e}")
        raise Exception(f"HuggingFace API error: {str(e)}")


async def get_single_embedding(text: str) -> List[float]:
    """Get embedding for a single text string."""
    embeddings = await get_embeddings_from_api([text])
    return embeddings[0]


class EmbeddingService:
    @staticmethod
    def chunk_text(text: str, max_tokens: int = 512, overlap: int = 50, min_tokens: int = 100) -> List[str]:
        """
        Token-aware chunking strategy.
        Splits by paragraphs/headings first, then ensures max_tokens limit.
        Note: Simple word-based tokenization as a proxy for actual tokens if not using a specific tokenizer.
        """
        # Split by structure (double newlines for paragraphs)
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        chunks = []
        current_chunk = []
        current_token_count = 0
        
        for para in paragraphs:
            para_tokens = para.split()
            para_token_count = len(para_tokens)
            
            if current_token_count + para_token_count <= max_tokens:
                current_chunk.extend(para_tokens)
                current_token_count += para_token_count
            else:
                # Save current chunk if it's large enough
                if current_token_count >= min_tokens:
                    chunks.append(" ".join(current_chunk))
                    
                    # Handle overlap: take last 'overlap' words
                    overlap_tokens = current_chunk[-overlap:] if overlap < len(current_chunk) else current_chunk
                    current_chunk = overlap_tokens + para_tokens
                    current_token_count = len(current_chunk)
                else:
                    # If current chunk is too small, just merge with next para anyway
                    current_chunk.extend(para_tokens)
                    current_token_count += para_token_count

        # Add the last chunk if it meets the minimum token requirement
        if current_chunk and (len(current_chunk) >= min_tokens or not chunks):
            chunks.append(" ".join(current_chunk))
            
        return chunks

    @staticmethod
    async def process_knowledge_source(knowledge_source_id: UUID):
        """
        1. Get all crawled_pages for knowledge_source
        2. Chunk each page's content
        3. Generate embeddings for each chunk using HuggingFace API
        4. Store in embeddings table with metadata
        """
        session_factory = get_session_factory()
        async with session_factory() as db:
            try:
                # 1. Fetch the knowledge source and its pages
                stmt = select(KnowledgeSource).where(KnowledgeSource.id == knowledge_source_id)
                result = await db.execute(stmt)
                ks = result.scalar_one_or_none()
                
                if not ks:
                    logger.error(f"Knowledge source {knowledge_source_id} not found for embedding")
                    return

                logger.info(f"Starting embedding pipeline for KS: {ks.id} (Type: {ks.source_type})")
                
                # Update status to indicate we're processing embeddings
                # Keep current status if it's CRAWLING, otherwise set to CRAWLING
                # (We'll update to COMPLETED or FAILED at the end)
                if ks.status != KnowledgeSourceStatus.CRAWLING:
                    await db.execute(
                        update(KnowledgeSource)
                        .where(KnowledgeSource.id == ks.id)
                        .values(status=KnowledgeSourceStatus.CRAWLING)
                    )
                    await db.commit()

                # Fetch all pages
                stmt_pages = select(CrawledPage).where(CrawledPage.knowledge_source_id == ks.id)
                res_pages = await db.execute(stmt_pages)
                pages = res_pages.scalars().all()

                # Fetch all Q&A pairs
                stmt_qa = select(QAPair).where(QAPair.knowledge_source_id == ks.id)
                res_qa = await db.execute(stmt_qa)
                qa_pairs = res_qa.scalars().all()

                if not pages and not qa_pairs:
                    logger.warning(f"No content found to embed for KS: {ks.id}")
                    return

                # Delete existing embeddings for this knowledge source if any (re-processing)
                await db.execute(delete(Embedding).where(Embedding.knowledge_source_id == ks.id))
                await db.commit()

                all_chunks = []
                all_metadata = []

                # Handle Pages
                for page in pages:
                    if not page.content:
                        continue
                    
                    # 2. Chunking
                    chunks = EmbeddingService.chunk_text(page.content)
                    
                    for i, chunk in enumerate(chunks):
                        all_chunks.append(chunk)
                        all_metadata.append({
                            "url": page.url,
                            "title": page.title,
                            "chunk_index": i,
                            "total_chunks": len(chunks)
                        })

                # Handle Q&A Pairs
                for qa in qa_pairs:
                    combined_text = f"Question: {qa.question}\nAnswer: {qa.answer}"
                    all_chunks.append(combined_text)
                    all_metadata.append({
                        "qa_id": str(qa.id),
                        "type": "qa_pair"
                    })

                if not all_chunks:
                    logger.warning(f"No content chunks generated for KS: {ks.id}")
                    return

                # 3. Generate embeddings in batches using HuggingFace API
                total_chunks = len(all_chunks)
                logger.info(f"Generating embeddings for {total_chunks} chunks in batches of {EMBEDDING_BATCH_SIZE}...")
                
                total_stored = 0
                
                for batch_start in range(0, total_chunks, EMBEDDING_BATCH_SIZE):
                    batch_end = min(batch_start + EMBEDDING_BATCH_SIZE, total_chunks)
                    batch_chunks = all_chunks[batch_start:batch_end]
                    batch_metadata = all_metadata[batch_start:batch_end]
                    
                    # Generate embeddings for this batch via HuggingFace API
                    try:
                        batch_embeddings = await get_embeddings_from_api(batch_chunks)
                    except Exception as e:
                        logger.error(f"Failed to get embeddings from API: {e}")
                        raise
                    
                    # 4. Store batch in database
                    for chunk_text, vector, meta in zip(batch_chunks, batch_embeddings, batch_metadata):
                        emb_obj = Embedding(
                            chatbot_id=ks.chatbot_id,
                            knowledge_source_id=ks.id,
                            source_type=ks.source_type,
                            content=chunk_text,
                            embedding=vector,
                            metadata_json=meta,
                            priority_weight=1.0
                        )
                        db.add(emb_obj)
                    
                    # Commit each batch
                    await db.commit()
                    total_stored += len(batch_chunks)
                    
                    # Force garbage collection to free memory
                    gc.collect()
                    
                    logger.info(f"Batch {batch_start // EMBEDDING_BATCH_SIZE + 1}: Stored {total_stored}/{total_chunks} embeddings")

                # Update status to COMPLETED after successful embedding
                await db.execute(
                    update(KnowledgeSource)
                    .where(KnowledgeSource.id == ks.id)
                    .values(status=KnowledgeSourceStatus.COMPLETED)
                )
                await db.commit()
                
                logger.success(f"Successfully processed and stored {total_stored} embeddings for KS: {ks.id}")

            except Exception as e:
                logger.error(f"Error in embedding pipeline for KS {knowledge_source_id}: {str(e)}")
                await db.rollback()
                
                # Update status to FAILED when embeddings fail
                try:
                    await db.execute(
                        update(KnowledgeSource)
                        .where(KnowledgeSource.id == knowledge_source_id)
                        .values(
                            status=KnowledgeSourceStatus.FAILED
                        )
                    )
                    await db.commit()
                    logger.error(f"Updated knowledge source {knowledge_source_id} status to FAILED due to embedding error")
                except Exception as update_error:
                    logger.error(f"Failed to update knowledge source status: {update_error}")
                    await db.rollback()