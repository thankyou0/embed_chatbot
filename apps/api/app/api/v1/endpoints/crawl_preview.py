from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
import asyncio
import hashlib
import urllib.robotparser
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Any, Optional
from datetime import datetime
import httpx
import trafilatura
from bs4 import BeautifulSoup
from app.services.product_extractor import extract_product_data
from app.core.error_sanitizer import sanitize_error_message

router = APIRouter()

class CrawlPreviewRequest(BaseModel):
    url: HttpUrl

class CrawlPreviewResponse(BaseModel):
    url: str
    title: str | None
    content: str
    content_length: int
    content_hash: str
    found_links: List[str]
    total_links: int
    chunks: List[Dict[str, Any]]
    chunk_stats: Dict[str, int]
    crawl_timestamp: str
    is_product: bool = False
    product_data: Optional[Dict[str, Any]] = None

def chunk_text(text: str, max_tokens: int = 512, overlap: int = 50, min_tokens: int = 100) -> List[str]:
    """Token-aware chunking strategy - same as EmbeddingService.chunk_text()"""
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
            if current_token_count >= min_tokens:
                chunks.append(" ".join(current_chunk))
                overlap_tokens = current_chunk[-overlap:] if overlap < len(current_chunk) else current_chunk
                current_chunk = overlap_tokens + para_tokens
                current_token_count = len(current_chunk)
            else:
                current_chunk.extend(para_tokens)
                current_token_count += para_token_count

    if current_chunk and (len(current_chunk) >= min_tokens or not chunks):
        chunks.append(" ".join(current_chunk))
        
    return chunks

async def crawl_single_page(url: str) -> dict:
    """Crawl a single page and extract content"""
    parsed = urlparse(url)
    if not parsed.scheme:
        url = "https://" + url
        parsed = urlparse(url)
    
    domain = parsed.netloc
    
    # Check robots.txt
    robot_parser = urllib.robotparser.RobotFileParser()
    robot_parser.set_url(urljoin(url, "/robots.txt"))
    
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, robot_parser.read)
        can_fetch = robot_parser.can_fetch("*", url)
    except Exception:
        can_fetch = True
    
    if not can_fetch:
        raise HTTPException(status_code=403, detail=f"Crawling disallowed by robots.txt for {url}")
    
    headers = {
        "User-Agent": "EcomChatbotCrawler/1.0 (Knowledge Base Bot)"
    }
    
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True, headers=headers) as client:
        try:
            response = await client.get(url)
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=f"HTTP {response.status_code}")
            
            content_type = response.headers.get("content-type", "").lower()
            if "text/html" not in content_type:
                raise HTTPException(status_code=400, detail=f"Not an HTML page (Content-Type: {content_type})")

            html_content = response.text
            
            # Extract content with trafilatura
            extracted = trafilatura.extract(html_content, favor_precision=True)
            metadata = trafilatura.extract_metadata(html_content)
            title = metadata.title if metadata and metadata.title else None
            
            if not extracted:
                raise HTTPException(status_code=400, detail="No extractable content found on this page")
            
            # Extract contact information from links (phone, email)
            # These are often in <a> tags and get stripped by trafilatura
            soup = BeautifulSoup(html_content, 'html.parser')
            contact_info = []
            
            # Extract emails from mailto: links
            for a in soup.find_all('a', href=True):
                href = a.get('href', '')
                if href.startswith('mailto:'):
                    email = href.replace('mailto:', '').split('?')[0].strip()
                    if email and email not in extracted:
                        contact_info.append(f"Email: {email}")
                elif href.startswith('tel:'):
                    phone = href.replace('tel:', '').strip()
                    # Clean up phone number formatting
                    phone = phone.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
                    if phone and phone not in extracted:
                        contact_info.append(f"Phone: {phone}")
            
            # Append contact info to extracted content if found
            if contact_info:
                extracted += "\n\nContact Information:\n" + "\n".join(set(contact_info))
            
            # Extract product data (returns None for non-product pages)
            product_data = extract_product_data(html_content, url)
            
            # Extract links
            soup = BeautifulSoup(html_content, 'html.parser')
            links = []
            for a in soup.find_all('a', href=True):
                link = urljoin(url, a['href'])
                link = link.split('#')[0].rstrip('/')
                if link != url:
                    links.append(link)
            
            unique_links = list(dict.fromkeys(links))
            
            return {
                'url': url,
                'title': title,
                'content': extracted,
                'content_length': len(extracted),
                'content_hash': hashlib.sha256(extracted.encode()).hexdigest(),
                'found_links': unique_links[:20],
                'total_links': len(unique_links),
                'crawl_timestamp': datetime.now().isoformat(),
                'is_product': product_data is not None,
                'product_data': product_data
            }
            
        except HTTPException:
            raise
        except Exception as e:
            detail = sanitize_error_message(
                str(e),
                fallback="Unable to preview this page. Please try again."
            )
            raise HTTPException(status_code=500, detail=detail)

@router.post("/preview", response_model=CrawlPreviewResponse)
async def preview_crawl(request: CrawlPreviewRequest):
    """
    Preview what content and chunks would be extracted from a URL.
    Shows the same data that would be stored in the database.
    Also extracts product data if the page is detected as a product page.
    """
    try:
        # Crawl the page
        page_data = await crawl_single_page(str(request.url))
        
        # Chunk the content
        chunks = chunk_text(page_data['content'], max_tokens=512, overlap=50, min_tokens=100)
        
        # Prepare chunk data with metadata
        chunk_data = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = {
                "url": page_data['url'],
                "title": page_data['title'],
                "chunk_index": i,
                "total_chunks": len(chunks),
                "is_product": page_data.get('is_product', False)
            }
            
            # Add product info to chunk metadata if it's a product page
            if page_data.get('is_product') and page_data.get('product_data'):
                product = page_data['product_data']
                chunk_metadata["product"] = {
                    "name": product.get("name"),
                    "price": product.get("price"),
                    "currency": product.get("currency"),
                    "images": product.get("images", [])[:3],
                    "availability": product.get("availability"),
                    "rating": product.get("rating"),
                    "review_count": product.get("review_count"),
                    "brand": product.get("brand"),
                }
            
            chunk_data.append({
                "index": i + 1,
                "content": chunk,
                "word_count": len(chunk.split()),
                "char_count": len(chunk),
                "metadata": chunk_metadata
            })
        
        # Calculate stats
        total_words = sum(len(chunk.split()) for chunk in chunks)
        chunk_stats = {
            "total_chunks": len(chunks),
            "total_words": total_words,
            "avg_words_per_chunk": total_words // len(chunks) if chunks else 0,
            "min_words": min(len(chunk.split()) for chunk in chunks) if chunks else 0,
            "max_words": max(len(chunk.split()) for chunk in chunks) if chunks else 0
        }
        
        return CrawlPreviewResponse(
            url=page_data['url'],
            title=page_data['title'],
            content=page_data['content'],
            content_length=page_data['content_length'],
            content_hash=page_data['content_hash'],
            found_links=page_data['found_links'],
            total_links=page_data['total_links'],
            chunks=chunk_data,
            chunk_stats=chunk_stats,
            crawl_timestamp=page_data['crawl_timestamp'],
            is_product=page_data.get('is_product', False),
            product_data=page_data.get('product_data')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        detail = sanitize_error_message(
            str(e),
            fallback="Unable to preview this page. Please try again."
        )
        raise HTTPException(status_code=500, detail=detail)
