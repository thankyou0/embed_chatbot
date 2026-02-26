"""
Query testing for NEW crawled bots only (excluding oldest 6 and failed crawls).
Uses subprocess per query to avoid SSE stream hanging.
"""
import json
import time
import subprocess
import sys
import os

# NEW bots only (exclude old 6: ramraj, kriyanta, zevaramaze, Crawl-Tentree, Crawl-DeathWishCoffee, Crawl-Beardbrand)
# Exclude failed: etsy, wayfair, bombayshirtcompany
BOTS = {
    "CrawlTest-themancompany": {"id": "9fa35176-cf46-42f1-ad62-cd077c7a4788", "desc": "Men's grooming India", "pages": 55},
    "CrawlTest-mokobara": {"id": "afda9afb-bcc1-4cfa-b8fe-da5f5fc38f73", "desc": "Travel bags & luggage", "pages": 52},
    "CrawlTest-rawpressery": {"id": "cc90afbd-5839-45d5-a4aa-68f681f60e61", "desc": "Cold pressed juices", "pages": 39},
    "CrawlTest-slurrpfarm": {"id": "33231221-b581-4058-9b38-2797b78d5947", "desc": "Organic kids food", "pages": 52},
    "CrawlTest-vahdam": {"id": "babcd869-2ab9-4fc0-85df-3b52d4654142", "desc": "Indian teas", "pages": 54},
    "CrawlTest-plumgoodness": {"id": "a839779a-0820-4694-b7e5-916ffab8ed7c", "desc": "Vegan beauty products", "pages": 53},
    "CrawlTest-nykaa": {"id": "e56295e0-1c15-4852-af46-8ce76f890575", "desc": "Indian beauty & cosmetics", "pages": 497},
    "CrawlTest-bewakoof": {"id": "77f727d3-53a2-4691-a32b-d62ca1dfb575", "desc": "Indian casual fashion", "pages": 241},
    "CrawlTest-chumbak": {"id": "854d3f93-b66d-41ff-b833-1f250093ab2a", "desc": "Indian quirky lifestyle", "pages": 185},
    "CrawlTest-zappos": {"id": "e8fe8c99-e3bb-4b58-9900-9853525b5362", "desc": "Shoes & clothing", "pages": 172},
    "CrawlTest-nicobar": {"id": "ce8a4a3b-eb33-4187-8731-8921060c6b38", "desc": "Indian clothing & lifestyle", "pages": 135},
}

SPECIFIC_PRODUCT_Q = {
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
}

MISSING_INFO_Q = {
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
}

def get_queries(bot_name, desc):
    key = bot_name.lower().replace("crawltest-", "")
    return [
        {"type": "greeting", "query": "Hi there! How can you help me?", "expect": "greeting_response"},
        {"type": "product_general", "query": "Show me your best selling products", "expect": "product_list"},
        {"type": "product_specific", "query": SPECIFIC_PRODUCT_Q.get(key, f"Show me popular items"), "expect": "product_list"},
        {"type": "product_price", "query": "What products do you have under 500 rupees?", "expect": "product_list_or_info"},
        {"type": "non_product_shipping", "query": "What are your shipping options and delivery times?", "expect": "info_response"},
        {"type": "non_product_returns", "query": "What is your return and refund policy?", "expect": "info_response"},
        {"type": "non_product_contact", "query": "How can I contact customer support?", "expect": "info_response"},
        {"type": "irrelevant_1", "query": "What is the weather in Mumbai today?", "expect": "deflection"},
        {"type": "irrelevant_2", "query": "Who won the cricket world cup 2023?", "expect": "deflection"},
        {"type": "missing_info", "query": MISSING_INFO_Q.get(key, "Can you tell me the exact manufacturing process?"), "expect": "may_lack_info"},
        {"type": "complex", "query": "I'm looking for a gift for my friend. Can you suggest something popular and affordable?", "expect": "helpful_response"},
        {"type": "hindi", "query": "आपके पास क्या प्रोडक्ट्स हैं?", "expect": "hindi_response"},
    ]


# Write the subprocess helper script to a file so we avoid inline script issues
HELPER_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_query_helper.py")

