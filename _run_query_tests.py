"""
Comprehensive query testing for all crawled bots.
Uses subprocess for each query to avoid SSE stream hanging issues.
Tests: greeting, product, non-product, irrelevant, missing-info, complex, context queries.
"""
import requests
import json
import time
import subprocess
import sys
import os

API = "http://localhost:8000/api/v1"

# Login
s = requests.Session()
r = s.post(f"{API}/auth/login", json={"email": "max@gmail.com", "password": "12345678"})
token = r.json()["access_token"]
s.headers.update({"Authorization": f"Bearer {token}"})

# All bots with crawled data
BOTS = {
    "CrawlTest-themancompany": {"id": "9fa35176-cf46-42f1-ad62-cd077c7a4788", "url": "themancompany.com", "desc": "Men's grooming India", "pages": 55},
    "CrawlTest-mokobara": {"id": "afda9afb-bcc1-4cfa-b8fe-da5f5fc38f73", "url": "mokobara.com", "desc": "Travel bags & luggage", "pages": 52},
    "CrawlTest-rawpressery": {"id": "cc90afbd-5839-45d5-a4aa-68f681f60e61", "url": "rawpressery.com", "desc": "Cold pressed juices", "pages": 39},
    "CrawlTest-slurrpfarm": {"id": "33231221-b581-4058-9b38-2797b78d5947", "url": "slurrpfarm.com", "desc": "Organic kids food", "pages": 52},
    "CrawlTest-vahdam": {"id": "babcd869-2ab9-4fc0-85df-3b52d4654142", "url": "vahdam.com", "desc": "Indian teas", "pages": 54},
    "CrawlTest-plumgoodness": {"id": "a839779a-0820-4694-b7e5-916ffab8ed7c", "url": "plumgoodness.com", "desc": "Vegan beauty products", "pages": 53},
    "CrawlTest-nykaa": {"id": "e56295e0-1c15-4852-af46-8ce76f890575", "url": "nykaa.com", "desc": "Indian beauty & cosmetics", "pages": 497},
    "CrawlTest-bewakoof": {"id": "77f727d3-53a2-4691-a32b-d62ca1dfb575", "url": "bewakoof.com", "desc": "Indian casual fashion", "pages": 241},
    "CrawlTest-chumbak": {"id": "854d3f93-b66d-41ff-b833-1f250093ab2a", "url": "chumbak.com", "desc": "Indian quirky lifestyle brand", "pages": 185},
    "CrawlTest-zappos": {"id": "e8fe8c99-e3bb-4b58-9900-9853525b5362", "url": "zappos.com", "desc": "Shoes & clothing", "pages": 172},
    "CrawlTest-nicobar": {"id": "ce8a4a3b-eb33-4187-8731-8921060c6b38", "url": "nicobar.com", "desc": "Indian clothing & lifestyle", "pages": 135},
    "Crawl-Tentree": {"id": "799637f9-391b-4b9d-84cb-5fdd17cdf109", "url": "tentree.com", "desc": "Sustainable clothing", "pages": 265},
    "Crawl-DeathWishCoffee": {"id": "99fc3604-99e7-4cd0-a2a6-509ac08d9fd0", "url": "deathwishcoffee.com", "desc": "Strong coffee", "pages": 811},
    "Crawl-Beardbrand": {"id": "e23fcc6f-7a02-4b09-8d49-95c00a57d852", "url": "beardbrand.com", "desc": "Men's grooming", "pages": 454},
    "ramraj": {"id": "182f88cd-02d8-4c94-824d-b41432847400", "url": "ramrajcotton.in", "desc": "Cotton clothing India", "pages": 4497},
    "kriyanta": {"id": "1cb18dc0-4909-409d-ab03-0436524fcec4", "url": "kriyanta.com", "desc": "Home decor India", "pages": 803},
    "zevaramaze": {"id": "e79b3754-006d-45d5-b21d-2391710e08ca", "url": "zevaramaze.com", "desc": "Ethnic wear", "pages": 408},
}

