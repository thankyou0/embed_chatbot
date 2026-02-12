#!/usr/bin/env python3
"""
One-time cleanup script to remove embeddings for already removed pages.
Run this after deploying the embedding cleanup fixes.

Usage:
    docker-compose exec api python cleanup_embeddings.py
"""

import asyncio
from sqlalchemy import select, delete, and_
from app.core.database import get_session_factory
from app.models.knowledge import Embedding, CrawledPage, KnowledgeSource
from app.core.logging import get_logger

logger = get_logger(__name__)

async def cleanup_orphaned_embeddings():
    """Remove embeddings for pages that are marked as removed"""
    session_factory = get_session_factory()
    async with session_factory() as db:
        try:
            # Find all removed pages across all knowledge sources
            removed_pages_stmt = select(
                CrawledPage.url,
                CrawledPage.knowledge_source_id
            ).where(CrawledPage.is_removed == True)
            
            result = await db.execute(removed_pages_stmt)
            removed_pages = result.fetchall()
            
            if not removed_pages:
                logger.info("✅ No removed pages found - nothing to clean up")
                return

            logger.info(f"🔍 Found {len(removed_pages)} removed pages to clean up...")
            
            total_deleted = 0
            for url, ks_id in removed_pages:
                # Delete embeddings for this specific removed page
                delete_stmt = delete(Embedding).where(
                    and_(
                        Embedding.knowledge_source_id == ks_id,
                        Embedding.metadata_json['url'].astext == url
                    )
                )
                result = await db.execute(delete_stmt)
                deleted_count = result.rowcount
                total_deleted += deleted_count
                
                if deleted_count > 0:
                    logger.info(f"🗑️  Removed {deleted_count} embeddings for: {url}")

            await db.commit()
            logger.info(f"✅ Cleanup completed! Deleted {total_deleted} orphaned embeddings.")

        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")
            await db.rollback()
            raise


async def main():
    logger.info("🧹 Starting orphaned embeddings cleanup...")
    await cleanup_orphaned_embeddings()
    logger.info("🎉 Cleanup finished!")


if __name__ == "__main__":
    asyncio.run(main())