def write_helper():
    code = r'''
import requests, json, sys

API = "http://localhost:8000/api/v1"
bot_id = sys.argv[1]
query = sys.argv[2]
session_id = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] != "NONE" else None

s = requests.Session()
r = s.post(f"{API}/auth/login", json={"email":"max@gmail.com","password":"12345678"})
token = r.json()["access_token"]

data = {"message": query}
if session_id:
    data["session_id"] = session_id

try:
    resp = s.post(
        f"{API}/chat/{bot_id}/message/stream",
        data=data,
        headers={"Authorization": f"Bearer {token}"},
        stream=True,
        timeout=40
    )

    full_text = ""
    session = None
    tags = []
    suggestions = []
    products = []
    error = None

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
                full_text += evt.get("content", "") or evt.get("text", "")
            elif etype == "done":
                tags = evt.get("tags", [])
                suggestions = evt.get("suggestions", [])
                products = evt.get("products", [])
                error = evt.get("error")
        except:
            pass

    result = {
        "text": full_text[:800],
        "session_id": session,
        "tags": tags,
        "suggestions": suggestions[:4],
        "product_count": len(products),
        "products": [{
            "name": p.get("name", "?")[:50],
            "price": p.get("price") or p.get("formatted_price", ""),
        } for p in products[:5]],
        "text_len": len(full_text),
        "error": error,
        "ok": True
    }
    print(json.dumps(result, ensure_ascii=False))
except requests.exceptions.Timeout:
    print(json.dumps({"ok": False, "error": "timeout"}))
except Exception as e:
    print(json.dumps({"ok": False, "error": str(e)[:200]}))
'''
    with open(HELPER_SCRIPT, "w", encoding="utf-8") as f:
        f.write(code)


def send_query(bot_id, query, session_id=None, timeout=50):
    args = [sys.executable, HELPER_SCRIPT, bot_id, query, session_id or "NONE"]
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=timeout, 
                                encoding="utf-8", errors="replace")
        if result.returncode == 0 and result.stdout and result.stdout.strip():
            lines = result.stdout.strip().split("\n")
            return json.loads(lines[-1])
        else:
            err = (result.stderr or "")[:200] if result else "no result"
            return {"ok": False, "error": f"exit={result.returncode} err={err}"}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "subprocess_timeout"}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


def main():
    write_helper()
    results = {}
    total_q = 0
    total_ok = 0
    total_fail = 0

    for bot_idx, (bot_name, info) in enumerate(BOTS.items()):
        print(f"\n{'='*70}")
        print(f"[{bot_idx+1}/{len(BOTS)}] {bot_name} ({info['desc']}, {info['pages']} pages)")
        print(f"{'='*70}")

        queries = get_queries(bot_name, info["desc"])
        bot_results = []
        session_id = None

        for qi, q in enumerate(queries):
            label = f"  [{qi+1}/{len(queries)}] {q['type']:25s}"
            print(f"{label} | {q['query'][:50]:50s}", end=" | ", flush=True)

            r = send_query(info["id"], q["query"], session_id)
            if r.get("ok"):
                if r.get("session_id"):
                    session_id = r["session_id"]
                prods = r.get("product_count", 0)
                tags = r.get("tags", [])
                tlen = r.get("text_len", 0)
                err = r.get("error", "")
                err_str = f" ERR={err}" if err else ""
                print(f"OK {tlen:4d}ch prods={prods} tags={tags}{err_str}")
                total_ok += 1
            else:
                print(f"FAIL {r.get('error','?')[:60]}")
                total_fail += 1

            total_q += 1
            bot_results.append({**q, **r})
            time.sleep(3)  # Longer delay to avoid rate limits

        results[bot_name] = {"info": info, "queries": bot_results}

        # Save intermediate
        with open("_query_results_intermediate.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n{'='*70}")
    print(f"DONE: {total_q} queries | {total_ok} OK | {total_fail} FAIL")
    print(f"{'='*70}")

    with open("_query_results_final.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    print("Saved to _query_results_final.json")

    # Cleanup helper
    try:
        os.remove(HELPER_SCRIPT)
    except:
        pass


if __name__ == "__main__":
    main()
