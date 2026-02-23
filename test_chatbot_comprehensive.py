"""
Comprehensive Chatbot Testing Script
Tests chat service across multiple e-commerce sites with diverse query types.
"""

import requests
import json
import time
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

BASE_URL = "http://localhost:8000/api/v1"
EMAIL = "max@gmail.com"
PASSWORD = "12345678"

# ============================================================
# E-commerce sites to crawl (diverse structures & niches)
# ============================================================
SITES_TO_CRAWL = [
    {"name": "Bewakoof", "url": "https://www.bewakoof.com", "category": "Fashion/Clothing", "expected": "trendy casual wear, t-shirts, joggers"},
    {"name": "Lenskart", "url": "https://www.lenskart.com", "category": "Eyewear", "expected": "glasses, sunglasses, contact lenses"},
    {"name": "Boat Lifestyle", "url": "https://www.boat-lifestyle.com", "category": "Electronics/Audio", "expected": "earbuds, headphones, speakers, smartwatches"},
    {"name": "Mamaearth", "url": "https://mamaearth.in", "category": "Beauty/Skincare", "expected": "skincare, haircare, organic products"},
    {"name": "Chumbak", "url": "https://www.chumbak.com", "category": "Home Decor/Lifestyle", "expected": "bags, decor, accessories, quirky designs"},
    {"name": "The Souled Store", "url": "https://www.thesouledstore.com", "category": "Pop Culture Fashion", "expected": "pop culture merch, t-shirts, shoes"},
    {"name": "Nestasia", "url": "https://nestasia.in", "category": "Home/Kitchen", "expected": "home decor, tableware, kitchen items"},
    {"name": "Nykaa Fashion", "url": "https://www.nykaafashion.com", "category": "Fashion", "expected": "women's fashion, dresses, ethnic wear"},
    {"name": "Snitch", "url": "https://www.snitch.co.in", "category": "Men's Fashion", "expected": "men's shirts, trousers, jackets"},
    {"name": "Sugar Cosmetics", "url": "https://in.sugarcosmetics.com", "category": "Cosmetics", "expected": "lipstick, foundation, eye makeup"},
    {"name": "Mokobara", "url": "https://www.mokobara.com", "category": "Bags/Luggage", "expected": "backpacks, luggage, travel bags"},
    {"name": "BlissClub", "url": "https://www.myblissclub.com", "category": "Activewear", "expected": "activewear, leggings, sports bras"},
]

# ============================================================
# Query templates organized by type
# ============================================================
def get_query_templates(site_category: str, site_name: str) -> List[Dict]:
    """Generate diverse queries based on site category."""
    
    queries = []
    
    # ---- TYPE 1: General Greeting ----
    queries.append({
        "type": "greeting",
        "queries": [
            {"lang": "en", "text": "Hi there!"},
            {"lang": "hi", "text": "नमस्ते"},
            {"lang": "hi_roman", "text": "hello bhai"},
            {"lang": "gu", "text": "કેમ છો?"},
        ]
    })
    
    # ---- TYPE 2: General Product Browsing ----
    category_products = {
        "Fashion/Clothing": ["t-shirts", "jeans", "hoodies", "dresses"],
        "Eyewear": ["sunglasses", "reading glasses", "computer glasses", "contact lenses"],
        "Electronics/Audio": ["earbuds", "headphones", "speakers", "smartwatches"],
        "Beauty/Skincare": ["face wash", "moisturizer", "sunscreen", "hair oil"],
        "Home Decor/Lifestyle": ["mugs", "cushion covers", "wall art", "bags"],
        "Pop Culture Fashion": ["marvel t-shirts", "anime hoodies", "sneakers", "joggers"],
        "Home/Kitchen": ["dinner set", "mugs", "planters", "storage jars"],
        "Fashion": ["kurtas", "dresses", "tops", "sarees"],
        "Men's Fashion": ["shirts", "trousers", "jackets", "casual wear"],
        "Cosmetics": ["lipstick", "foundation", "mascara", "eye shadow"],
        "Bags/Luggage": ["backpacks", "trolley bags", "laptop bags", "duffle bags"],
        "Activewear": ["leggings", "sports bra", "track pants", "gym wear"],
    }
    products = category_products.get(site_category, ["products"])
    
    queries.append({
        "type": "product_browse",
        "queries": [
            {"lang": "en", "text": f"Show me your best {products[0]}"},
            {"lang": "en", "text": f"What {products[1] if len(products) > 1 else products[0]} do you have?"},
            {"lang": "hi", "text": f"आपके पास कौन से {products[0]} उपलब्ध हैं?"},
            {"lang": "hi_roman", "text": f"mujhe {products[0]} dikhao"},
            {"lang": "gu", "text": f"તમારી પાસે કયા {products[0]} છે?"},
        ]
    })
    
    # ---- TYPE 3: Specific Product Search ----
    queries.append({
        "type": "specific_product",
        "queries": [
            {"lang": "en", "text": f"I'm looking for a black {products[0]}"},
            {"lang": "en", "text": f"Do you have any blue {products[1] if len(products) > 1 else products[0]}?"},
            {"lang": "hi", "text": f"काला {products[0]} चाहिए"},
            {"lang": "gu", "text": f"કાળો {products[0]} જોઈએ છે"},
        ]
    })
    
    # ---- TYPE 4: Price-based Query ----
    queries.append({
        "type": "price_filter",
        "queries": [
            {"lang": "en", "text": f"Show me {products[0]} under ₹500"},
            {"lang": "en", "text": f"What {products[0]} do you have between ₹1000 and ₹2000?"},
            {"lang": "hi", "text": f"500 रुपये से कम के {products[0]} दिखाओ"},
            {"lang": "hi_roman", "text": f"1000 rupaye se kam ke {products[0]} batao"},
            {"lang": "gu", "text": f"₹500 થી ઓછા {products[0]} બતાવો"},
        ]
    })
    
    # ---- TYPE 5: Non-Product / Policy Query ----
    queries.append({
        "type": "non_product",
        "queries": [
            {"lang": "en", "text": "What is your return policy?"},
            {"lang": "en", "text": "How long does shipping take?"},
            {"lang": "en", "text": "Do you offer cash on delivery?"},
            {"lang": "hi", "text": "रिटर्न पॉलिसी क्या है?"},
            {"lang": "gu", "text": "શિપિંગ કેટલો સમય લે છે?"},
        ]
    })
    
    # ---- TYPE 6: Irrelevant Query (should be rejected) ----
    queries.append({
        "type": "irrelevant",
        "queries": [
            {"lang": "en", "text": "What is the capital of France?"},
            {"lang": "en", "text": "Can you write me a Python script?"},
            {"lang": "hi", "text": "भारत का प्रधानमंत्री कौन है?"},
            {"lang": "en", "text": "Tell me a joke"},
        ]
    })
    
    # ---- TYPE 7: Missing Info / Ambiguous Query ----
    queries.append({
        "type": "missing_info",
        "queries": [
            {"lang": "en", "text": "I want something nice for a gift"},
            {"lang": "en", "text": "What do you recommend?"},
            {"lang": "hi", "text": "कुछ अच्छा बताओ"},
            {"lang": "gu", "text": "કંઈક સારું બતાવો"},
        ]
    })
    
    # ---- TYPE 8: Complex / Multi-intent Query ----
    queries.append({
        "type": "complex",
        "queries": [
            {"lang": "en", "text": f"I need a gift for my friend, she likes {products[0]} in red or blue color, budget is around 1500 rupees"},
            {"lang": "hi", "text": f"मेरी बहन के लिए {products[0]} चाहिए, लाल या नीला रंग, 2000 रुपये से कम"},
            {"lang": "en", "text": f"What's the difference between your cheapest and most expensive {products[0]}?"},
        ]
    })
    
    # ---- TYPE 9: Conversation Context / Follow-up ----
    queries.append({
        "type": "context_followup",
        "queries": [
            {"lang": "en", "text": f"Show me {products[0]}"},
            {"lang": "en", "text": "Do you have this in a different color?"},
            {"lang": "en", "text": "What about a smaller size?"},
            {"lang": "en", "text": "Can you summarize what we discussed?"},
        ]
    })
    
    # ---- TYPE 10: Color Filter Query ----
    queries.append({
        "type": "color_filter",
        "queries": [
            {"lang": "en", "text": f"Show me red {products[0]}"},
            {"lang": "hi", "text": f"सफेद {products[0]} दिखाओ"},
            {"lang": "gu", "text": f"લાલ {products[0]} બતાવો"},
            {"lang": "en", "text": f"I want a white or cream colored {products[0]}"},
        ]
    })
    
    # ---- TYPE 11: About the Brand / Company ----
    queries.append({
        "type": "about_brand",
        "queries": [
            {"lang": "en", "text": f"Tell me about {site_name}"},
            {"lang": "en", "text": "Where is your company located?"},
            {"lang": "hi", "text": f"{site_name} के बारे में बताओ"},
        ]
    })
    
    # ---- TYPE 12: Unsupported Language Test ----
    queries.append({
        "type": "unsupported_language",
        "queries": [
            {"lang": "fr", "text": "Bonjour, montrez-moi vos produits"},
            {"lang": "ja", "text": "こんにちは、製品を見せてください"},
        ]
    })
    
    # ---- TYPE 13: Suggestions Quality Test ----
    queries.append({
        "type": "suggestions_test",
        "queries": [
            {"lang": "en", "text": f"I'm new here, what do you sell?"},
            {"lang": "hi", "text": "यहां क्या मिलता है?"},
        ]
    })
    
    return queries


