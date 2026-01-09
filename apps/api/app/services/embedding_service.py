import asyncio
import httpx
from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.knowledge import KnowledgeSource, CrawledPage, Embedding, KnowledgeSourceStatus, KnowledgeSourceType, QAPair
from app.core.database import get_session_factory
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Hugging Face Inference API configuration
# Using all-MiniLM-L6-v2 model (384-dimensional embeddings)
HF_API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"


class EmbeddingService:
    """
    Embedding service using Hugging Face Inference API (free tier).
    No heavy model downloads required - uses API for embeddings.
    """
    
    @staticmethod
    async def get_embeddings_from_api(texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Get embeddings from Hugging Face Inference API.
        Free tier: ~30,000 characters per request.
        """
        all_embeddings = []
        
        # Get API key from settings (optional - HF has some free usage without key)
        headers = {}
        if hasattr(settings, 'HF_API_KEY') and settings.HF_API_KEY:
            headers["Authorization"] = f"Bearer {settings.HF_API_KEY}"
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Process in batches
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                try:
                    response = await client.post(
                        HF_API_URL,
                        headers=headers,
                        json={
                            "inputs": batch,
                            "options": {"wait_for_model": True}
                        }
                    )
                    
                    if response.status_code == 200:
                        embeddings = response.json()
                        # Handle nested response format
                        for emb in embeddings:
                            if isinstance(emb[0], list):
                                # Mean pooling if we get token-level embeddings
                                pooled = [sum(x) / len(emb) for x in zip(*emb)]
                                all_embeddings.append(pooled)
                            else:
                                all_embeddings.append(emb)
                    elif response.status_code == 503:
                        # Model is loading, wait and retry
                        logger.warning("Model is loading, waiting 20 seconds...")
                        await asyncio.sleep(20)
                        # Retry this batch
                        response = await client.post(
                            HF_API_URL,
                            headers=headers,
                            json={
                                "inputs": batch,
                                "options": {"wait_for_model": True}
                            }
                        )
                        if response.status_code == 200:
                            embeddings = response.json()
                            for emb in embeddings:
                                if isinstance(emb[0], list):
                                    pooled = [sum(x) / len(emb) for x in zip(*emb)]
                                    all_embeddings.append(pooled)
                                else:
                                    all_embeddings.append(emb)
                        else:
                            logger.error(f"HF API error after retry: {response.status_code} - {response.text}")
                            # Use fallback zero embeddings
                            all_embeddings.extend([[0.0] * 384 for _ in batch])
                    else:
                        logger.error(f"HF API error: {response.status_code} - {response.text}")
                        # Use fallback zero embeddings
                        all_embeddings.extend([[0.0] * 384 for _ in batch])
                        
                except Exception as e:
                    logger.error(f"Error calling HF API: {str(e)}")
                    # Use fallback zero embeddings
                    all_embeddings.extend([[0.0] * 384 for _ in batch])
                
                # Rate limiting - small delay between batches
                if i + batch_size < len(texts):
                    await asyncio.sleep(0.5)
        
        return all_embeddings

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
        3. Generate embeddings for each chunk using HF API
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

                # 3. Generate embeddings using HF API
                logger.info(f"Generating embeddings for {len(all_chunks)} chunks using HF API...")
                embeddings_list = await EmbeddingService.get_embeddings_from_api(all_chunks)

                # 4. Store in database
                for chunk_text, vector, meta in zip(all_chunks, embeddings_list, all_metadata):
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

                await db.commit()
                logger.success(f"Successfully processed and stored {len(all_chunks)} embeddings for KS: {ks.id}")

            except Exception as e:
                logger.error(f"Error in embedding pipeline for KS {knowledge_source_id}: {str(e)}")
                await db.rollback()


# For query embeddings (used in chat/search)
async def get_query_embedding(query: str) -> List[float]:
    """Get embedding for a single query using HF API."""
    embeddings = await EmbeddingService.get_embeddings_from_api([query])
    return embeddings[0] if embeddings else [0.0] * 384
