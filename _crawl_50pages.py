"""
Crawl remaining sites with 50-page limit.
Starts crawl, monitors progress, stops at 50 pages.
Crawls in batches of 3-4 sites simultaneously.
"""
import requests
import time
import json
import sys

API = "http://localhost:8000/api/v1"
MAX_PAGES = 50
POLL_INTERVAL = 8  # seconds

# Login
s = requests.Session()
r = s.post(f"{API}/auth/login", json={"email": "max@gmail.com", "password": "12345678"})
token = r.json()["access_token"]
s.headers.update({"Authorization": f"Bearer {token}"})
print("Logged in OK")

# Sites to crawl (uncrawled ones from crawl_test_bots.json)
SITES_TO_CRAWL = [
    {"bot_id": "9fa35176-cf46-42f1-ad62-cd077c7a4788", "name": "CrawlTest-themancompany", "url": "https://www.themancompany.com"},
    {"bot_id": "afda9afb-bcc1-4cfa-b8fe-da5f5fc38f73", "name": "CrawlTest-mokobara", "url": "https://www.mokobara.com"},
    {"bot_id": "cc90afbd-5839-45d5-a4aa-68f681f60e61", "name": "CrawlTest-rawpressery", "url": "https://www.rawpressery.com"},
    {"bot_id": "33231221-b581-4058-9b38-2797b78d5947", "name": "CrawlTest-slurrpfarm", "url": "https://www.slurrpfarm.com"},
    {"bot_id": "babcd869-2ab9-4fc0-85df-3b52d4654142", "name": "CrawlTest-vahdam", "url": "https://www.vahdam.com"},
    {"bot_id": "a839779a-0820-4694-b7e5-916ffab8ed7c", "name": "CrawlTest-plumgoodness", "url": "https://www.plumgoodness.com"},
    {"bot_id": "8e652492-ecbc-4803-9cfe-6dc08e630634", "name": "CrawlTest-bombayshirtcompany", "url": "https://www.bombayshirtcompany.com"},
]

# Also retry failed ones
RETRY_FAILED = [
    {"bot_id": "3374cca5-134f-4e4f-b29d-57ced76c9cf5", "name": "CrawlTest-etsy", "url": "https://www.etsy.com"},
    {"bot_id": "7a40b6e3-b067-4acf-853f-dce70a776ae6", "name": "CrawlTest-wayfair", "url": "https://www.wayfair.com"},
]

ALL_SITES = SITES_TO_CRAWL + RETRY_FAILED

def start_crawl(bot_id, url):
    """Start crawling a site"""
    r = s.post(f"{API}/chatbots/{bot_id}/crawl", json={"base_url": url})
    if r.ok:
        data = r.json()
        return data.get("id")
    else:
        print(f"  FAIL to start: {r.status_code} {r.text[:200]}")
        return None

def get_crawl_status(ks_id):
    """Get crawl status"""
    r = s.get(f"{API}/chatbots/knowledge-sources/{ks_id}/status")
    if r.ok:
        return r.json()
    return None

def stop_crawl(ks_id):
    """Stop a crawl"""
    r = s.post(f"{API}/chatbots/knowledge-sources/{ks_id}/stop")
    return r.ok

def get_page_count_from_db(ks_id):
    """Get actual page count from DB since API status sometimes shows 0"""
    import subprocess
    result = subprocess.run(
        ['docker', 'exec', 'chatbot_postgres', 'psql', '-U', 'postgres', '-d', 'embed_chatbot', '-t', '-c',
         f"SELECT COUNT(*) FROM crawled_pages WHERE knowledge_source_id='{ks_id}';"],
        capture_output=True, text=True
    )
    try:
        return int(result.stdout.strip())
    except:
        return 0

