import asyncio
import hashlib
import urllib.robotparser
from urllib.parse import urljoin, urlparse
from typing import Set, List, Optional, AsyncGenerator, Dict
from datetime import datetime, timezone
import httpx
import trafilatura
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from app.models.knowledge import (
    KnowledgeSource, CrawledPage, KnowledgeSourceStatus, KnowledgeSourceType,
    CrawlHistory, CrawlStatus, CrawlSchedule
)
from app.core.database import get_session_factory
from app.core.logging import get_logger
from app.services.embedding_service import EmbeddingService
from bs4 import BeautifulSoup

logger = get_logger(__name__)

class WebsiteCrawler:
    def __init__(self, base_url: str, max_pages: int = 500):
        # Normalize base_url: ensure it has a scheme and trailing slash if needed
        parsed_base = urlparse(base_url)
        if not parsed_base.scheme:
            base_url = "https://" + base_url
            parsed_base = urlparse(base_url)
        
        self.base_url = base_url
        self.domain = parsed_base.netloc
        self.path_prefix = parsed_base.path or "/"
        self.max_pages = max_pages
        self.visited_urls: Set[str] = set()
        self.queue: List[str] = [base_url]
        self.robot_parser = urllib.robotparser.RobotFileParser()
        self.robot_parser.set_url(urljoin(base_url, "/robots.txt"))
        self._robots_loaded = False
        
    async def _load_robots(self):
        if not self._robots_loaded:
            try:
                # RobotFileParser.read is blocking, but it's just one small file
                # In a high-concurrency app, we'd use a thread or an async alternative
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self.robot_parser.read)
            except Exception as e:
                logger.warning(f"Could not read robots.txt for {self.domain}: {e}")
            self._robots_loaded = True

    async def can_fetch(self, url: str) -> bool:
        await self._load_robots()
        try:
            return self.robot_parser.can_fetch("*", url)
        except:
            return True

    def _is_valid_link(self, url: str) -> bool:
        parsed = urlparse(url)
        # Same domain check
        if parsed.netloc != self.domain:
            return False
        # Same path prefix check
        if not parsed.path.startswith(self.path_prefix):
            return False
        # Already visited
        if url in self.visited_urls or url in self.queue:
            return False
        # Avoid common non-html extensions
        if any(url.lower().endswith(ext) for ext in ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.zip', '.tar', '.xml', '.css', '.js']):
            return False
        return True

    async def crawl(self) -> AsyncGenerator[dict, None]:
        if not await self.can_fetch(self.base_url):
            logger.warning(f"Crawling disallowed by robots.txt for {self.base_url}")
            return

        headers = {
            "User-Agent": "EcomChatbotCrawler/1.0 (Knowledge Base Bot)"
        }

        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True, headers=headers) as client:
            while self.queue and len(self.visited_urls) < self.max_pages:
                url = self.queue.pop(0)
                if url in self.visited_urls:
                    continue
                
                if not await self.can_fetch(url):
                    continue

                self.visited_urls.add(url)
                logger.info(f"Crawling: {url} ({len(self.visited_urls)}/{self.max_pages})")

                try:
                    response = await client.get(url)
                    if response.status_code != 200:
                        continue
                    
                    # Check content type - only process HTML
                    content_type = response.headers.get("content-type", "").lower()
                    if "text/html" not in content_type:
                        continue

                    html_content = response.text
                    
                    # Extract content with trafilatura
                    # favor_precision=True helps getting cleaner main content
                    extracted = trafilatura.extract(html_content, favor_precision=True)
                    
                    # Metadata extraction
                    metadata = trafilatura.extract_metadata(html_content)
                    title = metadata.title if metadata and metadata.title else None
                    
                    if extracted:
                        yield {
                            'url': url,
                            'title': title,
                            'content': extracted
                        }

                    # Extract links for further crawling
                    soup = BeautifulSoup(html_content, 'html.parser')
                    for a in soup.find_all('a', href=True):
                        link = urljoin(url, a['href'])
                        # Clean fragments and normalize
                        link = link.split('#')[0].rstrip('/')
                        
                        if self._is_valid_link(link):
                            self.queue.append(link)
                            
                except Exception as e:
                    logger.error(f"Error crawling {url}: {str(e)}")
                    continue
                
                # Small delay to be polite
                await asyncio.sleep(0.5)

