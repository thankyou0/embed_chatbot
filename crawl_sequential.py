"""
Start crawls sequentially (one at a time) to avoid OOM.
Wait for each to complete or timeout before starting next.
"""
import requests
import time
import json

BASE_URL = "http://localhost:8000/api/v1"

# Sites to crawl - fewer, one at a time  
SITES = [
    ("Beardbrand", "https://www.beardbrand.com"),
    ("Death Wish Coffee", "https://www.deathwishcoffee.com"),
    ("Tentree", "https://www.tentree.com"),
]

def login():
    r = requests.post(f"{BASE_URL}/auth/login", json={"email": "max@gmail.com", "password": "12345678"}, timeout=15)
    r.raise_for_status()
    return r.json()["access_token"]

def create_chatbot(token, name):
    r = requests.post(f"{BASE_URL}/chatbots/", 
        headers={"Authorization": f"Bearer {token}"},
        json={"name": f"Crawl-{name}"},
        timeout=15)
    if r.status_code in (200, 201):
        return r.json()["id"]
    print(f"  Create bot failed: {r.status_code} {r.text[:200]}")
    return None

def start_crawl(token, chatbot_id, url):
    r = requests.post(f"{BASE_URL}/chatbots/{chatbot_id}/crawl",
        headers={"Authorization": f"Bearer {token}"},
        json={"base_url": url},
        timeout=30)
    if r.status_code in (200, 201, 202):
        return r.json()["id"]
    print(f"  Start crawl failed: {r.status_code} {r.text[:300]}")
    return None

def wait_for_crawl(token, source_id, max_wait=300):
    """Wait for crawl to complete, max_wait seconds"""
    start = time.time()
    last_pages = 0
    stall_count = 0
    
    while time.time() - start < max_wait:
        try:
            r = requests.get(f"{BASE_URL}/chatbots/knowledge-sources/{source_id}/status",
                headers={"Authorization": f"Bearer {token}"}, timeout=15)
            if r.status_code == 200:
                data = r.json()
                status = data.get("status", "unknown")
                pages = data.get("pages_found", 0)
                elapsed = int(time.time() - start)
                print(f"  [{elapsed}s] {status}: {pages} pages", end="\r")
                
                if status in ("completed", "failed"):
                    print(f"  [{elapsed}s] {status}: {pages} pages")
                    return status, pages
                
                if pages == last_pages:
                    stall_count += 1
                else:
                    stall_count = 0
                    last_pages = pages
                
                # If stalled for too long (pages not increasing for 2 min)
                if stall_count > 8 and pages > 0:
                    print(f"  [{elapsed}s] Stalled at {pages} pages, moving on")
                    return "stalled", pages
        except Exception as e:
            # May need to re-login
            try:
                token = login()
            except:
                pass
        
        time.sleep(15)
    
    print(f"  Timeout after {max_wait}s")
    return "timeout", last_pages

def main():
    token = login()
    print("Logged in\n")
    
    results = []
    
    for name, url in SITES:
        print(f"\n{'='*50}")
        print(f"Crawling: {name} ({url})")
        print(f"{'='*50}")
        
        bot_id = create_chatbot(token, name)
        if not bot_id:
            continue
        print(f"  Bot created: {bot_id}")
        
        source_id = start_crawl(token, bot_id, url)
        if not source_id:
            continue
        print(f"  Crawl started: {source_id}")
        
        # Wait for this single crawl
        status, pages = wait_for_crawl(token, source_id, max_wait=300)
        
        results.append({
            "name": name,
            "url": url,
            "chatbot_id": bot_id,
            "source_id": source_id,
            "final_status": status,
            "pages": pages,
        })
        
        print(f"  Result: {status} with {pages} pages")
        
        # Brief pause between crawls
        time.sleep(5)
    
    # Summary
    print(f"\n{'='*50}")
    print("CRAWL SUMMARY")
    print(f"{'='*50}")
    for r in results:
        print(f"  {r['name']}: {r['final_status']} ({r['pages']} pages) - {r['chatbot_id']}")
    
    with open("sequential_crawl_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    return results

if __name__ == "__main__":
    main()