def crawl_batch(batch):
    """Crawl a batch of sites, stopping each at MAX_PAGES"""
    active = {}  # ks_id -> site info
    results = []
    
    # Start all crawls in the batch
    for site in batch:
        print(f"\n[START] {site['name']} -> {site['url']}")
        
        # Check if already has a knowledge source
        ks_r = s.get(f"{API}/chatbots/{site['bot_id']}/knowledge-sources")
        existing_ks = ks_r.json() if ks_r.ok else []
        
        if existing_ks:
            ks = existing_ks[0]
            if ks.get('status') == 'completed':
                pages = get_page_count_from_db(ks['id'])
                print(f"  Already completed with {pages} pages, skipping")
                results.append({**site, "status": "already_completed", "pages": pages, "ks_id": ks['id']})
                continue
            elif ks.get('status') == 'failed':
                # Delete failed KS and retry
                print(f"  Previous crawl failed, deleting and retrying...")
                # Delete the failed KS
                del_r = s.delete(f"{API}/chatbots/knowledge-sources/{ks['id']}")
                if not del_r.ok:
                    print(f"  Could not delete failed KS: {del_r.status_code}")
                    results.append({**site, "status": "failed_delete", "pages": 0})
                    continue
                time.sleep(1)
        
        ks_id = start_crawl(site['bot_id'], site['url'])
        if ks_id:
            active[ks_id] = site
            print(f"  Started, KS ID: {ks_id}")
        else:
            results.append({**site, "status": "start_failed", "pages": 0})
    
    if not active:
        return results
    
    # Monitor and stop at MAX_PAGES
    print(f"\n--- Monitoring {len(active)} active crawls (stop at {MAX_PAGES} pages) ---")
    max_wait = 300  # 5 minutes max per batch
    start_time = time.time()
    
    while active and (time.time() - start_time) < max_wait:
        time.sleep(POLL_INTERVAL)
        
        finished = []
        for ks_id, site in active.items():
            # Get page count from DB (more reliable)
            db_pages = get_page_count_from_db(ks_id)
            
            # Also check API status
            status = get_crawl_status(ks_id)
            api_status = status.get("status", "unknown") if status else "error"
            api_pages = status.get("pages_found", 0) if status else 0
            
            pages = max(db_pages, api_pages)
            
            print(f"  {site['name']:30s} | status={api_status:10s} | db_pages={db_pages:4d} | api_pages={api_pages:4d}")
            
            if pages >= MAX_PAGES and api_status == "crawling":
                print(f"  >>> STOPPING {site['name']} at {pages} pages")
                stop_crawl(ks_id)
                # Wait a moment for stop to process
                time.sleep(3)
                final_pages = get_page_count_from_db(ks_id)
                results.append({**site, "status": "stopped_at_limit", "pages": final_pages, "ks_id": ks_id})
                finished.append(ks_id)
            elif api_status in ("completed", "failed", "stopped"):
                final_pages = get_page_count_from_db(ks_id)
                results.append({**site, "status": api_status, "pages": final_pages, "ks_id": ks_id})
                finished.append(ks_id)
        
        for ks_id in finished:
            del active[ks_id]
        
        if active:
            elapsed = int(time.time() - start_time)
            print(f"  --- {len(active)} still active, elapsed={elapsed}s ---")
    
    # Timeout - stop remaining
    for ks_id, site in active.items():
        print(f"  TIMEOUT: Stopping {site['name']}")
        stop_crawl(ks_id)
        time.sleep(2)
        final_pages = get_page_count_from_db(ks_id)
        results.append({**site, "status": "timeout_stopped", "pages": final_pages, "ks_id": ks_id})
    
    return results

# Run in batches of 3-4
all_results = []
batch_size = 3

for i in range(0, len(ALL_SITES), batch_size):
    batch = ALL_SITES[i:i+batch_size]
    batch_num = i // batch_size
    print(f"\n{'='*60}")
    print(f"BATCH {batch_num}: {', '.join(s['name'] for s in batch)}")
    print(f"{'='*60}")
    
    batch_results = crawl_batch(batch)
    all_results.extend(batch_results)
    
    # Short pause between batches
    if i + batch_size < len(ALL_SITES):
        print(f"\nWaiting 5s before next batch...")
        time.sleep(5)

# Summary
print(f"\n{'='*60}")
print("CRAWL SUMMARY")
print(f"{'='*60}")
total_new_pages = 0
for r in all_results:
    status_icon = "OK" if r["pages"] > 0 else "FAIL"
    print(f"  [{status_icon:4s}] {r['name']:30s} | pages={r['pages']:4d} | status={r['status']}")
    total_new_pages += r["pages"]

print(f"\nTotal new pages crawled: {total_new_pages}")

# Save results
with open("_crawl_results.json", "w") as f:
    json.dump(all_results, f, indent=2, default=str)
print("Results saved to _crawl_results.json")
