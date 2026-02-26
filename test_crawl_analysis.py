#!/usr/bin/env python3
"""
Comprehensive Crawl Testing & Analysis Script
Tests crawling algorithm with diverse e-commerce sites, then queries each bot.
"""

import requests
import json
import time
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"
EMAIL = "max@gmail.com"
PASSWORD = "12345678"
MAX_PAGES = 50
POLL_INTERVAL = 10  # seconds between status checks

# --- Diverse e-commerce sites to test ---
# Categories: Large/Famous, Medium/Regional, Small/Local, Niche
TEST_SITES = [
    # Large / Famous e-commerce
    {"url": "https://www.etsy.com", "category": "large", "desc": "Handmade & vintage marketplace"},
    {"url": "https://www.zappos.com", "category": "large", "desc": "Shoes & clothing"},
    {"url": "https://www.wayfair.com", "category": "large", "desc": "Furniture & home goods"},
    
    # Medium / Regional
    {"url": "https://www.nykaa.com", "category": "medium", "desc": "Indian beauty & cosmetics"},
    {"url": "https://www.bewakoof.com", "category": "medium", "desc": "Indian casual fashion"},
    {"url": "https://www.chumbak.com", "category": "medium", "desc": "Indian quirky lifestyle brand"},
    
    # Small / Niche / Local
    {"url": "https://www.nicobar.com", "category": "small", "desc": "Indian clothing & lifestyle"},
    {"url": "https://www.bombayshirtcompany.com", "category": "small", "desc": "Custom shirts India"},
    {"url": "https://www.themancompany.com", "category": "small", "desc": "Men's grooming India"},
    {"url": "https://www.mokobara.com", "category": "small", "desc": "Travel bags & luggage"},
    
    # Very small / Static / Local shops
    {"url": "https://www.rawpressery.com", "category": "very-small", "desc": "Cold pressed juices"},
    {"url": "https://www.slurrpfarm.com", "category": "very-small", "desc": "Organic kids food"},
    {"url": "https://www.vahdam.com", "category": "very-small", "desc": "Indian teas"},
    {"url": "https://www.plumgoodness.com", "category": "very-small", "desc": "Vegan beauty products"},
]


def login():
    """Login and return access token."""
    r = requests.post(f"{BASE_URL}/auth/login",
                      json={"email": EMAIL, "password": PASSWORD}, timeout=15)
    r.raise_for_status()
    return r.json()["access_token"]


def list_bots(token):
    """List existing bots."""
    r = requests.get(f"{BASE_URL}/chatbots/",
                     headers={"Authorization": f"Bearer {token}"}, timeout=15)
    r.raise_for_status()
    return r.json()


def create_chatbot(token, name):
    """Create a new chatbot."""
    r = requests.post(f"{BASE_URL}/chatbots/",
                      headers={"Authorization": f"Bearer {token}"},
                      json={"name": name}, timeout=15)
    r.raise_for_status()
    return r.json()


def start_crawl(token, chatbot_id, url):
    """Start crawling a URL for a chatbot."""
    r = requests.post(f"{BASE_URL}/chatbots/{chatbot_id}/crawl",
                      headers={"Authorization": f"Bearer {token}"},
                      json={"base_url": url}, timeout=30)
    r.raise_for_status()
    return r.json()


def check_status(token, source_id):
    """Check crawl status."""
    r = requests.get(f"{BASE_URL}/chatbots/knowledge-sources/{source_id}/status",
                     headers={"Authorization": f"Bearer {token}"}, timeout=15)
    r.raise_for_status()
    return r.json()


def stop_crawl(token, source_id):
    """Stop a crawl."""
    r = requests.post(f"{BASE_URL}/chatbots/knowledge-sources/{source_id}/stop",
                      headers={"Authorization": f"Bearer {token}"}, timeout=30)
    r.raise_for_status()
    return r.json()


def get_knowledge_sources(token, chatbot_id):
    """Get knowledge sources for a chatbot."""
    r = requests.get(f"{BASE_URL}/chatbots/{chatbot_id}/knowledge-sources",
                     headers={"Authorization": f"Bearer {token}"}, timeout=15)
    r.raise_for_status()
    return r.json()


