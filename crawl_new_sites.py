"""
Crawl new e-commerce sites and monitor progress.
Picks SSR-friendly sites (Shopify, WordPress) that work with httpx-based crawling.
"""
import requests
import time
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"

# SSR-friendly e-commerce sites (Shopify stores, WordPress, SSR sites)
SITES_TO_CRAWL = [
    ("Bombas", "https://bombas.com"),
    ("Allbirds", "https://www.allbirds.com"),
    ("Gymshark", "https://www.gymshark.com"),
    ("Pura Vida", "https://www.puravidabracelets.com"),
    ("Death Wish Coffee", "https://www.deathwishcoffee.com"),
    ("Beardbrand", "https://www.beardbrand.com"),
    ("MVMT Watches", "https://www.mvmt.com"),
    ("Chubbies", "https://www.chubbiesshorts.com"),
    ("Tentree", "https://www.tentree.com"),
    ("Ridge Wallet", "https://ridge.com"),
]

def login():
    r = requests.post(f"{BASE_URL}/auth/login", json={"email": "max@gmail.com", "password": "12345678"}, timeout=15)
    r.raise_for_status()
    return r.json()["access_token"]

def create_chatbot(token, name):
    r = requests.post(f"{BASE_URL}/chatbots/", 
        headers={"Authorization": f"Bearer {token}"},
        json={"name": f"Test-{name}"},
        timeout=15)
    if r.status_code == 201 or r.status_code == 200:
        data = r.json()
        return data["id"]
    else:
        print(f"  Failed to create bot {name}: {r.status_code} {r.text[:200]}")
        return None

def start_crawl(token, chatbot_id, url):
    r = requests.post(f"{BASE_URL}/chatbots/{chatbot_id}/crawl",
        headers={"Authorization": f"Bearer {token}"},
        json={"base_url": url},
        timeout=30)
    if r.status_code in (200, 201, 202):
        data = r.json()
        return data["id"]
    else:
        print(f"  Failed to crawl {url}: {r.status_code} {r.text[:300]}")
        return None

def check_status(token, source_id):
    r = requests.get(f"{BASE_URL}/chatbots/knowledge-sources/{source_id}/status",
        headers={"Authorization": f"Bearer {token}"},
        timeout=15)
    if r.status_code == 200:
        return r.json()
    return None

def main():
    print("=" * 60)
    print("CRAWL NEW E-COMMERCE SITES")
    print("=" * 60)
    
    token = login()
    print(f"Logged in successfully\n")
    
    crawl_jobs = []
    
    for name, url in SITES_TO_CRAWL:
        print(f"Creating bot for {name} ({url})...")
        bot_id = create_chatbot(token, name)
        if not bot_id:
            continue
        
        print(f"  Bot created: {bot_id}")
        source_id = start_crawl(token, bot_id, url)
        if source_id:
            print(f"  Crawl started: {source_id}")
            crawl_jobs.append({
                "name": name,
                "url": url,
                "chatbot_id": bot_id,
                "source_id": source_id,
                "status": "crawling",
                "pages": 0,
            })
        else:
            print(f"  Crawl failed to start")
        
        time.sleep(1)  # Small delay between starts
    
    print(f"\n{'='*60}")
    print(f"Started {len(crawl_jobs)} crawls. Monitoring progress...")
    print(f"{'='*60}\n")
    
    # Monitor crawls
    max_wait = 600  # 10 minutes max
    check_interval = 15  # Check every 15 seconds
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        # Re-login periodically to avoid token expiry
        if (time.time() - start_time) % 120 < check_interval:
            try:
                token = login()
            except:
                pass
        
        active = 0
        for job in crawl_jobs:
            if job["status"] in ("crawling",):
                try:
                    status = check_status(token, job["source_id"])
                    if status:
                        job["status"] = status.get("status", "unknown")
                        job["pages"] = status.get("pages_found", 0)
                except:
                    pass
                if job["status"] == "crawling":
                    active += 1
        
        elapsed = int(time.time() - start_time)
        print(f"\n[{elapsed}s] Status update ({active} active):")
        for job in crawl_jobs:
            emoji = "⏳" if job["status"] == "crawling" else ("✅" if job["status"] == "completed" else "❌")
            print(f"  {emoji} {job['name']}: {job['status']} ({job['pages']} pages)")
        
        if active == 0:
            print("\nAll crawls completed!")
            break
        
        time.sleep(check_interval)
    
    # Final summary
    print(f"\n{'='*60}")
    print("CRAWL RESULTS SUMMARY")
    print(f"{'='*60}")
    successful = []
    for job in crawl_jobs:
        status_str = f"{job['status']} - {job['pages']} pages"
        print(f"  {job['name']} ({job['url']}): {status_str}")
        if job["pages"] > 0:
            successful.append(job)
    
    print(f"\nSuccessfully crawled: {len(successful)}/{len(crawl_jobs)}")
    
    # Save results
    with open("crawl_results.json", "w") as f:
        json.dump(crawl_jobs, f, indent=2, default=str)
    print(f"Results saved to crawl_results.json")
    
    return successful

if __name__ == "__main__":
    successful = main()