class CrawlerService:
    @staticmethod
    async def start_crawl(
        knowledge_source_id: str,
        base_url: str,
        max_pages: int = 500,
        is_recrawl: bool = False,
        crawl_history_id: Optional[str] = None
    ):
        """
        Entry point for background crawl job with diff detection support.
        """
        session_factory = get_session_factory()
        async with session_factory() as db:
            crawl_history = None
            try:
                if crawl_history_id:
                    # Use existing history entry
                    stmt = select(CrawlHistory).where(CrawlHistory.id == crawl_history_id)
                    result = await db.execute(stmt)
                    crawl_history = result.scalar_one_or_none()
                
                if not crawl_history:
                    # Create crawl history entry if not provided
                    crawl_history = CrawlHistory(
                        knowledge_source_id=knowledge_source_id,
                        started_at=datetime.now(timezone.utc),
                        status=CrawlStatus.SUCCESS,
                        pages_checked=0,
                        pages_added=0,
                        pages_updated=0,
                        pages_removed=0
                    )
                    db.add(crawl_history)
                    await db.commit()
                    await db.refresh(crawl_history)

                # Update status to CRAWLING
                await db.execute(
                    update(KnowledgeSource)
                    .where(KnowledgeSource.id == knowledge_source_id)
                    .values(status=KnowledgeSourceStatus.CRAWLING)
                )
                await db.commit()

                # Get existing pages if this is a recrawl
                existing_pages: Dict[str, CrawledPage] = {}
                if is_recrawl:
                    result = await db.execute(
                        select(CrawledPage).where(
                            and_(
                                CrawledPage.knowledge_source_id == knowledge_source_id,
                                CrawledPage.is_removed == False
                            )
                        )
                    )
                    for page in result.scalars().all():
                        existing_pages[page.url] = page

                # Start crawling
                crawler = WebsiteCrawler(base_url, max_pages)
                crawled_urls = set()
                pages_added = 0
                pages_updated = 0
                
                async for page_data in crawler.crawl():
                    url = page_data['url']
                    content_hash = hashlib.sha256(page_data['content'].encode()).hexdigest()
                    crawled_urls.add(url)
                    
                    if url in existing_pages:
                        # Check if content changed
                        existing_page = existing_pages[url]
                        if existing_page.content_hash != content_hash:
                            # Content changed - update
                            await db.execute(
                                update(CrawledPage)
                                .where(CrawledPage.id == existing_page.id)
                                .values(
                                    title=page_data['title'],
                                    content=page_data['content'],
                                    content_hash=content_hash,
                                    updated_at=datetime.now(timezone.utc)
                                )
                            )
                            pages_updated += 1
                            logger.info(f"Updated page: {url}")
                        # else: Hash match - skip (no change)
                    else:
                        # New URL - add
                        crawled_page = CrawledPage(
                            knowledge_source_id=knowledge_source_id,
                            url=url,
                            title=page_data['title'],
                            content=page_data['content'],
                            content_hash=content_hash,
                            is_removed=False
                        )
                        db.add(crawled_page)
                        pages_added += 1
                        logger.info(f"Added new page: {url}")
                    
                    # Update stats periodically
                    if (pages_added + pages_updated) % 5 == 0:
                        await db.commit()

                # Mark removed pages (URLs that existed before but not found now)
                pages_removed = 0
                if is_recrawl:
                    for url, page in existing_pages.items():
                        if url not in crawled_urls:
                            await db.execute(
                                update(CrawledPage)
                                .where(CrawledPage.id == page.id)
                                .values(is_removed=True, updated_at=datetime.now(timezone.utc))
                            )
                            pages_removed += 1
                            logger.info(f"Marked as removed: {url}")

                # Calculate total pages
                total_pages = len(existing_pages) + pages_added - pages_removed if is_recrawl else pages_added

                # Update crawl history
                await db.execute(
                    update(CrawlHistory)
                    .where(CrawlHistory.id == crawl_history.id)
                    .values(
                        completed_at=datetime.now(timezone.utc),
                        status=CrawlStatus.SUCCESS,
                        pages_checked=len(crawled_urls),
                        pages_added=pages_added,
                        pages_updated=pages_updated,
                        pages_removed=pages_removed
                    )
                )

                # Update knowledge source (keep status as CRAWLING - embeddings will set to COMPLETED or FAILED)
                await db.execute(
                    update(KnowledgeSource)
                    .where(KnowledgeSource.id == knowledge_source_id)
                    .values(
                        pages_found=total_pages
                        # Don't set status to COMPLETED here - let embedding service handle it
                        # Status stays as CRAWLING until embeddings complete
                    )
                )
                
                # Update schedule last_crawl_at
                await db.execute(
                    update(CrawlSchedule)
                    .where(CrawlSchedule.knowledge_source_id == knowledge_source_id)
                    .values(last_crawl_at=datetime.now(timezone.utc))
                )
                
                await db.commit()
                logger.success(
                    f"Crawl completed for {base_url}. "
                    f"Checked: {len(crawled_urls)}, Added: {pages_added}, "
                    f"Updated: {pages_updated}, Removed: {pages_removed}"
                )

                # Trigger embedding process for new/updated pages
                # Embedding service will update status to COMPLETED on success or FAILED on error
                if pages_added > 0 or pages_updated > 0:
                    await EmbeddingService.process_knowledge_source(knowledge_source_id)
                else:
                    # If no new/updated pages, set status to COMPLETED since no embeddings needed
                    await db.execute(
                        update(KnowledgeSource)
                        .where(KnowledgeSource.id == knowledge_source_id)
                        .values(status=KnowledgeSourceStatus.COMPLETED)
                    )
                    await db.commit()

            except Exception as e:
                logger.error(f"Crawl failed for {base_url}: {str(e)}")
                
                # Update crawl history with error
                if crawl_history:
                    try:
                        await db.execute(
                            update(CrawlHistory)
                            .where(CrawlHistory.id == crawl_history.id)
                            .values(
                                completed_at=datetime.now(timezone.utc),
                                status=CrawlStatus.FAILED,
                                error_message=str(e)
                            )
                        )
                        await db.commit()
                    except:
                        pass
                
                # Update knowledge source status
                try:
                    await db.execute(
                        update(KnowledgeSource)
                        .where(KnowledgeSource.id == knowledge_source_id)
                        .values(status=KnowledgeSourceStatus.FAILED)
                    )
                    await db.commit()
                except:
                    pass