# Query templates per type - customized per bot
def get_queries_for_bot(bot_name, desc):
    """Generate test queries based on the bot's domain"""
    queries = []
    
    # 1. Greeting
    queries.append({"type": "greeting", "query": "Hi there! How can you help me?", "expect": "greeting_response"})
    
    # 2. Product search (generic)
    queries.append({"type": "product_general", "query": "Show me your best selling products", "expect": "product_list"})
    
    # 3. Product search (specific) - based on domain
    specific_product_queries = {
        "themancompany": "Do you have beard oil?",
        "mokobara": "Show me your laptop backpacks",
        "rawpressery": "What fruit juices do you have?",
        "slurrpfarm": "Show me organic cereals for kids",
        "vahdam": "What green tea varieties do you have?",
        "plumgoodness": "Show me face serums",
        "nykaa": "What lipstick brands do you have?",
        "bewakoof": "Show me oversized t-shirts for men",
        "chumbak": "Show me your phone cases",
        "zappos": "Show me running shoes for men",
        "nicobar": "Show me summer dresses",
        "tentree": "Show me men's jackets",
        "deathwishcoffee": "What coffee blends do you offer?",
        "beardbrand": "Show me beard wash products",
        "ramrajcotton": "Show me cotton dhotis",
        "kriyanta": "Show me wall art options",
        "zevaramaze": "Show me kurta sets for women",
    }
    domain_key = bot_name.lower().replace("crawltest-", "").replace("crawl-", "").replace(" ", "")
    specific_q = specific_product_queries.get(domain_key, f"Show me popular items from {desc}")
    queries.append({"type": "product_specific", "query": specific_q, "expect": "product_list"})
    
    # 4. Product with price filter
    queries.append({"type": "product_price", "query": "What products do you have under 500 rupees?", "expect": "product_list_or_info"})
    
    # 5. Non-product: shipping
    queries.append({"type": "non_product_shipping", "query": "What are your shipping options and delivery times?", "expect": "info_response"})
    
    # 6. Non-product: return policy
    queries.append({"type": "non_product_returns", "query": "What is your return and refund policy?", "expect": "info_response"})
    
    # 7. Non-product: contact
    queries.append({"type": "non_product_contact", "query": "How can I contact customer support?", "expect": "info_response"})
    
    # 8. Irrelevant query
    queries.append({"type": "irrelevant_1", "query": "What is the weather in Mumbai today?", "expect": "deflection"})
    queries.append({"type": "irrelevant_2", "query": "Who won the cricket world cup 2023?", "expect": "deflection"})
    
    # 9. Missing info query (something plausible but likely not in data)
    missing_info_queries = {
        "themancompany": "What is the ingredients list for your charcoal face wash?",
        "mokobara": "What is the warranty period for luggage?",
        "rawpressery": "What is the shelf life of your juices after opening?",
        "slurrpfarm": "What age group are your products suitable for?",
        "vahdam": "How should I store loose leaf tea?",
        "plumgoodness": "Are your products tested on animals?",
        "nykaa": "What is the expiry date of the products?",
        "bewakoof": "What sizes are available for plus size clothing?",
        "chumbak": "Do you offer gift wrapping?",
        "zappos": "Do you ship internationally?",
        "nicobar": "What fabrics do you use?",
        "tentree": "How many trees have you planted so far?",
        "deathwishcoffee": "What is the caffeine content per cup?",
        "beardbrand": "How long does a bottle of beard oil last?",
        "ramrajcotton": "Do you have options for school uniforms?",
        "kriyanta": "Do you offer custom art pieces?",
        "zevaramaze": "What is the fabric composition of your kurtas?",
    }
    missing_q = missing_info_queries.get(domain_key, "Can you tell me the exact manufacturing process?")
    queries.append({"type": "missing_info", "query": missing_q, "expect": "may_lack_info"})
    
    # 10. Complex query
    queries.append({"type": "complex", "query": f"I'm looking for a gift for my friend. Can you suggest something from your collection that's popular and affordable?", "expect": "helpful_response"})
    
    # 11. Hindi query
    queries.append({"type": "hindi", "query": "आपके पास क्या प्रोडक्ट्स हैं?", "expect": "hindi_response"})
    
    return queries


