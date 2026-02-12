#!/usr/bin/env python3
"""
Crawl Preview Tool

This script shows what content and chunks the crawler would extract from a specific URL.
It uses the same logic as the main crawler but doesn't save to database.

Usage:
    python crawl_preview.py

Then enter the URL when prompted.
"""

import asyncio
import hashlib
import urllib.robotparser
from urllib.parse import urljoin, urlparse
from typing import List
from datetime import datetime
import httpx
import trafilatura
from bs4 import BeautifulSoup


def chunk_text(text: str, max_tokens: int = 512, overlap: int = 50, min_tokens: int = 100) -> List[str]:
    """
    Token-aware chunking strategy - same as EmbeddingService.chunk_text()
    Splits by paragraphs/headings first, then ensures max_tokens limit.
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


async def crawl_single_page(url: str) -> dict:
    """Crawl a single page and extract content, similar to WebsiteCrawler.crawl()"""
    
    # Normalize URL
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
    except Exception as e:
        print(f"⚠️  Could not read robots.txt for {domain}: {e}")
        can_fetch = True
    
    if not can_fetch:
        raise Exception(f"❌ Crawling disallowed by robots.txt for {url}")
    
    headers = {
        "User-Agent": "EcomChatbotCrawler/1.0 (Knowledge Base Bot)"
    }
    
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True, headers=headers) as client:
        print(f"🌐 Fetching: {url}")
        
        try:
            response = await client.get(url)
            if response.status_code != 200:
                raise Exception(f"❌ HTTP {response.status_code}: {response.reason_phrase}")
            
            # Check content type - only process HTML
            content_type = response.headers.get("content-type", "").lower()
            if "text/html" not in content_type:
                raise Exception(f"❌ Not an HTML page (Content-Type: {content_type})")

            html_content = response.text
            
            # Extract content with trafilatura
            print("🔍 Extracting main content...")
            extracted = trafilatura.extract(html_content, favor_precision=True)
            
            # Metadata extraction
            metadata = trafilatura.extract_metadata(html_content)
            title = metadata.title if metadata and metadata.title else None
            
            if not extracted:
                raise Exception("❌ No extractable content found on this page")
            
            # Extract links for analysis
            soup = BeautifulSoup(html_content, 'html.parser')
            links = []
            for a in soup.find_all('a', href=True):
                link = urljoin(url, a['href'])
                link = link.split('#')[0].rstrip('/')  # Clean fragments and normalize
                if link != url:  # Don't include self-links
                    links.append(link)
            
            # Remove duplicates while preserving order
            unique_links = list(dict.fromkeys(links))
            
            return {
                'url': url,
                'title': title,
                'content': extracted,
                'content_length': len(extracted),
                'content_hash': hashlib.sha256(extracted.encode()).hexdigest(),
                'found_links': unique_links[:20],  # Show first 20 links
                'total_links': len(unique_links),
                'crawl_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"❌ Error crawling {url}: {str(e)}")


def print_separator(title: str):
    """Print a nice separator"""
    print("\n" + "="*80)
    print(f" {title}")
    print("="*80)


def print_chunks(chunks: List[str]):
    """Print chunks with nice formatting"""
    if not chunks:
        print("❌ No chunks generated")
        return
    
    print(f"📦 Generated {len(chunks)} chunks:")
    print()
    
    for i, chunk in enumerate(chunks, 1):
        words = chunk.split()
        word_count = len(words)
        
        print(f"┌─ Chunk {i}/{len(chunks)} ({word_count} words)")
        print("│")
        
        # Print first few lines of chunk
        lines = chunk.split('\n')
        for j, line in enumerate(lines[:5]):  # Show first 5 lines
            if line.strip():
                print(f"│ {line[:75]}{'...' if len(line) > 75 else ''}")
        
        if len(lines) > 5:
            print(f"│ ... ({len(lines) - 5} more lines)")
        
        print("└─")
        print()


async def main():
    print("🔍 Crawl Preview Tool")
    print("Shows what content and chunks would be extracted from a URL")
    print()
    
    while True:
        try:
            url = input("Enter URL to crawl (or 'quit' to exit): ").strip()
            
            if url.lower() in ['quit', 'q', 'exit']:
                print("👋 Goodbye!")
                break
                
            if not url:
                print("❌ Please enter a valid URL")
                continue
            
            print()
            
            # Crawl the page
            page_data = await crawl_single_page(url)
            
            print_separator("PAGE INFO")
            print(f"📄 Title: {page_data['title'] or 'No title'}")
            print(f"🌐 URL: {page_data['url']}")
            print(f"📏 Content Length: {page_data['content_length']:,} characters")
            print(f"🔑 Content Hash: {page_data['content_hash'][:16]}...")
            print(f"🔗 Found Links: {page_data['total_links']} (showing first 20)")
            print(f"⏰ Crawled At: {page_data['crawl_timestamp']}")
            
            # Show some links
            if page_data['found_links']:
                print(f"\n📎 Sample Links Found:")
                for link in page_data['found_links']:
                    print(f"   • {link}")
            
            print_separator("EXTRACTED CONTENT")
            content = page_data['content']
            
            # Show first 1000 characters
            print("📝 Main Content Preview:")
            print()
            lines = content.split('\n')
            char_count = 0
            for line in lines:
                if char_count + len(line) > 1000:
                    print("... (content truncated)")
                    break
                print(line)
                char_count += len(line)
            
            print_separator("CONTENT CHUNKS")
            
            # Chunk the content
            print("🔄 Chunking content...")
            chunks = chunk_text(content, max_tokens=512, overlap=50, min_tokens=100)
            
            print_chunks(chunks)
            
            # Summary
            total_words = sum(len(chunk.split()) for chunk in chunks)
            print(f"📊 Summary: {len(chunks)} chunks, {total_words:,} total words")
            print(f"   Average: {total_words//len(chunks) if chunks else 0} words per chunk")
            
            print("\n" + "-"*80)
            print()
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")