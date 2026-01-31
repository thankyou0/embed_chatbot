import asyncio
import hashlib
import urllib.robotparser
from urllib.parse import urljoin, urlparse
from typing import Set, List, Optional, AsyncGenerator, Dict
from datetime import datetime, timezone, timedelta
import httpx
import trafilatura
from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, func
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
    def __init__(self, base_url: str):
        # Normalize base_url: ensure it has a scheme and trailing slash if needed
        parsed_base = urlparse(base_url)
        if not parsed_base.scheme:
            base_url = "https://" + base_url
            parsed_base = urlparse(base_url)
        
        self.base_url = base_url
        self.domain = parsed_base.netloc
        
        # Extract actual path from URL to use as prefix
        # Example: https://example.com/collections/shirts -> /collections/shirts
        # This restricts crawling to only pages under this path
        self.path_prefix = parsed_base.path.rstrip('/') or '/'
        
        self.visited_urls: Set[str] = set()
        self.queue: List[str] = [base_url]
        self.robot_parser = urllib.robotparser.RobotFileParser()
        self.robot_parser.set_url(urljoin(base_url, "/robots.txt"))
        self._robots_loaded = False
        
        logger.info(f"Initialized crawler for domain: {self.domain}, path prefix: {self.path_prefix}")
        
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

    def _get_url_depth(self, url: str) -> int:
        """Calculate depth of URL path (number of segments)"""
        parsed = urlparse(url)
        path = parsed.path.strip('/')
        return len([p for p in path.split('/') if p]) if path else 0
    
    def _get_path_similarity(self, url: str, reference_url: str) -> int:
        """Calculate how many path segments match between two URLs"""
        parsed1 = urlparse(url)
        parsed2 = urlparse(reference_url)
        
        path1_parts = [p for p in parsed1.path.strip('/').split('/') if p]
        path2_parts = [p for p in parsed2.path.strip('/').split('/') if p]
        
        # Count matching segments from the start
        matches = 0
        for p1, p2 in zip(path1_parts, path2_parts):
            if p1 == p2:
                matches += 1
            else:
                break
        return matches
    
    def _sort_queue_by_priority(self, current_url: str):
        """Sort queue for Smart DFS: prioritize similar paths and deeper URLs"""
        if len(self.queue) <= 1:
            return
        
        def priority_score(url: str) -> tuple:
            # Higher similarity = crawl first (negative for sorting)
            similarity = -self._get_path_similarity(url, current_url)
            # Higher depth = crawl first (negative for sorting)
            depth = -self._get_url_depth(url)
            return (similarity, depth, url)
        
        self.queue.sort(key=priority_score)
    
    def _is_valid_link(self, url: str) -> bool:
        parsed = urlparse(url)
        # Same domain check
        if parsed.netloc != self.domain:
            return False
        # Same path prefix check - URL must start with the path prefix
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
            # Quota_limit in start_crawl() will stop crawling
            while self.queue:
                # Sort queue by priority before each pop (Smart DFS)
                current_context = list(self.visited_urls)[-1] if self.visited_urls else self.base_url
                self._sort_queue_by_priority(current_context)
                
                # Pop from front (will be highest priority due to sorting)
                url = self.queue.pop(0)
                if url in self.visited_urls:
                    continue
                
                if not await self.can_fetch(url):
                    continue

                self.visited_urls.add(url)
                logger.info(f"Crawling [{self._get_url_depth(url)}]: {url} (Page #{len(self.visited_urls)})")

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
                            'title': title,
                            'url': url,
                            'content': content_to_store,
                            'is_product': product_data is not None,
                            'product_metadata': product_data
                        }

                    # Extract links for further crawling
                    soup = BeautifulSoup(html_content, 'html.parser')
                    new_links = []
                    for a in soup.find_all('a', href=True):
                        link = urljoin(url, a['href'])
                        # Clean fragments and normalize
                        link = link.split('#')[0].rstrip('/')
                        
                        if self._is_valid_link(link):
                            new_links.append(link)
                    
                    # Add all new links at once
                    self.queue.extend(new_links)
                    logger.debug(f"Found {len(new_links)} new valid links from {url}")
                            
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
        is_recrawl: bool = False,
        crawl_history_id: Optional[str] = None,
        quota_limit: Optional[int] = None,  # New parameter for quota enforcement
        background_tasks: Optional[BackgroundTasks] = None
    ):
        """
        Entry point for background crawl job with diff detection support and quota management.
        
        Args:
            knowledge_source_id: ID of the knowledge source
            base_url: Starting URL to crawl
            is_recrawl: Whether this is a recrawl of existing source
            crawl_history_id: ID of crawl history entry (if exists)
            quota_limit: Total page quota remaining (None = unlimited)
            background_tasks: Optional FastAPI background tasks for chaining
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
                    # Load BOTH active and removed pages to support resurrection
                    result = await db.execute(
                        select(CrawledPage).where(
                            CrawledPage.knowledge_source_id == knowledge_source_id
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

                # Pre-validate the URL to provide specific feedback to the user
                try:
                    headers = {"User-Agent": "EcomChatbotCrawler/1.0 (Knowledge Base Bot)"}
                    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True, headers=headers) as client:
                        response = await client.get(base_url)
                        if response.status_code == 404:
                            raise ValueError(f"The URL could not be found (404). Please check for typos in the address.")
                        elif response.status_code == 403:
                            raise ValueError(f"Access to this site is forbidden (403). The website may be using bot protection or a firewall to block automated crawlers.")
                        elif response.status_code >= 400:
                            raise ValueError(f"The website returned an error (Status {response.status_code}). The site might be temporarily down or blocking our request.")
                        
                        ctype = response.headers.get("content-type", "").lower()
                        if "text/html" not in ctype:
                             # Provide specific message for non-HTML files
                             file_type = ctype.split(';')[0].split('/')[-1].upper() if '/' in ctype else "binary"
                             raise ValueError(f"The URL points to a {file_type} file, not a webpage. We can only crawl HTML websites.")
                             
                except httpx.ConnectError:
                    raise ValueError(f"Could not connect to the domain. Please check if the URL is correct or if the site is online.")
                except httpx.TimeoutException:
                     raise ValueError(f"The website took too long to respond. It might be under heavy load or intentionally blocking our access.")
                except Exception as e:
                    if isinstance(e, ValueError): raise e
                    logger.warning(f"URL pre-check encountered an issue but proceeding: {e}")

                # Start crawling
                crawler = WebsiteCrawler(base_url)
                
                # Check robots.txt BEFORE starting the crawl loop
                if not await crawler.can_fetch(base_url):
                    # robots.txt disallows crawling - provide specific friendly message
                    raise PermissionError(f"This website explicitly blocks automated crawling in its 'robots.txt' file. We must respect their policy and cannot process this URL.")
                
                crawled_urls = set()
                pages_added = 0
                pages_updated = 0
                pages_skipped = 0  # Track URLs skipped due to existing in other knowledge sources
                quota_reached = False  # Track if quota limit was hit
                
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
                    
                    # CHECK QUOTA LIMIT BEFORE PROCESSING: Stop if we've reached the quota
                    # This prevents going over limit by checking BEFORE adding new pages
                    if quota_limit is not None and url not in existing_pages:
                        # Count total pages across all sources for this chatbot
                        total_pages_stmt = select(func.count(CrawledPage.id)).join(
                            KnowledgeSource,
                            KnowledgeSource.id == CrawledPage.knowledge_source_id
                        ).where(
                            KnowledgeSource.chatbot_id == current_ks.chatbot_id,
                            CrawledPage.is_removed == False
                        )
                        total_result = await db.execute(total_pages_stmt)
                        current_total = total_result.scalar() or 0
                        
                        if current_total >= quota_limit:
                            quota_reached = True
                            logger.warning(
                                f"Quota limit reached! Total pages: {current_total}/{quota_limit}. "
                                f"Stopping crawl and processing what we have."
                            )
                            break  # Stop crawling - don't add this page
                    
                    if url in existing_pages:
                        existing_page = existing_pages[url]
                        
                        # 🔁 RESURRECT if page was previously removed
                        resurrected = False
                        if existing_page.is_removed:
                            resurrected = True
                            
                        if existing_page.content_hash != content_hash or resurrected:
                            # Content changed or resurrected - update
                            await db.execute(
                                update(CrawledPage)
                                .where(CrawledPage.id == existing_page.id)
                                .values(
                                    title=page_data['title'],
                                    content=page_data['content'],
                                    content_hash=content_hash,
                                    is_removed=False,  # 🔥 resurrect
                                    is_product=is_product,
                                    product_metadata=product_metadata,
                                    updated_at=datetime.now(timezone.utc)
                                )
                            )
                            
                            if resurrected:
                                logger.info(f"Resurrected page: {url}")
                            else:
                                logger.info(f"Updated page: {url} (is_product: {is_product})")
                                
                            pages_updated += 1
                        # else: Hash match and not removed - skip (no change)
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

                # Calculate total pages for this knowledge source
                ks_total_pages = len(existing_pages) + pages_added - pages_removed if is_recrawl else pages_added
                
                # For quota warnings, we need the CHATBOT total across all sources, not just this KS
                if quota_limit and is_recrawl:
                    # Get actual total across all knowledge sources for this chatbot
                    chatbot_total_stmt = select(func.count(CrawledPage.id)).join(
                        KnowledgeSource,
                        KnowledgeSource.id == CrawledPage.knowledge_source_id
                    ).where(
                        KnowledgeSource.chatbot_id == current_ks.chatbot_id,
                        CrawledPage.is_removed == False
                    )
                    chatbot_total_result = await db.execute(chatbot_total_stmt)
                    chatbot_total_pages = chatbot_total_result.scalar() or 0
                else:
                    chatbot_total_pages = ks_total_pages
                
                # DEBUG: Log quota calculations
                logger.info(f"Quota debug - quota_limit: {quota_limit}, ks_pages: {ks_total_pages}, chatbot_total: {chatbot_total_pages}, quota_reached: {quota_reached}, is_recrawl: {is_recrawl}")

                # Prepare quota warning message if limit was reached or we are at capacity
                quota_warning = None
                # For re-crawl: Always show warning if at or over quota limit (use chatbot total)
                # For new crawl: Only show if quota was actually hit during crawling
                if quota_limit and is_recrawl and chatbot_total_pages >= quota_limit:
                    # Re-crawl at capacity - always inform user
                    quota_warning = (
                        f"⚠️ Sync completed: Updated {pages_updated} pages. "
                        f"Note: Your {quota_limit} page limit is reached, so no new pages can be added. "
                        f"Upgrade your plan to add more pages."
                    )
                elif quota_limit and not is_recrawl and quota_reached:
                    # New crawl that hit quota
                    quota_warning = (
                        f"⚠️ Page limit reached: Crawled {pages_added} pages before hitting your "
                        f"{quota_limit} page quota. Upgrade your plan to crawl more pages."
                    )
                
                if quota_warning:
                    logger.warning(f"Setting quota warning: {quota_warning}")

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
                        pages_removed=pages_removed,
                        error_message=quota_warning  # Store quota warning in history
                    )
                )

                # Update knowledge source
                # If quota reached, we still process embeddings but show warning
                update_values = {
                    'pages_found': ks_total_pages,  # Use KS total for this field
                    # Keep status as CRAWLING - embeddings will set to COMPLETED
                    # But if quota reached and no pages added, mark as failed
                }
                
                # Add quota warning to error_message if quota was reached (user-facing message)
                # This will be shown in the frontend
                if quota_warning:
                    update_values['error_message'] = quota_warning
                else:
                    # Clear any previous error if crawl was successful
                    update_values['error_message'] = None
                
                await db.execute(
                    update(KnowledgeSource)
                    .where(KnowledgeSource.id == knowledge_source_id)
                    .values(**update_values)
                )
                
                # Update schedule last_crawl_at
                await db.execute(
                    update(CrawlSchedule)
                    .where(CrawlSchedule.knowledge_source_id == knowledge_source_id)
                    .values(last_crawl_at=datetime.now(timezone.utc))
                )
                
                await db.commit()
                
                # Enhanced logging with quota info
                log_message = (
                    f"Crawl completed for {base_url}. "
                    f"Checked: {len(crawled_urls)}, Added: {pages_added}, "
                    f"Updated: {pages_updated}, Removed: {pages_removed}, "
                    f"Skipped (duplicates): {pages_skipped}"
                )
                if quota_reached:
                    log_message += f" | ⚠️ QUOTA LIMIT REACHED at {quota_limit} pages"
                    
                logger.success(log_message)

                # Check if we actually crawled any pages (first crawl)
                if not is_recrawl and len(crawled_urls) == 0:
                    # No pages were found - this is a failure for initial crawl
                    error_msg = f"No accessible pages were found at this address. The site might be a 'Single Page App' (SPA) or require login/JavaScript, which our simple crawler cannot currently process."
                    logger.error(error_msg)
                    
                    # Log activity
                    from app.models.chatbot import ChatbotActivity
                    ks_stmt = select(KnowledgeSource).where(KnowledgeSource.id == knowledge_source_id)
                    ks_res = await db.execute(ks_stmt)
                    ks_obj = ks_res.scalar_one_or_none()
                    if ks_obj:
                        activity = ChatbotActivity(
                            chatbot_id=ks_obj.chatbot_id,
                            user_id=None,
                            activity_type="crawl_failed",
                            description=f"Crawl failed for {base_url}: No pages found"
                        )
                        db.add(activity)
                        await db.commit()

                    # Update status to FAILED so frontend can see the error before we delete it
                    await db.execute(
                        update(KnowledgeSource)
                        .where(KnowledgeSource.id == knowledge_source_id)
                        .values(
                            status=KnowledgeSourceStatus.FAILED,
                            error_message=error_msg
                        )
                    )
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
                                error_message=None
                            )
                        )
                        await db.commit()
                        logger.info(f"No content changes detected for KS {knowledge_source_id}, marked as COMPLETED")

                # Trigger background cleanup for old removed pages (daily policy)
                if background_tasks:
                    background_tasks.add_task(
                        CrawlerService.cleanup_old_removed_pages,
                        days=30
                    )

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
                    # Check if we should delete this source (initial crawl that failed with 0 content)
                    is_empty_initial = not is_recrawl
                    if not is_recrawl:
                        # Double check for ANY pages in database
                        page_count_stmt = select(func.count(CrawledPage.id)).where(CrawledPage.knowledge_source_id == knowledge_source_id)
                        pc_result = await db.execute(page_count_stmt)
                        if pc_result.scalar() > 0:
                            is_empty_initial = False

                    # Log failure activity first
                    from app.models.chatbot import ChatbotActivity
                    ks_stmt = select(KnowledgeSource).where(KnowledgeSource.id == knowledge_source_id)
                    ks_res = await db.execute(ks_stmt)
                    ks_obj = ks_res.scalar_one_or_none()
                    
                    if ks_obj:
                        activity = ChatbotActivity(
                            chatbot_id=ks_obj.chatbot_id,
                            user_id=None,
                            activity_type="crawl_failed",
                            description=f"Crawl failed for {base_url}: {error_msg[:150]}..."
                        )
                        db.add(activity)
                        await db.commit()
                    
                    # If not deleted (recrawl or has some pages), update status to FAILED
                    await db.execute(
                        update(KnowledgeSource)
                        .where(KnowledgeSource.id == knowledge_source_id)
                        .values(
                            status=KnowledgeSourceStatus.FAILED,
                            error_message=f"Crawl failed: {error_msg}"
                        )
                    )
                    await db.commit()
                    
                except Exception as update_error:
                    logger.error(f"Failed to handle crawl error: {update_error}")
                    await db.rollback()

    @staticmethod
    async def cleanup_old_removed_pages(days: int = 30):
        """Hard delete pages that have been marked as removed for more than X days."""
        from app.models.knowledge import Embedding
        session_factory = get_session_factory()
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

        async with session_factory() as db:
            try:
                # Find pages eligible for hard delete
                stmt = select(CrawledPage).where(
                    and_(
                        CrawledPage.is_removed == True,
                        CrawledPage.updated_at < cutoff
                    )
                )

                result = await db.execute(stmt)
                pages_to_delete = result.scalars().all()

                if not pages_to_delete:
                    return

                page_count = len(pages_to_delete)
                logger.info(f"Hard deleting {page_count} stale removed pages (older than {days} days)")

                for page in pages_to_delete:
                    # 1. Delete associated embeddings using URL-based approach 
                    # consistent with EmbeddingService.cleanup_removed_pages_embeddings
                    delete_emb_stmt = delete(Embedding).where(
                        and_(
                            Embedding.knowledge_source_id == page.knowledge_source_id,
                            Embedding.metadata_json['url'].astext == page.url
                        )
                    )
                    await db.execute(delete_emb_stmt)

                    # 2. Delete the page itself
                    await db.delete(page)

                await db.commit()
                logger.success(f"Successfully hard-deleted {page_count} stale removed pages and their embeddings")

            except Exception as e:
                logger.error(f"Error during removed pages cleanup: {e}")
                await db.rollback()