def send_query_subprocess(bot_id, query, session_id=None, timeout=45):
    """Send a query using a subprocess to avoid hanging"""
    script = f'''
import requests
import json
import sys

API = "http://localhost:8000/api/v1"
s = requests.Session()
r = s.post(f"{{API}}/auth/login", json={{"email":"max@gmail.com","password":"12345678"}})
token = r.json()["access_token"]

data = {{"message": {json.dumps(query)}}}
if {json.dumps(session_id)} is not None:
    data["session_id"] = {json.dumps(session_id)}

try:
    resp = s.post(
        f"{{API}}/chat/{bot_id}/message/stream",
        data=data,
        headers={{"Authorization": f"Bearer {{token}}"}},
        stream=True,
        timeout=40
    )
    
    full_text = ""
    session = None
    tags = []
    suggestions = []
    products = []
    
    for line in resp.iter_lines(decode_unicode=True):
        if not line or not line.startswith("data: "):
            continue
        payload = line[6:]
        if payload == "[DONE]":
            break
        try:
            evt = json.loads(payload)
            etype = evt.get("type", "")
            if etype == "session":
                session = evt.get("session_id")
            elif etype == "content":
                full_text += evt.get("text", "")
            elif etype == "done":
                tags = evt.get("tags", [])
                suggestions = evt.get("suggestions", [])
                products = evt.get("products", [])
        except:
            pass
    
    result = {{
        "text": full_text[:800],
        "session_id": session,
        "tags": tags,
        "suggestions": suggestions,
        "product_count": len(products),
        "products": [{{
            "name": p.get("name", "?")[:50],
            "price": p.get("price") or p.get("formatted_price", ""),
        }} for p in products[:5]],
        "text_len": len(full_text),
        "ok": True
    }}
    print(json.dumps(result))
except requests.exceptions.Timeout:
    print(json.dumps({{"ok": False, "error": "timeout"}}))
except Exception as e:
    print(json.dumps({{"ok": False, "error": str(e)[:200]}}))
'''
    
    try:
        result = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True, text=True, timeout=timeout
        )
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout.strip())
        else:
            return {"ok": False, "error": f"exit={result.returncode} stderr={result.stderr[:200]}"}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "subprocess_timeout"}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


def run_all_tests():
    """Run all queries on all bots"""
    results = {}
    total_queries = 0
    total_success = 0
    total_fail = 0
    
    bot_names = list(BOTS.keys())
    print(f"Testing {len(bot_names)} bots...")
    
    for bot_idx, (bot_name, bot_info) in enumerate(BOTS.items()):
        print(f"\n{'='*60}")
        print(f"[{bot_idx+1}/{len(BOTS)}] {bot_name} ({bot_info['desc']}, {bot_info['pages']} pages)")
        print(f"{'='*60}")
        
        queries = get_queries_for_bot(bot_name, bot_info['desc'])
        bot_results = []
        session_id = None
        
        for q_idx, q in enumerate(queries):
            print(f"  [{q_idx+1}/{len(queries)}] {q['type']:25s} | {q['query'][:50]:50s}", end=" | ", flush=True)
            
            result = send_query_subprocess(bot_info['id'], q['query'], session_id)
            
            if result.get("ok"):
                # Update session for context queries
                if result.get("session_id"):
                    session_id = result["session_id"]
                
                print(f"OK | {result.get('text_len', 0):4d}ch | prods={result.get('product_count', 0)} | tags={result.get('tags', [])}")
                total_success += 1
            else:
                print(f"FAIL | {result.get('error', '?')[:50]}")
                total_fail += 1
            
            total_queries += 1
            bot_results.append({
                "query": q['query'],
                "type": q['type'],
                "expect": q['expect'],
                **result
            })
            
            # Small delay between queries
            time.sleep(1)
        
        results[bot_name] = {
            "info": bot_info,
            "queries": bot_results
        }
        
        # Save intermediate results
        with open("_query_results_intermediate.json", "w") as f:
            json.dump(results, f, indent=2, default=str, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"TOTAL: {total_queries} queries | {total_success} success | {total_fail} failed")
    print(f"{'='*60}")
    
    # Save final results
    with open("_query_results_final.json", "w") as f:
        json.dump(results, f, indent=2, default=str, ensure_ascii=False)
    print("Results saved to _query_results_final.json")
    
    return results


if __name__ == "__main__":
    results = run_all_tests()
