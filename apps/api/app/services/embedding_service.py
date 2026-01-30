import asyncio
import gc
from typing import List, Dict, Any
from uuid import UUID
from sqlalchemy import select, delete, update, and_, text
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
                if ks.status != KnowledgeSourceStatus.PROCESSING:
                    await db.execute(
                        update(KnowledgeSource)
                        .where(KnowledgeSource.id == knowledge_source_id)
                        .values(status=KnowledgeSourceStatus.PROCESSING)
                    )
                    await db.commit()

                # Fetch all active pages (not removed)
                stmt_pages = select(CrawledPage).where(
                    and_(
                        CrawledPage.knowledge_source_id == ks.id,
                        CrawledPage.is_removed == False
                    )
                )
                res_pages = await db.execute(stmt_pages)
                pages = res_pages.scalars().all()

                # Fetch all Q&A pairs
                stmt_qa = select(QAPair).where(QAPair.knowledge_source_id == ks.id)
                res_qa = await db.execute(stmt_qa)
                qa_pairs = res_qa.scalars().all()

                if not pages and not qa_pairs:
                    # No content to embed - mark as FAILED
                    error_msg = "No content found to embed. The crawled pages may be empty or the website may have blocked content extraction."
                    logger.warning(f"No content found to embed for KS: {ks.id}")
                    
                    await db.execute(
                        update(KnowledgeSource)
                        .where(KnowledgeSource.id == ks.id)
                        .values(
                            status=KnowledgeSourceStatus.FAILED,
                            error_message=error_msg
                        )
                    )
                    await db.commit()
                    
                    # Log activity
                    from app.models.chatbot import ChatbotActivity
                    activity = ChatbotActivity(
                        chatbot_id=ks.chatbot_id,
                        user_id=None,
                        activity_type="embedding_failed",
                        description=f"No content found to embed for knowledge source"
                    )
                    db.add(activity)
                    await db.commit()
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
                        
                        # Determine if this is a product page
                        # Check both is_product flag AND if product_metadata exists (fallback)
                        has_product_data = (
                            (hasattr(page, 'is_product') and page.is_product) or 
                            (hasattr(page, 'product_metadata') and page.product_metadata)
                        )
                        
                        # Build metadata - include product info if available
                        chunk_metadata = {
                            "url": page.url,
                            "title": page.title,
                            "chunk_index": i,
                            "total_chunks": len(chunks),
                            "is_product": has_product_data
                        }
                        
                        # Add product metadata for product pages
                        if has_product_data and hasattr(page, 'product_metadata') and page.product_metadata:
                            # Include key product fields in embedding metadata
                            product_meta = page.product_metadata
                            chunk_metadata["product"] = {
                                "name": product_meta.get("name"),
                                "price": product_meta.get("price"),
                                "currency": product_meta.get("currency"),
                                "images": product_meta.get("images", [])[:3],  # Limit to 3 images
                                "availability": product_meta.get("availability"),
                                "rating": product_meta.get("rating"),
                                "review_count": product_meta.get("review_count"),
                                "brand": product_meta.get("brand"),
                            }
                        
                        all_metadata.append(chunk_metadata)

                # Handle Q&A Pairs
                for qa in qa_pairs:
                    combined_text = f"Question: {qa.question}\nAnswer: {qa.answer}"
                    all_chunks.append(combined_text)
                    all_metadata.append({
                        "qa_id": str(qa.id),
                        "type": "qa_pair"
                    })

                if not all_chunks:
                    logger.warning(f"No content chunks generated for KS: {knowledge_source_id}")
                    await db.execute(
                        update(KnowledgeSource)
                        .where(KnowledgeSource.id == knowledge_source_id)
                        .values(status=KnowledgeSourceStatus.COMPLETED)
                    )
                    await db.commit()
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
                # Keep existing error_message if it contains a warning (like quota reached)
                # Only clear error messages that indicate actual failures
                update_values = {
                    'status': KnowledgeSourceStatus.COMPLETED
                }
                
                # Only clear error_message if it doesn't contain warnings like "quota"
                if not ks.error_message or 'quota' not in ks.error_message.lower():
                    update_values['error_message'] = None
                
                await db.execute(
                    update(KnowledgeSource)
                    .where(KnowledgeSource.id == knowledge_source_id)
                    .values(**update_values)
                )
                # Commit immediately so frontend polling sees the updated status without manual refresh
                await db.commit()
                
                logger.success(f"Successfully processed and stored {total_stored} embeddings for KS: {ks.id}")

            except Exception as e:
                error_msg = str(e)
                logger.error(f"Error in embedding pipeline for KS {knowledge_source_id}: {error_msg}")
                await db.rollback()
                
                # Update status to FAILED with error message
                try:
                    # Get the knowledge source to get chatbot_id
                    stmt = select(KnowledgeSource).where(KnowledgeSource.id == knowledge_source_id)
                    result = await db.execute(stmt)
                    ks_for_error = result.scalar_one_or_none()
                    
                    await db.execute(
                        update(KnowledgeSource)
                        .where(KnowledgeSource.id == knowledge_source_id)
                        .values(
                            status=KnowledgeSourceStatus.FAILED,
                            error_message=f"Embedding generation failed: {error_msg}"
                        )
                    )
                    await db.commit()
                    
                    # Log activity for the error
                    if ks_for_error:
                        from app.models.chatbot import ChatbotActivity
                        short_error = error_msg[:200] + "..." if len(error_msg) > 200 else error_msg
                        activity = ChatbotActivity(
                            chatbot_id=ks_for_error.chatbot_id,
                            user_id=None,  # System action
                            activity_type="embedding_failed",
                            description=f"Embedding generation failed: {short_error}"
                        )
                        db.add(activity)
                        await db.commit()
                    
                    logger.error(f"Updated knowledge source {knowledge_source_id} status to FAILED due to embedding error")
                except Exception as update_error:
                    logger.error(f"Failed to update knowledge source status: {update_error}")
                    await db.rollback()
                
                # Re-raise the exception so the caller (like _process_uploaded_file) knows it failed
                raise e

    @staticmethod
    async def process_single_qa_pair(qa_id: UUID):
        """
        Re-embed a single QA pair efficiently without affecting KnowledgeSource status.
        Ensures the UI doesn't flicker to 'Processing' for a simple update.
        """
        session_factory = get_session_factory()
        async with session_factory() as db:
            try:
                # 1. Fetch QA pair
                stmt = select(QAPair).where(QAPair.id == qa_id)
                result = await db.execute(stmt)
                qa = result.scalar_one_or_none()
                if not qa:
                    logger.error(f"QA pair {qa_id} not found for re-embedding")
                    return

                # Get KS for metadata
                stmt_ks = select(KnowledgeSource).where(KnowledgeSource.id == qa.knowledge_source_id)
                ks_res = await db.execute(stmt_ks)
                ks = ks_res.scalar_one()

                # 2. Delete existing embedding for this specific pair
                qa_id_str = str(qa_id)
                await db.execute(
                    delete(Embedding).where(
                        and_(
                            Embedding.knowledge_source_id == qa.knowledge_source_id,
                            text(f"metadata_json->>'qa_id' = '{qa_id_str}'")
                        )
                    )
                )

                # 3. Generate new embedding
                combined_text = f"Question: {qa.question}\nAnswer: {qa.answer}"
                vector = await get_single_embedding(combined_text)

                # 4. Store new embedding
                emb_obj = Embedding(
                    chatbot_id=ks.chatbot_id,
                    knowledge_source_id=qa.knowledge_source_id,
                    source_type=KnowledgeSourceType.QA_PAIR,
                    content=combined_text,
                    embedding=vector,
                    metadata_json={"qa_id": str(qa_id), "type": "qa_pair"},
                    priority_weight=1.0
                )
                db.add(emb_obj)
                await db.commit()
                logger.success(f"Successfully re-embedded QA pair: {qa_id}")

            except Exception as e:
                logger.error(f"Error re-embedding QA pair {qa_id}: {e}")
                await db.rollback()

    @staticmethod
    async def cleanup_removed_pages_embeddings(knowledge_source_id: UUID):
        """
        Clean up embeddings for pages that have been marked as removed.
        This should be called after crawling when pages are marked as removed.
        """
        session_factory = get_session_factory()
        async with session_factory() as db:
            try:
                # Get all removed pages for this knowledge source
                stmt = select(CrawledPage.url).where(
                    and_(
                        CrawledPage.knowledge_source_id == knowledge_source_id,
                        CrawledPage.is_removed == True
                    )
                )
                result = await db.execute(stmt)
                removed_urls = [row[0] for row in result.fetchall()]
                
                if not removed_urls:
                    logger.info(f"No removed pages to clean up embeddings for KS: {knowledge_source_id}")
                    return

                # Delete embeddings for removed pages
                # Use JSON contains query to find embeddings with matching URLs
                deleted_count = 0
                for url in removed_urls:
                    delete_stmt = delete(Embedding).where(
                        and_(
                            Embedding.knowledge_source_id == knowledge_source_id,
                            Embedding.metadata_json['url'].astext == url
                        )
                    )
                    result = await db.execute(delete_stmt)
                    deleted_count += result.rowcount

                await db.commit()
                logger.info(f"Cleaned up {deleted_count} embeddings for {len(removed_urls)} removed pages from KS: {knowledge_source_id}")

            except Exception as e:
                logger.error(f"Error cleaning up embeddings for removed pages: {e}")
                await db.rollback()
                    
                