def send_chat(chatbot_id, message, session_id=None):
    """Send a chat message and collect SSE response."""
    data = {"message": message}
    if session_id:
        data["session_id"] = session_id

    try:
        resp = requests.post(f"{BASE_URL}/chat/{chatbot_id}/message/stream",
                             data=data, stream=True, timeout=90)
        resp.raise_for_status()
    except Exception as e:
        return {"content": f"ERROR: {e}", "sources": [], "suggestions": [], "products": [], "session_id": session_id, "error": str(e)}

    result = {"content": "", "sources": [], "suggestions": [], "products": [],
              "session_id": session_id, "tags": [], "error": None}

    for line in resp.iter_lines(decode_unicode=True):
        if line and line.startswith("data: "):
            try:
                event = json.loads(line[6:])
                if event.get("type") == "session":
                    result["session_id"] = event.get("session_id")
                elif event.get("type") == "content":
                    result["content"] += event.get("content", "")
                elif event.get("type") == "done":
                    result["sources"] = event.get("sources", [])
                    result["suggestions"] = event.get("suggestions", [])
                    result["products"] = event.get("products", [])
                    result["tags"] = event.get("tags", [])
                elif event.get("type") == "error":
                    result["error"] = event.get("error", "Unknown error")
            except json.JSONDecodeError:
                pass

    return result


def refresh_token():
    """Re-login to get a fresh token."""
    return login()


