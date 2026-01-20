import asyncio
import hashlib
import urllib.robotparser
from urllib.parse import urljoin, urlparse
from typing import Set, List, Optional, AsyncGenerator, Dict
from datetime import datetime, timezone
import httpx
import trafilatura
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, func
from app.models.knowledge import (
    KnowledgeSource, CrawledPage, KnowledgeSourceStatus, KnowledgeSourceType,
    CrawlHistory, CrawlStatus, CrawlSchedule
)
from app.core.database import get_session_factory
from app.core.logging import get_logger
from app.services.embedding_service import EmbeddingService
from app.services.product_extractor import extract_product_data
from bs4 import BeautifulSoup

logger = get_logger(__name__)

class WebsiteCrawler:
    def __init__(self, base_url: str, max_pages: int = 100):
        # Normalize base_url: ensure it has a scheme and trailing slash if needed
        parsed_base = urlparse(base_url)
        if not parsed_base.scheme:
            base_url = "https://" + base_url
            parsed_base = urlparse(base_url)
        
        self.base_url = base_url
        self.domain = parsed_base.netloc
        # Don't restrict to path prefix - allow crawling entire domain
        # This is important because category pages (/category-view/shop) 
        # link to product pages (/product-detail/item) which have different paths
        self.path_prefix = "/"  # Allow all paths on the domain
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
        # Note: robots.txt check is now done by the caller before calling this method
        
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
                    
                    # Extract contact information from links (phone, email)
                    # These are often in <a> tags and get stripped by trafilatura
                    soup = BeautifulSoup(html_content, 'html.parser')
                    contact_info = []
                    
                    # Extract emails from mailto: links and phone from tel: links
                    for a in soup.find_all('a', href=True):
                        href = a.get('href', '')
                        if href.startswith('mailto:'):
                            email = href.replace('mailto:', '').split('?')[0].strip()
                            if email and extracted and email not in extracted:
                                contact_info.append(f"Email: {email}")
                        elif href.startswith('tel:'):
                            phone = href.replace('tel:', '').strip()
                            # Clean up phone number formatting
                            phone = phone.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
                            if phone and extracted and phone not in extracted:
                                contact_info.append(f"Phone: {phone}")
                    
                    # Append contact info to extracted content if found
                    if contact_info and extracted:
                        extracted += "\n\nContact Information:\n" + "\n".join(set(contact_info))
                    
                    # Extract product data (returns None for non-product pages)
                    product_data = extract_product_data(html_content, url)
                    
                    # Prepare content for embedding (concatenate with product info if available)
                    # This helps the AI find price/brand info during semantic search
                    content_to_store = extracted
                    if product_data:
                        product_summary = "\n\nProduct Information:\n"
                        if product_data.get('name'):
                            product_summary += f"- Name: {product_data.get('name')}\n"
                        if product_data.get('price'):
                            product_summary += f"- Price: {product_data.get('price')} {product_data.get('currency', '')}\n"
                        if product_data.get('brand'):
                            product_summary += f"- Brand: {product_data.get('brand')}\n"
                        if product_data.get('availability'):
                            product_summary += f"- Status: {product_data.get('availability')}\n"
                        
                        content_to_store = product_summary + "\n" + extracted

                    if extracted:
                        yield {
                            'url': url,
                            'title': title,
                            'content': content_to_store,
                            'is_product': product_data is not None,
                            'product_metadata': product_data
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
        max_pages: int = 100,
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

                # Get existing pages for this knowledge source (for recrawl detection)
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

                # Get the chatbot_id to check for duplicates across all knowledge sources
                ks_stmt = select(KnowledgeSource).where(KnowledgeSource.id == knowledge_source_id)
                ks_result = await db.execute(ks_stmt)
                current_ks = ks_result.scalar_one_or_none()
                if not current_ks:
                    raise ValueError(f"Knowledge source {knowledge_source_id} not found")
                
                # Get all URLs already crawled for this chatbot (across all knowledge sources)
                # This prevents duplicate pages when crawling from different starting URLs
                chatbot_existing_urls: Set[str] = set()
                all_ks_result = await db.execute(
                    select(CrawledPage.url).join(
                        KnowledgeSource, 
                        KnowledgeSource.id == CrawledPage.knowledge_source_id
                    ).where(
                        and_(
                            KnowledgeSource.chatbot_id == current_ks.chatbot_id,
                            CrawledPage.is_removed == False,
                            CrawledPage.knowledge_source_id != knowledge_source_id  # Exclude current source
                        )
                    )
                )
                for row in all_ks_result.scalars().all():
                    chatbot_existing_urls.add(row)

                # Start crawling
                crawler = WebsiteCrawler(base_url, max_pages)
                
                # Check robots.txt BEFORE starting the crawl loop
                if not await crawler.can_fetch(base_url):
                    # Robots.txt disallows crawling - fail immediately
                    error_msg = f"Crawling disallowed by robots.txt for {base_url}"
                    logger.error(error_msg)
                    raise PermissionError(error_msg)
                
                crawled_urls = set()
                pages_added = 0
                pages_updated = 0
                pages_skipped = 0  # Track URLs skipped due to existing in other knowledge sources
                
                async for page_data in crawler.crawl():
                    url = page_data['url']
                    content_hash = hashlib.sha256(page_data['content'].encode()).hexdigest()
                    crawled_urls.add(url)
                    
                    # Extract product info from page_data
                    is_product = page_data.get('is_product', False)
                    product_metadata = page_data.get('product_metadata')
                    
                    # FIRST: Check if URL already exists in other knowledge sources for this chatbot
                    if url in chatbot_existing_urls:
                        pages_skipped += 1
                        logger.info(f"Skipping duplicate URL (already in another knowledge source): {url}")
                        continue
                    
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
                                    is_product=is_product,
                                    product_metadata=product_metadata,
                                    updated_at=datetime.now(timezone.utc)
                                )
                            )
                            pages_updated += 1
                            logger.info(f"Updated page: {url} (is_product: {is_product})")
                        # else: Hash match - skip (no change)
                    else:
                        # New URL - add
                        crawled_page = CrawledPage(
                            knowledge_source_id=knowledge_source_id,
                            url=url,
                            title=page_data['title'],
                            content=page_data['content'],
                            content_hash=content_hash,
                            is_removed=False,
                            is_product=is_product,
                            product_metadata=product_metadata
                        )
                        db.add(crawled_page)
                        pages_added += 1
                        logger.info(f"Added new page: {url} (is_product: {is_product})")
                    
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

                # Clean up embeddings for removed pages if any were removed
                if pages_removed > 0:
                    logger.info(f"Cleaning up embeddings for {pages_removed} removed pages...")
                    await EmbeddingService.cleanup_removed_pages_embeddings(knowledge_source_id)

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
                    f"Updated: {pages_updated}, Removed: {pages_removed}, "
                    f"Skipped (duplicates): {pages_skipped}"
                )

                # Check if we actually crawled any pages (first crawl)
                if not is_recrawl and len(crawled_urls) == 0:
                    # No pages were found - this is a failure for initial crawl
                    error_msg = f"No pages could be crawled from {base_url}. The website may be blocking our crawler or have no accessible content."
                    logger.error(error_msg)
                    
                    # Update status to FAILED
                    await db.execute(
                        update(KnowledgeSource)
                        .where(KnowledgeSource.id == knowledge_source_id)
                        .values(
                            status=KnowledgeSourceStatus.FAILED,
                            error_message=error_msg
                        )
                    )
                    
                    # Update crawl history
                    if crawl_history:
                        await db.execute(
                            update(CrawlHistory)
                            .where(CrawlHistory.id == crawl_history.id)
                            .values(
                                completed_at=datetime.now(timezone.utc),
                                status=CrawlStatus.FAILED,
                                error_message=error_msg
                            )
                        )
                    
                    await db.commit()
                    
                    # Log activity for the error
                    from app.models.chatbot import ChatbotActivity
                    ks_stmt = select(KnowledgeSource).where(KnowledgeSource.id == knowledge_source_id)
                    ks_result = await db.execute(ks_stmt)
                    ks = ks_result.scalar_one_or_none()
                    if ks:
                        activity = ChatbotActivity(
                            chatbot_id=ks.chatbot_id,
                            user_id=None,
                            activity_type="crawl_failed",
                            description=f"Crawl failed for {base_url}: No accessible pages found"
                        )
                        db.add(activity)
                        await db.commit()
                    return

                # Trigger embedding process for new/updated pages
                # Embedding service will update status to COMPLETED on success or FAILED on error
                if pages_added > 0 or pages_updated > 0:
                    await EmbeddingService.process_knowledge_source(knowledge_source_id)
                else:
                    # If no new/updated pages, check if embeddings exist
                    # This handles the case where crawling succeeded before but embedding failed
                    from app.models.knowledge import Embedding
                    embedding_count_stmt = select(func.count(Embedding.id)).where(
                        Embedding.knowledge_source_id == knowledge_source_id
                    )
                    embedding_count = (await db.execute(embedding_count_stmt)).scalar() or 0
                    
                    if embedding_count == 0:
                        # No embeddings exist - need to regenerate them
                        logger.info(f"No embeddings found for KS {knowledge_source_id}, regenerating...")
                        await EmbeddingService.process_knowledge_source(knowledge_source_id)
                    else:
                        # Embeddings exist and no content changes - set to COMPLETED
                        await db.execute(
                            update(KnowledgeSource)
                            .where(KnowledgeSource.id == knowledge_source_id)
                            .values(
                                status=KnowledgeSourceStatus.COMPLETED,
                                error_message=None  # Clear any previous error
                            )
                        )
                        await db.commit()

            except Exception as e:
                error_msg = str(e)
                logger.error(f"Crawl failed for {base_url}: {error_msg}")
                
                # Update crawl history with error
                if crawl_history:
                    try:
                        await db.execute(
                            update(CrawlHistory)
                            .where(CrawlHistory.id == crawl_history.id)
                            .values(
                                completed_at=datetime.now(timezone.utc),
                                status=CrawlStatus.FAILED,
                                error_message=error_msg
                            )
                        )
                        await db.commit()
                    except:
                        pass
                
                # Update knowledge source status with error message
                try:
                    await db.execute(
                        update(KnowledgeSource)
                        .where(KnowledgeSource.id == knowledge_source_id)
                        .values(
                            status=KnowledgeSourceStatus.FAILED,
                            error_message=f"Crawl failed: {error_msg}"
                        )
                    )
                    await db.commit()
                    
                    # Log activity for the error
                    from app.models.chatbot import ChatbotActivity
                    ks_stmt = select(KnowledgeSource).where(KnowledgeSource.id == knowledge_source_id)
                    ks_result = await db.execute(ks_stmt)
                    ks = ks_result.scalar_one_or_none()
                    if ks:
                        # Truncate error message for activity description
                        short_error = error_msg[:200] + "..." if len(error_msg) > 200 else error_msg
                        activity = ChatbotActivity(
                            chatbot_id=ks.chatbot_id,
                            user_id=None,  # System action
                            activity_type="crawl_failed",
                            description=f"Crawl failed for {base_url}: {short_error}"
                        )
                        db.add(activity)
                        await db.commit()
                except:
                    pass