# ============================================================
# API Helper Functions (with retry logic)
# ============================================================

def retry_request(func, *args, max_retries=3, backoff=5, **kwargs):
    """Retry a request function with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            if attempt < max_retries - 1:
                wait = backoff * (2 ** attempt)
                print(f"\n      [RETRY] Connection error, waiting {wait}s (attempt {attempt+1}/{max_retries})...")
                time.sleep(wait)
            else:
                raise


def login() -> str:
    """Login and return access token."""
    def _login():
        resp = requests.post(f"{BASE_URL}/auth/login", json={"email": EMAIL, "password": PASSWORD}, timeout=30)
        resp.raise_for_status()
        return resp.json()["access_token"]
    return retry_request(_login)


def get_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def list_chatbots(token: str) -> List[Dict]:
    def _list():
        resp = requests.get(f"{BASE_URL}/chatbots", headers=get_headers(token), timeout=30)
        resp.raise_for_status()
        return resp.json()["chatbots"]
    return retry_request(_list)


def create_chatbot(token: str, name: str) -> Dict:
    def _create():
        resp = requests.post(f"{BASE_URL}/chatbots", headers=get_headers(token), json={"name": name}, timeout=30)
        resp.raise_for_status()
        return resp.json()
    return retry_request(_create)


def get_knowledge_sources(token: str, chatbot_id: str) -> List[Dict]:
    def _get():
        resp = requests.get(f"{BASE_URL}/chatbots/{chatbot_id}/knowledge-sources", headers=get_headers(token), timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and "sources" in data:
            return data["sources"]
        return data if isinstance(data, list) else []
    return retry_request(_get)


def start_crawl(token: str, chatbot_id: str, url: str) -> Dict:
    def _start():
        resp = requests.post(
            f"{BASE_URL}/chatbots/{chatbot_id}/crawl",
            headers=get_headers(token),
            json={"base_url": url},
            timeout=30
        )
        resp.raise_for_status()
        return resp.json()
    return retry_request(_start)


def get_crawl_status(token: str, source_id: str) -> Dict:
    def _status():
        resp = requests.get(
            f"{BASE_URL}/chatbots/knowledge-sources/{source_id}/status",
            headers=get_headers(token),
            timeout=30
        )
        resp.raise_for_status()
        return resp.json()
    return retry_request(_status)


def stop_crawl(token: str, source_id: str) -> Dict:
    def _stop():
        resp = requests.post(
            f"{BASE_URL}/chatbots/knowledge-sources/{source_id}/stop",
            headers=get_headers(token),
            timeout=30
        )
        resp.raise_for_status()
        return resp.json()
    return retry_request(_stop)


def send_chat_message(chatbot_id: str, message: str, session_id: Optional[str] = None) -> Dict:
    """Send message via SSE stream and collect full response."""
    data = {"message": message}
    if session_id:
        data["session_id"] = session_id
    
    try:
        resp = requests.post(
            f"{BASE_URL}/chat/{chatbot_id}/message/stream",
            data=data,
            stream=True,
            timeout=60
        )
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "content": "", "sources": [], "suggestions": [], "products": [], "session_id": None}
    
    result = {
        "content": "",
        "sources": [],
        "suggestions": [],
        "products": [],
        "session_id": None,
        "error": None, 
        "image_analysis": None,
        "status_messages": [],
        "raw_events": []
    }
    
    try:
        for line in resp.iter_lines(decode_unicode=True):
            if not line:
                continue
            if line.startswith("data: "):
                json_str = line[6:]
                try:
                    event = json.loads(json_str)
                    result["raw_events"].append(event)
                    
                    if event.get("type") == "session":
                        result["session_id"] = event.get("session_id")
                    elif event.get("type") == "status":
                        result["status_messages"].append(event.get("status", ""))
                    elif event.get("type") == "content":
                        result["content"] += event.get("content", "")
                    elif event.get("type") == "done":
                        result["sources"] = event.get("sources", [])
                        result["suggestions"] = event.get("suggestions", [])
                        result["products"] = event.get("products", [])
                        result["image_analysis"] = event.get("image_analysis")
                    elif event.get("type") == "error":
                        result["error"] = event.get("error", "Unknown error")
                except json.JSONDecodeError:
                    pass
    except Exception as e:
        result["error"] = f"Stream error: {str(e)}"
    
    return result


def get_chatbot_stats(token: str, chatbot_id: str) -> Dict:
    try:
        resp = requests.get(f"{BASE_URL}/chatbots/{chatbot_id}/stats", headers=get_headers(token))
        resp.raise_for_status()
        return resp.json()
    except:
        return {}


# ============================================================
# Test Result Tracking
# ============================================================

class TestResult:
    def __init__(self, chatbot_name: str, chatbot_id: str, category: str):
        self.chatbot_name = chatbot_name
        self.chatbot_id = chatbot_id
        self.category = category
        self.crawl_info = {}
        self.query_results = []
    
    def add_crawl_info(self, info: Dict):
        self.crawl_info = info
    
    def add_query_result(self, query_type: str, lang: str, query: str, response: Dict, evaluation: Dict):
        self.query_results.append({
            "type": query_type,
            "lang": lang,
            "query": query,
            "response_content": response.get("content", "")[:500],
            "sources_count": len(response.get("sources", [])),
            "products_count": len(response.get("products", [])),
            "suggestions": response.get("suggestions", []),
            "error": response.get("error"),
            "status_messages": response.get("status_messages", []),
            "evaluation": evaluation,
            "products": response.get("products", [])[:5],  # First 5 products
        })

    def to_dict(self) -> Dict:
        return {
            "chatbot_name": self.chatbot_name,
            "chatbot_id": self.chatbot_id,
            "category": self.category,
            "crawl_info": self.crawl_info,
            "query_results": self.query_results,
        }


def evaluate_response(query_type: str, response: Dict, lang: str) -> Dict:
    """Evaluate response quality based on query type."""
    eval_result = {
        "score": 0,  # 0-10
        "issues": [],
        "passed": True,
        "notes": ""
    }
    
    content = response.get("content", "").strip()
    error = response.get("error")
    sources = response.get("sources", [])
    products = response.get("products", [])
    suggestions = response.get("suggestions", [])
    
    # Check for errors
    if error:
        eval_result["score"] = 0
        eval_result["passed"] = False
        eval_result["issues"].append(f"ERROR: {error}")
        return eval_result
    
    # Check empty response
    if not content:
        eval_result["score"] = 0
        eval_result["passed"] = False
        eval_result["issues"].append("Empty response")
        return eval_result
    
    # Type-specific evaluation
    if query_type == "greeting":
        # Should respond with a greeting, not search knowledge base
        if len(content) > 10:
            eval_result["score"] = 8
        else:
            eval_result["score"] = 5
            eval_result["issues"].append("Very short greeting response")
        if suggestions:
            eval_result["score"] = min(10, eval_result["score"] + 1)
            eval_result["notes"] = f"Suggestions: {suggestions}"
    
    elif query_type == "product_browse":
        if products:
            eval_result["score"] = 9
            eval_result["notes"] = f"Found {len(products)} products"
        elif sources:
            eval_result["score"] = 6
            eval_result["notes"] = f"Found sources but no product cards"
            eval_result["issues"].append("No product cards returned for product query")
        else:
            eval_result["score"] = 3
            eval_result["passed"] = False
            eval_result["issues"].append("No products or sources found for product browse query")
    
    elif query_type == "specific_product":
        if products:
            eval_result["score"] = 9
            eval_result["notes"] = f"Found {len(products)} products"
        elif sources:
            eval_result["score"] = 5
            eval_result["issues"].append("Sources found but no product cards")
        else:
            eval_result["score"] = 2
            eval_result["passed"] = False
            eval_result["issues"].append("No results for specific product search")
    
    elif query_type == "price_filter":
        if products:
            eval_result["score"] = 8
            # Check if products actually have price info
            has_prices = any(p.get("price") for p in products)
            if has_prices:
                eval_result["score"] = 9
                eval_result["notes"] = f"Products with prices found"
            else:
                eval_result["issues"].append("Products found but no price data")
        else:
            eval_result["score"] = 3
            eval_result["issues"].append("No products for price filter query")
    
    elif query_type == "non_product":
        # Should provide informational response from knowledge base
        if sources:
            eval_result["score"] = 8
            eval_result["notes"] = "Found relevant sources"
        elif "sorry" in content.lower() or "don't have" in content.lower() or "missing" in content.lower():
            eval_result["score"] = 5
            eval_result["notes"] = "Bot acknowledged missing info"
        else:
            eval_result["score"] = 4
            eval_result["issues"].append("No sources for policy/info query")
    
    elif query_type == "irrelevant":
        # Should reject or indicate out of scope
        irrelevant_markers = ["not related", "can't help", "outside", "scope", "don't have", 
                              "sorry", "cannot", "not able", "beyond", "irrelevant", "unrelated",
                              "assist with", "not something", "IRRELEVANT", "MISSING"]
        is_rejected = any(m.lower() in content.lower() for m in irrelevant_markers)
        if is_rejected:
            eval_result["score"] = 9
            eval_result["notes"] = "Correctly identified as irrelevant"
        else:
            eval_result["score"] = 2
            eval_result["passed"] = False
            eval_result["issues"].append("Failed to detect irrelevant query - bot tried to answer")
    
    elif query_type == "missing_info":
        if suggestions:
            eval_result["score"] = 7
            eval_result["notes"] = f"Gave suggestions: {suggestions}"
        if "recommend" in content.lower() or "suggest" in content.lower() or "popular" in content.lower():
            eval_result["score"] = max(eval_result["score"], 7)
        else:
            eval_result["score"] = max(eval_result["score"], 4)
            eval_result["issues"].append("Could provide better guidance for ambiguous queries")
    
    elif query_type == "complex":
        if products:
            eval_result["score"] = 8
            eval_result["notes"] = f"Handled complex query with {len(products)} products"
        elif sources:
            eval_result["score"] = 5
            eval_result["issues"].append("Sources but no products for complex query")
        else:
            eval_result["score"] = 3
            eval_result["issues"].append("Failed to handle complex multi-intent query")
    
    elif query_type == "context_followup":
        if content and len(content) > 20:
            eval_result["score"] = 7
            eval_result["notes"] = "Follow-up response generated"
        else:
            eval_result["score"] = 3
            eval_result["issues"].append("Poor follow-up context handling")
    
    elif query_type == "color_filter":
        if products:
            eval_result["score"] = 8
            eval_result["notes"] = f"Color filter returned {len(products)} products"
        else:
            eval_result["score"] = 3
            eval_result["issues"].append("No products for color filter query")
    
    elif query_type == "about_brand":
        if sources or len(content) > 50:
            eval_result["score"] = 7
            eval_result["notes"] = "Brand info provided"
        else:
            eval_result["score"] = 3
            eval_result["issues"].append("No brand information found")
    
    elif query_type == "unsupported_language":
        # Should reject unsupported language
        unsupported_markers = ["support", "language", "sorry", "english", "hindi", "gujarati",
                               "not support", "available in"]
        detected_rejection = any(m.lower() in content.lower() for m in unsupported_markers)
        if detected_rejection:
            eval_result["score"] = 9
            eval_result["notes"] = "Correctly rejected unsupported language"
        else:
            eval_result["score"] = 3
            eval_result["issues"].append("Failed to detect/reject unsupported language")
    
    elif query_type == "suggestions_test":
        if suggestions and len(suggestions) >= 2:
            eval_result["score"] = 9
            eval_result["notes"] = f"Good suggestions: {suggestions}"
        elif suggestions:
            eval_result["score"] = 6
            eval_result["notes"] = f"Only {len(suggestions)} suggestion(s)"
        else:
            eval_result["score"] = 3
            eval_result["issues"].append("No suggestions generated")
    
    # Bonus/penalty for suggestions
    if suggestions and query_type not in ["irrelevant", "unsupported_language"]:
        eval_result["score"] = min(10, eval_result["score"] + 0.5)
    
    # Check for "undefined" in response (known bug)
    if "undefined" in content:
        eval_result["issues"].append("Response contains 'undefined' text")
        eval_result["score"] = max(0, eval_result["score"] - 2)
    
    return eval_result


# ============================================================
# Main Test Orchestrator
# ============================================================

def run_tests():
    print("=" * 80)
    print("COMPREHENSIVE CHATBOT TESTING")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Step 1: Login
    print("\n[1] Logging in...")
    token = login()
    print(f"    ✓ Logged in as {EMAIL}")
    
    # Step 2: Get existing chatbots
    print("\n[2] Getting existing chatbots...")
    existing_bots = list_chatbots(token)
    print(f"    Found {len(existing_bots)} existing chatbots:")
    for bot in existing_bots:
        print(f"      - {bot['name']} ({bot['id']}) [{bot['status']}]")
    
    all_test_results = []
    
    # Step 3: Test existing chatbots first
    print("\n[3] Testing existing chatbots...")
    for bot in existing_bots:
        print(f"\n    --- Testing existing: {bot['name']} ---")
        try:
            sources = get_knowledge_sources(token, bot["id"])
        except Exception as e:
            print(f"      ✗ Failed to get sources (retrying after re-login): {e}")
            try:
                token = login()
                sources = get_knowledge_sources(token, bot["id"])
            except Exception as e2:
                print(f"      ✗ Still failed: {e2}, skipping bot")
                continue
        
        # Determine category heuristically
        name_lower = bot["name"].lower()
        if "ramraj" in name_lower:
            category = "Fashion/Clothing"
        elif "truff" in name_lower:
            category = "Food/Condiments"
        elif "kriyanta" in name_lower:
            category = "General/Unknown"
        elif "kids" in name_lower:
            category = "Kids/Clothing"
        elif "zevar" in name_lower:
            category = "Jewelry"
        else:
            category = "General"
        
        result = TestResult(bot["name"], bot["id"], category)
        
        # Get source count
        if isinstance(sources, list):
            source_items = sources
        elif isinstance(sources, dict):
            source_items = sources.get("sources", sources.get("items", []))
        else:
            source_items = []
        
        page_count = 0
        for s in source_items if isinstance(source_items, list) else []:
            if isinstance(s, dict):
                pages = s.get("pages", s.get("crawled_pages", []))
                if isinstance(pages, list):
                    page_count += len(pages)
                elif isinstance(s.get("pages_crawled"), int):
                    page_count += s["pages_crawled"]
        
        result.add_crawl_info({"source_count": len(source_items) if isinstance(source_items, list) else 0, "page_count": page_count})
        print(f"      Sources: {result.crawl_info}")

        # Generate appropriate queries
        templates = get_query_templates(category, bot["name"])
        
        session_id = None
        for template_group in templates:
            qtype = template_group["type"]
            for q in template_group["queries"]:
                # For context_followup, maintain session
                use_session = session_id if qtype == "context_followup" else None
                
                print(f"      [{qtype}][{q['lang']}] {q['text'][:60]}...", end="", flush=True)
                
                # Retry chat message on connection errors
                resp = None
                for chat_attempt in range(3):
                    resp = send_chat_message(bot["id"], q["text"], use_session)
                    if resp.get("error") and "Connection" in str(resp.get("error", "")):
                        print(f" [retry {chat_attempt+1}]", end="", flush=True)
                        time.sleep(5 * (chat_attempt + 1))
                    else:
                        break
                
                if not session_id and resp.get("session_id"):
                    session_id = resp["session_id"]
                
                evaluation = evaluate_response(qtype, resp, q["lang"])
                result.add_query_result(qtype, q["lang"], q["text"], resp, evaluation)
                
                score_icon = "✓" if evaluation["passed"] else "✗"
                print(f" [{score_icon} {evaluation['score']}/10]")
                
                time.sleep(2)  # Rate limit respect
        
        all_test_results.append(result)
        # Save intermediate results after each chatbot
        try:
            with open("chatbot_test_raw_data.json", "w", encoding="utf-8") as f:
                json.dump([r.to_dict() for r in all_test_results], f, indent=2, ensure_ascii=False)
            print(f"      [Saved intermediate results: {len(all_test_results)} bots]")
        except Exception as e:
            print(f"      [Failed to save intermediate: {e}]")
    
    # Step 4: Create and crawl new e-commerce sites
    print("\n[4] Creating chatbots & crawling e-commerce sites...")
    crawl_tracking = []  # Track (chatbot_id, source_id, site_info, result_obj)
    
    for site in SITES_TO_CRAWL:
        print(f"\n    Creating chatbot for: {site['name']}...")
        
        # Check if already exists
        existing = [b for b in existing_bots if site["name"].lower() in b["name"].lower()]
        if existing:
            print(f"      Chatbot already exists: {existing[0]['id']}")
            bot_id = existing[0]["id"]
        else:
            try:
                bot = create_chatbot(token, f"Test-{site['name']}")
                bot_id = bot["id"]
                print(f"      Created: {bot_id}")
            except Exception as e:
                print(f"      ✗ Failed to create: {e}")
                continue
        
        # Start crawl
        print(f"    Starting crawl: {site['url']}...")
        try:
            crawl_resp = start_crawl(token, bot_id, site["url"])
            source_id = crawl_resp.get("id") or crawl_resp.get("source_id") or crawl_resp.get("knowledge_source_id")
            if not source_id:
                # Try to find from the response
                print(f"      Crawl response: {json.dumps(crawl_resp)[:200]}")
                # Try to get knowledge sources 
                ks = get_knowledge_sources(token, bot_id)
                if isinstance(ks, list) and ks:
                    source_id = ks[-1].get("id")
                elif isinstance(ks, dict):
                    src_list = ks.get("sources", ks.get("items", []))
                    if src_list:
                        source_id = src_list[-1].get("id")
            
            if source_id:
                print(f"      Crawl started, source: {source_id}")
                result = TestResult(site["name"], bot_id, site["category"])
                crawl_tracking.append((bot_id, source_id, site, result))
            else:
                print(f"      ✗ Could not get source ID from crawl response")
        except Exception as e:
            print(f"      ✗ Crawl failed: {e}")
            # Still create result for the record
            result = TestResult(site["name"], bot_id, site["category"])
            result.add_crawl_info({"error": str(e), "pages_crawled": 0})
            all_test_results.append(result)
    
    # Step 5: Monitor crawls - wait for pages or stop at ~150
    if crawl_tracking:
        print(f"\n[5] Monitoring {len(crawl_tracking)} crawls...")
        MAX_PAGES = 150
        MAX_WAIT_SECONDS = 600  # 10 min max per site
        CHECK_INTERVAL = 15
        
        active_crawls = list(crawl_tracking)
        completed_crawls = []
        
        while active_crawls:
            still_active = []
            for bot_id, source_id, site, result in active_crawls:
                try:
                    status = get_crawl_status(token, source_id)
                    pages = status.get("pages_crawled", status.get("page_count", 0))
                    crawl_status = status.get("status", "unknown")
                    
                    print(f"    {site['name']}: {pages} pages, status={crawl_status}")
                    
                    if pages >= MAX_PAGES:
                        print(f"    → Stopping {site['name']} (reached {MAX_PAGES} pages)")
                        try:
                            stop_crawl(token, source_id)
                        except:
                            pass
                        result.add_crawl_info({"pages_crawled": pages, "status": "stopped_at_limit", "url": site["url"]})
                        completed_crawls.append((bot_id, source_id, site, result))
                    elif crawl_status in ["completed", "failed", "stopped"]:
                        result.add_crawl_info({"pages_crawled": pages, "status": crawl_status, "url": site["url"]})
                        completed_crawls.append((bot_id, source_id, site, result))
                        if crawl_status == "failed":
                            error_msg = status.get("error", status.get("error_message", "Unknown"))
                            result.crawl_info["error"] = error_msg
                            print(f"    ✗ {site['name']} crawl failed: {error_msg}")
                    else:
                        still_active.append((bot_id, source_id, site, result))
                except Exception as e:
                    print(f"    ✗ Error checking {site['name']}: {e}")
                    result.add_crawl_info({"pages_crawled": 0, "status": "error", "error": str(e), "url": site["url"]})
                    completed_crawls.append((bot_id, source_id, site, result))
            
            active_crawls = still_active
            
            if active_crawls:
                print(f"    ... {len(active_crawls)} still crawling, waiting {CHECK_INTERVAL}s ...")
                time.sleep(CHECK_INTERVAL)
        
        # Step 6: Test all newly crawled chatbots
        print(f"\n[6] Testing {len(completed_crawls)} crawled chatbots...")
        
        for bot_id, source_id, site, result in completed_crawls:
            print(f"\n    --- Testing: {site['name']} ({result.crawl_info.get('pages_crawled', 0)} pages) ---")
            
            if result.crawl_info.get("pages_crawled", 0) == 0:
                print(f"      Skipping - no pages crawled")
                all_test_results.append(result)
                continue
            
            templates = get_query_templates(site["category"], site["name"])
            session_id = None
            
            for template_group in templates:
                qtype = template_group["type"]
                for q in template_group["queries"]:
                    use_session = session_id if qtype == "context_followup" else None
                    
                    print(f"      [{qtype}][{q['lang']}] {q['text'][:60]}...", end="", flush=True)
                    resp = send_chat_message(bot_id, q["text"], use_session)
                    
                    if not session_id and resp.get("session_id"):
                        session_id = resp["session_id"]
                    
                    evaluation = evaluate_response(qtype, resp, q["lang"])
                    result.add_query_result(qtype, q["lang"], q["text"], resp, evaluation)
                    
                    score_icon = "✓" if evaluation["passed"] else "✗"
                    print(f" [{score_icon} {evaluation['score']}/10]")
                    
                    time.sleep(1.5)
            
            all_test_results.append(result)
    
    # Step 7: Generate comprehensive report
    print("\n[7] Generating analysis report...")
    generate_report(all_test_results)
    print("\n" + "=" * 80)
    print("TESTING COMPLETE!")
    print("=" * 80)


def generate_report(results: List[TestResult]):
    """Generate a comprehensive Markdown analysis report."""
    
    report_lines = []
    report_lines.append("# 🔍 Comprehensive Chatbot Testing Report")
    report_lines.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"**Tester:** Automated Testing Script")
    report_lines.append(f"**Total Sites Tested:** {len(results)}")
    
    total_queries = sum(len(r.query_results) for r in results)
    total_passed = sum(1 for r in results for q in r.query_results if q["evaluation"]["passed"])
    total_failed = total_queries - total_passed
    avg_score = sum(q["evaluation"]["score"] for r in results for q in r.query_results) / max(total_queries, 1)
    
    report_lines.append(f"**Total Queries Tested:** {total_queries}")
    report_lines.append(f"**Pass Rate:** {total_passed}/{total_queries} ({100*total_passed/max(total_queries,1):.1f}%)")
    report_lines.append(f"**Average Score:** {avg_score:.1f}/10")
    
    # ============ Executive Summary ============
    report_lines.append("\n---\n## 📊 Executive Summary\n")
    
    # Score by query type
    report_lines.append("### Score by Query Type\n")
    report_lines.append("| Query Type | Avg Score | Pass Rate | Total |")
    report_lines.append("|---|---|---|---|")
    
    type_scores = {}
    for r in results:
        for q in r.query_results:
            qt = q["type"]
            if qt not in type_scores:
                type_scores[qt] = {"scores": [], "passed": 0, "total": 0}
            type_scores[qt]["scores"].append(q["evaluation"]["score"])
            type_scores[qt]["total"] += 1
            if q["evaluation"]["passed"]:
                type_scores[qt]["passed"] += 1
    
    for qt, data in sorted(type_scores.items(), key=lambda x: sum(x[1]["scores"])/max(len(x[1]["scores"]),1), reverse=True):
        avg = sum(data["scores"]) / max(len(data["scores"]), 1)
        pr = 100 * data["passed"] / max(data["total"], 1)
        icon = "🟢" if avg >= 7 else "🟡" if avg >= 4 else "🔴"
        report_lines.append(f"| {icon} {qt} | {avg:.1f}/10 | {pr:.0f}% | {data['total']} |")
    
    # Score by language
    report_lines.append("\n### Score by Language\n")
    report_lines.append("| Language | Avg Score | Pass Rate | Total |")
    report_lines.append("|---|---|---|---|")
    
    lang_scores = {}
    for r in results:
        for q in r.query_results:
            lang = q["lang"]
            if lang not in lang_scores:
                lang_scores[lang] = {"scores": [], "passed": 0, "total": 0}
            lang_scores[lang]["scores"].append(q["evaluation"]["score"])
            lang_scores[lang]["total"] += 1
            if q["evaluation"]["passed"]:
                lang_scores[lang]["passed"] += 1
    
    for lang, data in sorted(lang_scores.items()):
        avg = sum(data["scores"]) / max(len(data["scores"]), 1)
        pr = 100 * data["passed"] / max(data["total"], 1)
        lang_name = {"en": "English", "hi": "Hindi (Devanagari)", "hi_roman": "Hindi (Romanized)", 
                     "gu": "Gujarati", "fr": "French", "ja": "Japanese"}.get(lang, lang)
        report_lines.append(f"| {lang_name} | {avg:.1f}/10 | {pr:.0f}% | {data['total']} |")
    
    # Score by site
    report_lines.append("\n### Score by Site\n")
    report_lines.append("| Site | Category | Pages Crawled | Avg Score | Pass Rate | Queries |")
    report_lines.append("|---|---|---|---|---|---|")
    
    for r in results:
        if not r.query_results:
            report_lines.append(f"| {r.chatbot_name} | {r.category} | {r.crawl_info.get('pages_crawled', r.crawl_info.get('page_count', '?'))} | N/A | N/A | 0 |")
            continue
        scores = [q["evaluation"]["score"] for q in r.query_results]
        avg = sum(scores) / max(len(scores), 1)
        passed = sum(1 for q in r.query_results if q["evaluation"]["passed"])
        pr = 100 * passed / max(len(r.query_results), 1)
        pages = r.crawl_info.get("pages_crawled", r.crawl_info.get("page_count", "?"))
        icon = "🟢" if avg >= 7 else "🟡" if avg >= 4 else "🔴"
        report_lines.append(f"| {icon} {r.chatbot_name} | {r.category} | {pages} | {avg:.1f}/10 | {pr:.0f}% | {len(r.query_results)} |")
    
    # ============ Crawl Analysis ============
    report_lines.append("\n---\n## 🕷️ Crawl Analysis\n")
    
    for r in results:
        status = r.crawl_info.get("status", "existing")
        pages = r.crawl_info.get("pages_crawled", r.crawl_info.get("page_count", "?"))
        url = r.crawl_info.get("url", "N/A")
        error = r.crawl_info.get("error", "")
        
        icon = "✅" if pages and pages != "?" and int(str(pages)) > 0 else "❌"
        report_lines.append(f"### {icon} {r.chatbot_name}")
        report_lines.append(f"- **URL:** {url}")
        report_lines.append(f"- **Pages Crawled:** {pages}")
        report_lines.append(f"- **Status:** {status}")
        if error:
            report_lines.append(f"- **Error:** {error}")
        report_lines.append("")
    
    # ============ Detailed Results Per Site ============
    report_lines.append("\n---\n## 📋 Detailed Results Per Site\n")
    
    for r in results:
        report_lines.append(f"### {r.chatbot_name} ({r.category})")
        report_lines.append(f"**Chatbot ID:** `{r.chatbot_id}`\n")
        
        if not r.query_results:
            report_lines.append("_No queries tested (crawl may have failed)_\n")
            continue
        
        report_lines.append("| # | Type | Lang | Query | Score | Products | Sources | Suggestions | Issues |")
        report_lines.append("|---|---|---|---|---|---|---|---|---|")
        
        for i, q in enumerate(r.query_results, 1):
            issues = "; ".join(q["evaluation"]["issues"]) if q["evaluation"]["issues"] else "—"
            sugg = ", ".join(q["suggestions"][:3]) if q["suggestions"] else "—"
            score = q["evaluation"]["score"]
            icon = "🟢" if score >= 7 else "🟡" if score >= 4 else "🔴"
            query_short = q["query"][:50].replace("|", "\\|")
            report_lines.append(
                f"| {i} | {q['type']} | {q['lang']} | {query_short} | {icon} {score}/10 | "
                f"{q['products_count']} | {q['sources_count']} | {sugg[:60]} | {issues[:80]} |"
            )
        
        report_lines.append("")
    
    # ============ Product Display Analysis ============
    report_lines.append("\n---\n## 🛒 Product Display Analysis\n")
    report_lines.append("Analysis of how product cards are returned for product-related queries.\n")
    
    product_query_types = ["product_browse", "specific_product", "price_filter", "color_filter", "complex"]
    
    for r in results:
        product_queries = [q for q in r.query_results if q["type"] in product_query_types]
        if not product_queries:
            continue
        
        report_lines.append(f"### {r.chatbot_name}")
        total_pq = len(product_queries)
        pq_with_products = sum(1 for q in product_queries if q["products_count"] > 0)
        report_lines.append(f"- Product queries: {total_pq}")
        report_lines.append(f"- Queries with product cards: {pq_with_products}/{total_pq} ({100*pq_with_products/max(total_pq,1):.0f}%)")
        
        # Show sample product data
        for q in product_queries:
            if q["products"]:
                report_lines.append(f"\n  **Query:** \"{q['query'][:60]}\"")
                report_lines.append(f"  **Products returned:** {q['products_count']}")
                for p in q["products"][:3]:
                    name = p.get("name", p.get("title", "?"))[:50]
                    price = p.get("price", "N/A")
                    url = p.get("url", "N/A")[:60]
                    report_lines.append(f"  - {name} | Price: {price} | URL: {url}")
        report_lines.append("")
    
    # ============ Suggestions Analysis ============
    report_lines.append("\n---\n## 💡 Suggestions Analysis\n")
    report_lines.append("Evaluation of follow-up suggestions quality.\n")
    
    all_suggestions = []
    with_suggestions = 0
    without_suggestions = 0
    
    for r in results:
        for q in r.query_results:
            if q["type"] not in ["irrelevant", "unsupported_language"]:
                if q["suggestions"]:
                    with_suggestions += 1
                    all_suggestions.extend(q["suggestions"])
                else:
                    without_suggestions += 1
    
    report_lines.append(f"- Queries with suggestions: {with_suggestions}")
    report_lines.append(f"- Queries without suggestions: {without_suggestions}")
    report_lines.append(f"- Suggestion rate: {100*with_suggestions/max(with_suggestions+without_suggestions,1):.0f}%")
    
    if all_suggestions:
        report_lines.append(f"\n**Sample suggestions (first 20):**")
        for s in all_suggestions[:20]:
            report_lines.append(f"  - {s}")
    
    # ============ Issues Summary ============
    report_lines.append("\n---\n## ⚠️ Issues & Failures Summary\n")
    
    all_issues = []
    for r in results:
        for q in r.query_results:
            for issue in q["evaluation"]["issues"]:
                all_issues.append({
                    "site": r.chatbot_name,
                    "type": q["type"],
                    "lang": q["lang"],
                    "query": q["query"][:60],
                    "issue": issue,
                    "error": q.get("error")
                })
    
    if all_issues:
        # Group by issue type
        issue_groups = {}
        for iss in all_issues:
            key = iss["issue"][:50]
            if key not in issue_groups:
                issue_groups[key] = []
            issue_groups[key].append(iss)
        
        report_lines.append(f"**Total issues found:** {len(all_issues)}\n")
        
        for issue_type, items in sorted(issue_groups.items(), key=lambda x: -len(x[1])):
            report_lines.append(f"### {issue_type} ({len(items)} occurrences)")
            report_lines.append("| Site | Query Type | Language | Query |")
            report_lines.append("|---|---|---|---|")
            for item in items[:10]:
                report_lines.append(f"| {item['site']} | {item['type']} | {item['lang']} | {item['query']} |")
            if len(items) > 10:
                report_lines.append(f"| ... | ... | ... | +{len(items)-10} more |")
            report_lines.append("")
    else:
        report_lines.append("No issues found! 🎉\n")
    
    # ============ Recommendations ============
    report_lines.append("\n---\n## 🔧 Recommendations & Improvements\n")
    
    # Analyze patterns
    recommendations = []
    
    # Check irrelevant detection
    irrelevant_scores = [q["evaluation"]["score"] for r in results for q in r.query_results if q["type"] == "irrelevant"]
    if irrelevant_scores and sum(irrelevant_scores)/len(irrelevant_scores) < 6:
        recommendations.append({
            "category": "Irrelevant Query Detection",
            "priority": "HIGH",
            "description": "Bot struggles to identify off-topic queries. It should firmly but politely decline answering questions unrelated to the website's content.",
            "suggestion": "Improve the system prompt's out-of-scope instructions. Add explicit confidence thresholds. When retrieval scores are very low, default to 'this is outside my knowledge' response."
        })
    
    # Check product display
    product_queries_total = sum(1 for r in results for q in r.query_results if q["type"] in product_query_types)
    product_queries_with_cards = sum(1 for r in results for q in r.query_results if q["type"] in product_query_types and q["products_count"] > 0)
    if product_queries_total > 0 and product_queries_with_cards / product_queries_total < 0.5:
        recommendations.append({
            "category": "Product Card Display",
            "priority": "HIGH",
            "description": f"Only {100*product_queries_with_cards/product_queries_total:.0f}% of product queries returned product cards. Product data extraction from crawled content may need improvement.",
            "suggestion": "Review product extraction logic in crawl service. Ensure structured data (JSON-LD, Open Graph) is properly parsed. Consider improving product detection heuristics for non-standard e-commerce site structures."
        })
    
    # Check suggestions
    if with_suggestions + without_suggestions > 0 and with_suggestions / (with_suggestions + without_suggestions) < 0.7:
        recommendations.append({
            "category": "Suggestion Generation",
            "priority": "MEDIUM",
            "description": "Follow-up suggestions are not consistently generated across queries.",
            "suggestion": "Ensure the LLM prompt always requests 3 contextual follow-up suggestions. Add fallback suggestion generation when LLM doesn't include them."
        })
    
    # Check unsupported language
    unsupported_scores = [q["evaluation"]["score"] for r in results for q in r.query_results if q["type"] == "unsupported_language"]
    if unsupported_scores and sum(unsupported_scores)/len(unsupported_scores) < 6:
        recommendations.append({
            "category": "Unsupported Language Handling",
            "priority": "MEDIUM",
            "description": "Bot doesn't consistently reject queries in unsupported languages.",
            "suggestion": "Strengthen language detection. When detected language is not in the chatbot's configured languages list, return a clear message in the user's language + English explaining which languages are supported."
        })
    
    # Check context followup
    followup_scores = [q["evaluation"]["score"] for r in results for q in r.query_results if q["type"] == "context_followup"]
    if followup_scores and sum(followup_scores)/len(followup_scores) < 6:
        recommendations.append({
            "category": "Conversation Context",
            "priority": "MEDIUM",
            "description": "Follow-up queries that reference previous messages aren't handled well.",
            "suggestion": "Review conversation summary generation. Ensure the summary is passed correctly to the LLM. Test that referential queries ('the one I mentioned', 'in a different color') properly leverage conversation history."
        })
    
    # Check non-product queries
    non_product_scores = [q["evaluation"]["score"] for r in results for q in r.query_results if q["type"] == "non_product"]
    if non_product_scores and sum(non_product_scores)/len(non_product_scores) < 5:
        recommendations.append({
            "category": "Non-Product Query Handling",
            "priority": "MEDIUM",
            "description": "Policy queries (return policy, shipping, etc.) have low scores. These pages may not be crawled or the bot is not finding them.",
            "suggestion": "Ensure crawler follows links to /policy, /faq, /shipping, /about pages. These are high-value pages for customer support. Consider prioritizing them during crawl."
        })
    
    # Check crawl failures
    crawl_failures = [r for r in results if r.crawl_info.get("status") == "failed" or r.crawl_info.get("error")]
    if crawl_failures:
        recommendations.append({
            "category": "Crawl Failures",
            "priority": "HIGH",
            "description": f"{len(crawl_failures)} sites had crawl issues: {', '.join(r.chatbot_name for r in crawl_failures)}",
            "suggestion": "Review crawl error handling. Common issues: JS-heavy sites (need headless browser), anti-bot measures (need rate limiting/headers), sitemap.xml not being used as fallback, robots.txt blocking. Consider adding: 1) Automatic sitemap.xml detection, 2) Better user-agent rotation, 3) JavaScript rendering for SPA sites, 4) Clear user warnings about blocked/JS-heavy sites."
        })
    
    # Check Hindi/Gujarati scores vs English
    en_scores = [q["evaluation"]["score"] for r in results for q in r.query_results if q["lang"] == "en"]
    hi_scores = [q["evaluation"]["score"] for r in results for q in r.query_results if q["lang"] in ["hi", "hi_roman"]]
    gu_scores = [q["evaluation"]["score"] for r in results for q in r.query_results if q["lang"] == "gu"]
    
    en_avg = sum(en_scores)/max(len(en_scores),1)
    hi_avg = sum(hi_scores)/max(len(hi_scores),1)
    gu_avg = sum(gu_scores)/max(len(gu_scores),1)
    
    if hi_avg < en_avg - 1.5 or gu_avg < en_avg - 1.5:
        recommendations.append({
            "category": "Multi-Language Performance Gap",
            "priority": "HIGH",
            "description": f"English avg: {en_avg:.1f}, Hindi avg: {hi_avg:.1f}, Gujarati avg: {gu_avg:.1f}. Non-English languages underperform significantly.",
            "suggestion": "1) Improve Hindi/Gujarati query translation quality in the unified LLM call. 2) Ensure embeddings search uses English-translated queries. 3) Add more Hindi/Gujarati few-shot examples. 4) Consider bilingual embedding models for better cross-language retrieval."
        })
    
    # Always add general recommendations
    recommendations.append({
        "category": "General Improvements",
        "priority": "LOW",
        "description": "General observations from testing",
        "suggestion": "1) Add more robust handling for very short queries. 2) Improve response formatting consistency. 3) Add confidence score in API response for debugging. 4) Consider response quality logging for continuous improvement."
    })
    
    for rec in sorted(recommendations, key=lambda x: {"HIGH": 0, "MEDIUM": 1, "LOW": 2}[x["priority"]]):
        priority_icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}[rec["priority"]]
        report_lines.append(f"### {priority_icon} [{rec['priority']}] {rec['category']}")
        report_lines.append(f"**Problem:** {rec['description']}")
        report_lines.append(f"**Suggestion:** {rec['suggestion']}\n")
    
    # ============ Raw Response Samples ============
    report_lines.append("\n---\n## 📝 Sample Responses (First 3 per Type)\n")
    
    shown_types = set()
    for r in results:
        for q in r.query_results:
            type_key = f"{q['type']}"
            if type_key not in shown_types:
                shown_types.add(type_key)
                report_lines.append(f"### {q['type']} — \"{q['query'][:70]}\"")
                report_lines.append(f"**Site:** {r.chatbot_name} | **Lang:** {q['lang']} | **Score:** {q['evaluation']['score']}/10\n")
                response_text = q["response_content"][:400] if q["response_content"] else "(empty)"
                report_lines.append(f"**Response:**\n```\n{response_text}\n```\n")
                if q["suggestions"]:
                    report_lines.append(f"**Suggestions:** {q['suggestions']}\n")
                if q["products"]:
                    report_lines.append(f"**Products:** {len(q['products'])} returned")
                    for p in q["products"][:2]:
                        report_lines.append(f"  - {p.get('name', p.get('title','?'))[:60]} | {p.get('price', 'N/A')}")
                report_lines.append("")
    
    # Write report
    report_content = "\n".join(report_lines)
    report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "CHATBOT_TEST_REPORT.md")
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
    
    print(f"\n    Report saved to: {report_path}")
    
    # Also save raw JSON data
    raw_data = []
    for r in results:
        raw_data.append({
            "chatbot_name": r.chatbot_name,
            "chatbot_id": r.chatbot_id,
            "category": r.category,
            "crawl_info": r.crawl_info,
            "query_results": r.query_results
        })
    
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chatbot_test_raw_data.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(raw_data, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"    Raw data saved to: {json_path}")


if __name__ == "__main__":
    run_tests()