# ============================================
# MAIN EXECUTION
# ============================================
if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "list"
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Logging in...")
    token = login()
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Login successful!")

    if mode == "list":
        data = list_bots(token)
        print(f"\nTotal bots: {data['total']}")
        for b in data["chatbots"]:
            print(f"  ID: {b['id']} | Name: {b['name']} | Status: {b['status']}")
    
    elif mode == "create":
        # Create bots for all test sites
        results = []
        for site in TEST_SITES:
            name = f"CrawlTest-{site['url'].split('//')[1].split('.')[1] if '.' in site['url'].split('//')[1] else site['url'].split('//')[1].split('.')[0]}"
            print(f"\nCreating bot: {name} for {site['url']}...")
            try:
                bot = create_chatbot(token, name)
                bot_id = bot["id"]
                print(f"  Created bot ID: {bot_id}")
                results.append({"site": site, "bot_id": bot_id, "bot_name": name})
            except Exception as e:
                print(f"  ERROR creating bot: {e}")
                results.append({"site": site, "bot_id": None, "error": str(e)})
        
        with open("crawl_test_bots.json", "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nCreated {len([r for r in results if r.get('bot_id')])} bots. Saved to crawl_test_bots.json")
    
    elif mode == "crawl_batch":
        # Crawl a batch of sites (pass batch number as argv[2])
        batch_num = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        batch_size = 4
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, len(TEST_SITES))
        
        if start_idx >= len(TEST_SITES):
            print("No more sites to crawl!")
            sys.exit(0)
        
        # Load bot mappings
        with open("crawl_test_bots.json") as f:
            bot_mappings = json.load(f)
        
        batch_sites = bot_mappings[start_idx:end_idx]
        print(f"\n=== BATCH {batch_num} ({start_idx}-{end_idx-1}) ===")
        
        # Start crawls
        active_crawls = []
        for item in batch_sites:
            if not item.get("bot_id"):
                print(f"  Skipping {item['site']['url']} - no bot")
                continue
            
            url = item["site"]["url"]
            bot_id = item["bot_id"]
            print(f"\n  Starting crawl: {url} → Bot {bot_id}")
            try:
                result = start_crawl(token, bot_id, url)
                source_id = result.get("id")
                print(f"    Source ID: {source_id}")
                active_crawls.append({
                    "bot_id": bot_id,
                    "source_id": source_id,
                    "url": url,
                    "site": item["site"],
                    "start_time": datetime.now().isoformat()
                })
            except Exception as e:
                print(f"    ERROR starting crawl: {e}")
                try:
                    err_detail = e.response.text if hasattr(e, 'response') and e.response else str(e)
                except:
                    err_detail = str(e)
                active_crawls.append({
                    "bot_id": bot_id,
                    "source_id": None,
                    "url": url,
                    "site": item["site"],
                    "error": err_detail,
                    "start_time": datetime.now().isoformat()
                })
        
        # Monitor crawls until all reach 50 pages or complete/fail
        print(f"\n  Monitoring {len([c for c in active_crawls if c.get('source_id')])} active crawls...")
        completed = set()
        token_refresh_time = time.time()
        
        while len(completed) < len(active_crawls):
            # Refresh token every 10 minutes
            if time.time() - token_refresh_time > 600:
                token = refresh_token()
                token_refresh_time = time.time()
            
            time.sleep(POLL_INTERVAL)
            
            for crawl in active_crawls:
                if crawl.get("source_id") is None or crawl["source_id"] in completed:
                    if crawl["source_id"] is None and id(crawl) not in [id(c) for c in active_crawls if c.get("source_id")]:
                        completed.add(id(crawl))
                    continue
                
                try:
                    status = check_status(token, crawl["source_id"])
                    pages = status.get("pages_found", status.get("pages_crawled", 0))
                    state = status.get("status", "unknown")
                    crawl["last_status"] = status
                    
                    print(f"    [{datetime.now().strftime('%H:%M:%S')}] {crawl['url']}: {state} - {pages} pages")
                    
                    if pages >= MAX_PAGES and state == "crawling":
                        print(f"    >>> Stopping {crawl['url']} at {pages} pages")
                        try:
                            stop_result = stop_crawl(token, crawl["source_id"])
                            crawl["stopped_at"] = pages
                            crawl["stop_result"] = "stopped"
                        except Exception as e:
                            crawl["stop_result"] = f"stop_error: {e}"
                        completed.add(crawl["source_id"])
                    
                    elif state in ("completed", "failed", "stopped", "embedding_complete"):
                        crawl["final_status"] = state
                        crawl["final_pages"] = pages
                        completed.add(crawl["source_id"])
                        print(f"    >>> {crawl['url']} finished: {state} ({pages} pages)")
                    
                except Exception as e:
                    print(f"    ERROR checking {crawl['url']}: {e}")
        
        # Save batch results
        batch_file = f"crawl_batch_{batch_num}_results.json"
        with open(batch_file, "w") as f:
            json.dump(active_crawls, f, indent=2, default=str)
        print(f"\n  Batch {batch_num} complete! Saved to {batch_file}")
    
    elif mode == "test_queries":
        # Test queries on all crawled bots
        # Load bot mappings
        with open("crawl_test_bots.json") as f:
            bot_mappings = json.load(f)
        
        # Generic test queries for all bots
        GENERIC_QUERIES = [
            # Product queries
            {"query": "What products do you have?", "type": "product-general", "lang": "en"},
            {"query": "Show me your best sellers", "type": "product-specific", "lang": "en"},
            {"query": "What is the price range of your products?", "type": "product-price", "lang": "en"},
            
            # Non-product queries
            {"query": "What are your shipping options?", "type": "non-product", "lang": "en"},
            {"query": "Do you have a return policy?", "type": "non-product", "lang": "en"},
            {"query": "How can I contact customer support?", "type": "non-product", "lang": "en"},
            
            # Irrelevant queries
            {"query": "What is the weather today?", "type": "irrelevant", "lang": "en"},
            {"query": "Tell me a joke", "type": "irrelevant", "lang": "en"},
            
            # Missing info queries
            {"query": "What material is this product made of?", "type": "missing-info", "lang": "en"},
            {"query": "Is this product available in size XXL?", "type": "missing-info", "lang": "en"},
            
            # Complex / context queries
            {"query": "I'm looking for a gift under $50, what do you recommend?", "type": "complex", "lang": "en"},
            
            # Greeting
            {"query": "Hi there!", "type": "greeting", "lang": "en"},
        ]
        
        all_results = []
        
        for item in bot_mappings:
            if not item.get("bot_id"):
                continue
            
            bot_id = item["bot_id"]
            bot_name = item.get("bot_name", "Unknown")
            site_url = item["site"]["url"]
            
            print(f"\n{'='*60}")
            print(f"Testing: {bot_name} ({site_url})")
            print(f"{'='*60}")
            
            session_id = None
            bot_results = {"bot_id": bot_id, "bot_name": bot_name, "site": item["site"], "queries": []}
            
            for q in GENERIC_QUERIES:
                print(f"\n  [{q['type']}] {q['query']}")
                result = send_chat(bot_id, q["query"], session_id)
                session_id = result.get("session_id", session_id)
                
                content = result["content"][:200] + "..." if len(result["content"]) > 200 else result["content"]
                print(f"    Response: {content}")
                print(f"    Products: {len(result.get('products', []))}")
                print(f"    Suggestions: {result.get('suggestions', [])}")
                print(f"    Tags: {result.get('tags', [])}")
                
                bot_results["queries"].append({
                    "query": q["query"],
                    "type": q["type"],
                    "lang": q["lang"],
                    "response": result["content"],
                    "products_count": len(result.get("products", [])),
                    "products": result.get("products", [])[:3],  # first 3
                    "suggestions": result.get("suggestions", []),
                    "sources_count": len(result.get("sources", [])),
                    "tags": result.get("tags", []),
                    "error": result.get("error"),
                    "session_id": session_id
                })
                
                time.sleep(2)  # Rate limit friendly
            
            all_results.append(bot_results)
            
            # Refresh token periodically
            token = refresh_token()
        
        with open("crawl_test_query_results.json", "w") as f:
            json.dump(all_results, f, indent=2, default=str)
        print(f"\n\nAll query results saved to crawl_test_query_results.json")
    
    elif mode == "report":
        # Generate analysis report from query results
        with open("crawl_test_query_results.json") as f:
            results = json.load(f)
        
        # Load crawl batch results
        crawl_data = {}
        for i in range(4):
            try:
                with open(f"crawl_batch_{i}_results.json") as f:
                    batch = json.load(f)
                    for item in batch:
                        crawl_data[item.get("bot_id", "")] = item
            except FileNotFoundError:
                pass
        
        report = []
        report.append("# Comprehensive Crawl & Chat Testing Analysis Report")
        report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"\nTotal sites tested: {len(results)}")
        
        # Summary table
        report.append("\n## 1. Crawl Summary\n")
        report.append("| Site | Category | Pages Crawled | Status | Errors |")
        report.append("|------|----------|---------------|--------|--------|")
        
        for bot_result in results:
            bot_id = bot_result["bot_id"]
            cd = crawl_data.get(bot_id, {})
            ls = cd.get("last_status", {})
            pages = ls.get("pages_found", ls.get("pages_crawled", "N/A"))
            status = cd.get("final_status", cd.get("stop_result", "N/A"))
            error = cd.get("error", "None")
            report.append(f"| {bot_result['site']['url']} | {bot_result['site']['category']} | {pages} | {status} | {error[:50]} |")
        
        # Query analysis per type
        report.append("\n## 2. Query Response Analysis\n")
        
        query_types = {}
        for bot_result in results:
            for q in bot_result["queries"]:
                qt = q["type"]
                if qt not in query_types:
                    query_types[qt] = []
                query_types[qt].append({
                    "bot": bot_result["bot_name"],
                    "site": bot_result["site"]["url"],
                    **q
                })
        
        for qtype, queries in query_types.items():
            report.append(f"\n### {qtype.upper()} Queries\n")
            
            success_count = 0
            fail_count = 0
            issues = []
            
            for q in queries:
                resp = q["response"]
                has_error = q.get("error")
                products = q.get("products_count", 0)
                tags = q.get("tags", [])
                
                is_good = True
                issue_notes = []
                
                # Evaluate based on type
                if qtype.startswith("product"):
                    if products == 0 and "product" not in resp.lower() and "item" not in resp.lower():
                        is_good = False
                        issue_notes.append("No products found for product query")
                
                elif qtype == "irrelevant":
                    if "irrelevant" not in str(tags).lower() and "out_of_scope" not in str(tags).lower():
                        if "sorry" not in resp.lower() and "can't help" not in resp.lower() and "outside" not in resp.lower():
                            is_good = False
                            issue_notes.append("Bot answered irrelevant query without flagging it")
                
                elif qtype == "missing-info":
                    if "don't have" not in resp.lower() and "not available" not in resp.lower() and "missing" not in str(tags).lower():
                        issue_notes.append("Possible missing info not detected")
                
                elif qtype == "greeting":
                    if len(resp) < 5:
                        is_good = False
                        issue_notes.append("No greeting response")
                
                if has_error:
                    is_good = False
                    issue_notes.append(f"Error: {has_error}")
                
                if is_good:
                    success_count += 1
                else:
                    fail_count += 1
                
                if issue_notes:
                    issues.append(f"  - **{q['bot']}**: {'; '.join(issue_notes)}")
                
                report.append(f"- **{q['bot']}** ({q['site']})")
                report.append(f"  - Query: \"{q['query']}\"")
                report.append(f"  - Response: {resp[:150]}...")
                report.append(f"  - Products: {products} | Tags: {tags} | Suggestions: {len(q.get('suggestions', []))}")
                if issue_notes:
                    report.append(f"  - ⚠️ Issues: {'; '.join(issue_notes)}")
                report.append("")
            
            report.append(f"\n**{qtype} Summary**: {success_count}/{success_count+fail_count} passed")
            if issues:
                report.append("\n**Issues found:**")
                report.extend(issues)
        
        # Overall recommendations
        report.append("\n## 3. Recommendations\n")
        report.append("Based on the analysis above, here are key areas for improvement:\n")
        report.append("1. **Crawl Robustness**: Sites that blocked or failed need better error handling")
        report.append("2. **Product Detection**: Review product extraction for sites with zero products")
        report.append("3. **Irrelevant Query Handling**: Ensure consistent flagging of off-topic queries")
        report.append("4. **Missing Info Detection**: Improve detection of information gaps")
        report.append("5. **Error Messages**: Provide clearer user-facing error messages")
        
        report_content = "\n".join(report)
        with open("CRAWL_TEST_ANALYSIS_REPORT.md", "w", encoding="utf-8") as f:
            f.write(report_content)
        print(report_content)
        print(f"\n\nReport saved to CRAWL_TEST_ANALYSIS_REPORT.md")
    
    else:
        print(f"Unknown mode: {mode}")
        print("Usage: python test_crawl_analysis.py [list|create|crawl_batch <N>|test_queries|report]")
