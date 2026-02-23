"""
Comprehensive Chatbot Testing Script with Multi-GROQ-Key Rotation
=================================================================
- Rotates between 6 GROQ API keys when rate limits are hit
- Tests existing chatbots with diverse query types
- Starts crawling 2-3 new e-commerce sites in parallel
- Generates a comprehensive analysis report
"""

import requests
import json
import time
import sys
import os
import re
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

# ============================================================
# Configuration
# ============================================================
BASE_URL = "http://localhost:8000/api/v1"
EMAIL = "max@gmail.com"
PASSWORD = "12345678"
ENV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")

# All 6 GROQ API keys
GROQ_KEYS = [
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
]

current_key_index = 0
rate_limited_keys = set()  # Track which keys got rate limited
all_keys_exhausted = False
MAX_CRAWL_PAGES = 150
DELAY_BETWEEN_MSGS = 3  # seconds between chat messages
DELAY_AFTER_RATE_LIMIT = 10  # seconds after key switch

# ============================================================
# Existing chatbots
# ============================================================
EXISTING_BOTS = [
    {"id": "182f88cd-02d8-4c94-824d-b41432847400", "name": "ramraj", "url": "https://ramrajcotton.in", "category": "Fashion/Clothing", "pages": 256},
    {"id": "e9f5fd28-cfe1-4456-994e-46aeb154388f", "name": "truff", "url": "https://truff.com", "category": "Food/Condiments", "pages": 262},
    {"id": "1cb18dc0-4909-409d-ab03-0436524fcec4", "name": "kriyanta", "url": "https://www.kriyanta.com", "category": "Tech/Startup", "pages": 803},
    {"id": "868f937e-8559-446d-b7c8-ff630ec7fd79", "name": "kids", "url": "https://www.cheaperzonetoys.com", "category": "Kids/Toys", "pages": 102},
    {"id": "e79b3754-006d-45d5-b21d-2391710e08ca", "name": "zevaramaze", "url": "https://zevaramaze.com", "category": "Jewelry", "pages": 276},
]

# Sites to crawl (pick 3 diverse ones)
SITES_TO_CRAWL = [
    {"name": "Boat Lifestyle", "url": "https://www.boat-lifestyle.com", "category": "Electronics/Audio"},
    {"name": "Sugar Cosmetics", "url": "https://in.sugarcosmetics.com", "category": "Cosmetics"},
    {"name": "Mokobara", "url": "https://www.mokobara.com", "category": "Bags/Luggage"},
]


# ============================================================
# GROQ Key Rotation
# ============================================================
def switch_groq_key() -> bool:
    """Switch to next available GROQ key. Returns False if all exhausted."""
    global current_key_index, all_keys_exhausted
    
    rate_limited_keys.add(current_key_index)
    
    # Find next non-exhausted key
    for i in range(len(GROQ_KEYS)):
        candidate = (current_key_index + 1 + i) % len(GROQ_KEYS)
        if candidate not in rate_limited_keys:
            current_key_index = candidate
            print(f"\n    >>> SWITCHING TO GROQ KEY #{candidate+1}/{len(GROQ_KEYS)} <<<")
            _update_env_and_restart()
            return True
    
    # All keys exhausted
    all_keys_exhausted = True
    print(f"\n    >>> ALL {len(GROQ_KEYS)} GROQ KEYS EXHAUSTED <<<")
    return False


def _update_env_and_restart():
    """Update .env with new GROQ key and restart docker API."""
    new_key = GROQ_KEYS[current_key_index]
    
    # Read current .env
    with open(ENV_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Replace the active GROQ_API_KEY line
    # Match the line starting with GROQ_API_KEY (not commented)
    content = re.sub(
        r'^GROQ_API_KEY\s*=\s*.*$',
        f'GROQ_API_KEY ={new_key}',
        content,
        flags=re.MULTILINE
    )
    
    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"    Updated .env with key #{current_key_index+1}: ...{new_key[-8:]}")
    
    # Restart docker API
    print(f"    Restarting docker API container...")
    try:
        subprocess.run(
            ["docker-compose", "up", "-d", "api"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            capture_output=True, text=True, timeout=60
        )
    except Exception as e:
        print(f"    Warning: docker restart issue: {e}")
    
    # Wait for API to be ready
    print(f"    Waiting for API to be ready...")
    for attempt in range(20):
        try:
            resp = requests.get(f"{BASE_URL}/health", timeout=5)
            if resp.status_code == 200:
                print(f"    API ready after {(attempt+1)*3}s")
                return
        except:
            pass
        time.sleep(3)
    
    # Fallback: try login endpoint
    for attempt in range(10):
        try:
            resp = requests.post(
                f"{BASE_URL}/auth/login",
                json={"email": EMAIL, "password": PASSWORD},
                timeout=10
            )
            if resp.status_code in [200, 401, 422]:
                print(f"    API ready (confirmed via login endpoint)")
                return
        except:
            pass
        time.sleep(3)
    
    print(f"    Warning: API may not be fully ready, continuing anyway...")


# ============================================================
# API Helpers
# ============================================================
def login() -> str:
    for attempt in range(5):
        try:
            resp = requests.post(
                f"{BASE_URL}/auth/login",
                json={"email": EMAIL, "password": PASSWORD},
                timeout=30
            )
            resp.raise_for_status()
            return resp.json()["access_token"]
        except Exception as e:
            if attempt < 4:
                time.sleep(5)
            else:
                raise


def get_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def list_chatbots(token: str) -> List[Dict]:
    resp = requests.get(f"{BASE_URL}/chatbots", headers=get_headers(token), timeout=30)
    resp.raise_for_status()
    return resp.json()["chatbots"]


def create_chatbot(token: str, name: str) -> Dict:
    resp = requests.post(f"{BASE_URL}/chatbots", headers=get_headers(token), json={"name": name}, timeout=30)
    resp.raise_for_status()
    return resp.json()


def start_crawl(token: str, chatbot_id: str, url: str) -> Dict:
    resp = requests.post(
        f"{BASE_URL}/chatbots/{chatbot_id}/crawl",
        headers=get_headers(token),
        json={"base_url": url},
        timeout=30
    )
    resp.raise_for_status()
    return resp.json()


def get_knowledge_sources(token: str, chatbot_id: str) -> List:
    resp = requests.get(f"{BASE_URL}/chatbots/{chatbot_id}/knowledge-sources", headers=get_headers(token), timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        return data.get("sources", data.get("items", [data] if "id" in data else []))
    return []


def get_crawl_status(token: str, source_id: str) -> Dict:
    resp = requests.get(
        f"{BASE_URL}/chatbots/knowledge-sources/{source_id}/status",
        headers=get_headers(token), timeout=30
    )
    resp.raise_for_status()
    return resp.json()


def stop_crawl(token: str, source_id: str) -> Dict:
    resp = requests.post(
        f"{BASE_URL}/chatbots/knowledge-sources/{source_id}/stop",
        headers=get_headers(token), timeout=30
    )
    resp.raise_for_status()
    return resp.json()


def send_chat_message(chatbot_id: str, message: str, session_id: Optional[str] = None) -> Dict:
    """Send message via SSE stream and collect full response. Detects rate limits."""
    data = {"message": message}
    if session_id:
        data["session_id"] = session_id
    
    result = {
        "content": "",
        "sources": [],
        "suggestions": [],
        "products": [],
        "session_id": None,
        "error": None,
        "status_messages": [],
        "raw_events": [],
        "is_rate_limited": False,
    }
    
    try:
        resp = requests.post(
            f"{BASE_URL}/chat/{chatbot_id}/message/stream",
            data=data,
            stream=True,
            timeout=90
        )
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        result["error"] = str(e)
        return result
    
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
                    elif event.get("type") == "error":
                        result["error"] = event.get("error", "Unknown error")
                except json.JSONDecodeError:
                    pass
    except Exception as e:
        result["error"] = f"Stream error: {str(e)}"
    
    # Detect rate limiting in response
    rate_limit_phrases = [
        "rate limit", "too many requests", "try again in a few minutes",
        "getting a lot of requests", "rate_limit_exceeded", "429",
        "please try again", "lot of requests right now"
    ]
    full_text = (result["content"] + " " + str(result.get("error", ""))).lower()
    if any(phrase in full_text for phrase in rate_limit_phrases):
        result["is_rate_limited"] = True
    
    return result


# ============================================================
# Query Templates
# ============================================================
def get_queries_for_bot(bot_name: str, category: str) -> List[Dict]:
    """Generate diverse queries tailored to each bot's content."""
    
    queries = []
    
    # Category-specific product terms
    product_map = {
        "Fashion/Clothing": {"products": ["shirts", "dhotis", "cotton shirts", "formal shirts"], "brand_items": "cotton clothing and traditional wear"},
        "Food/Condiments": {"products": ["hot sauce", "truffle sauce", "pasta sauce", "condiments"], "brand_items": "premium sauces and condiments"},
        "Tech/Startup": {"products": ["services", "solutions", "portfolio", "projects"], "brand_items": "technology services"},
        "Kids/Toys": {"products": ["toys", "board games", "action figures", "puzzles"], "brand_items": "kids toys and games"},
        "Jewelry": {"products": ["bracelets", "necklaces", "rings", "earrings"], "brand_items": "jewelry and accessories"},
        "Electronics/Audio": {"products": ["earbuds", "headphones", "speakers", "smartwatches"], "brand_items": "audio products and wearables"},
        "Cosmetics": {"products": ["lipstick", "foundation", "mascara", "nail polish"], "brand_items": "cosmetics and beauty products"},
        "Bags/Luggage": {"products": ["backpacks", "luggage", "laptop bags", "travel bags"], "brand_items": "bags and luggage"},
    }
    
    pdata = product_map.get(category, {"products": ["products", "items", "goods", "offerings"], "brand_items": "products"})
    p = pdata["products"]
    brand_desc = pdata["brand_items"]
    
    # ===== TYPE 1: Greeting =====
    queries.append({"type": "greeting", "lang": "en", "text": "Hi there! What can you help me with?"})
    queries.append({"type": "greeting", "lang": "hi", "text": "नमस्ते! आप मेरी कैसे मदद कर सकते हैं?"})
    queries.append({"type": "greeting", "lang": "hi_roman", "text": "hello bhai, kya help kar sakte ho?"})
    
    # ===== TYPE 2: General Product Browsing =====
    queries.append({"type": "product_browse", "lang": "en", "text": f"Show me your best {p[0]}"})
    queries.append({"type": "product_browse", "lang": "en", "text": f"What {p[1]} do you have available?"})
    queries.append({"type": "product_browse", "lang": "hi", "text": f"आपके पास कौन से {p[0]} उपलब्ध हैं?"})
    queries.append({"type": "product_browse", "lang": "gu", "text": f"તમારી પાસે કયા {p[0]} છે?"})
    
    # ===== TYPE 3: Specific Product Search =====
    queries.append({"type": "specific_product", "lang": "en", "text": f"I'm looking for a black {p[0]}"})
    queries.append({"type": "specific_product", "lang": "en", "text": f"Do you have any premium {p[2] if len(p) > 2 else p[0]}?"})
    queries.append({"type": "specific_product", "lang": "hi", "text": f"मुझे {p[0]} चाहिए जो बहुत अच्छी क्वालिटी का हो"})
    queries.append({"type": "specific_product", "lang": "hi_roman", "text": f"best quality {p[0]} dikhao"})
    
    # ===== TYPE 4: Price Queries =====
    queries.append({"type": "price_query", "lang": "en", "text": f"Show me {p[0]} under ₹500"})
    queries.append({"type": "price_query", "lang": "en", "text": f"What's the price range for your {p[1]}?"})
    queries.append({"type": "price_query", "lang": "hi", "text": f"500 रुपये से कम के {p[0]} बताओ"})
    queries.append({"type": "price_query", "lang": "gu", "text": f"₹1000 થી ઓછા {p[0]} બતાવો"})
    
    # ===== TYPE 5: Non-Product Queries (policies, shipping etc.) =====
    queries.append({"type": "non_product", "lang": "en", "text": "What is your return policy?"})
    queries.append({"type": "non_product", "lang": "en", "text": "How long does shipping take?"})
    queries.append({"type": "non_product", "lang": "en", "text": "Do you offer cash on delivery?"})
    queries.append({"type": "non_product", "lang": "hi", "text": "रिटर्न पॉलिसी क्या है?"})
    
    # ===== TYPE 6: Irrelevant (should be rejected) =====
    queries.append({"type": "irrelevant", "lang": "en", "text": "What is the capital of France?"})
    queries.append({"type": "irrelevant", "lang": "en", "text": "Can you write me a Python script to sort a list?"})
    queries.append({"type": "irrelevant", "lang": "hi", "text": "भारत का प्रधानमंत्री कौन है?"})
    queries.append({"type": "irrelevant", "lang": "en", "text": "What's the weather like in Tokyo today?"})
    
    # ===== TYPE 7: Missing Info / Ambiguous =====
    queries.append({"type": "ambiguous", "lang": "en", "text": "I want something nice for a gift"})
    queries.append({"type": "ambiguous", "lang": "en", "text": "What do you recommend for someone new here?"})
    queries.append({"type": "ambiguous", "lang": "hi", "text": "कुछ अच्छा बताओ ना"})
    
    # ===== TYPE 8: Complex Multi-Intent =====
    queries.append({"type": "complex", "lang": "en", "text": f"I need a gift for my sister, she likes {p[0]} in red or blue, budget around ₹1500, and also tell me about your return policy"})
    queries.append({"type": "complex", "lang": "hi", "text": f"मेरी बहन के लिए {p[0]} चाहिए, लाल या नीला रंग, 2000 रुपये से कम, और delivery कितने दिन में होगी?"})
    
    # ===== TYPE 9: Conversation Context / Follow-up (sequential - must keep session) =====
    queries.append({"type": "context_start", "lang": "en", "text": f"Show me your most popular {p[0]}"})
    queries.append({"type": "context_followup", "lang": "en", "text": "Do you have this in a different color?"})
    queries.append({"type": "context_followup", "lang": "en", "text": "What about a larger size?"})
    queries.append({"type": "context_summary", "lang": "en", "text": "Can you summarize what we've talked about so far?"})
    
    # ===== TYPE 10: About the Brand =====
    queries.append({"type": "about_brand", "lang": "en", "text": f"Tell me about {bot_name} and what you sell"})
    queries.append({"type": "about_brand", "lang": "hi", "text": f"{bot_name} के बारे में बताओ"})
    
    # ===== TYPE 11: Unsupported Language =====
    queries.append({"type": "unsupported_lang", "lang": "fr", "text": "Bonjour, montrez-moi vos produits les plus populaires"})
    queries.append({"type": "unsupported_lang", "lang": "ja", "text": "こんにちは、人気商品を教えてください"})
    
    # ===== TYPE 12: Suggestions Quality =====
    queries.append({"type": "suggestions_test", "lang": "en", "text": "I'm new here, what kind of things do you sell?"})
    queries.append({"type": "suggestions_test", "lang": "hi", "text": "यहां क्या-क्या मिलता है?"})
    
    # ===== TYPE 13: Comparison Query =====
    queries.append({"type": "comparison", "lang": "en", "text": f"What's the difference between your cheapest and most expensive {p[0]}?"})
    
    # ===== TYPE 14: Size/Variant Query =====
    queries.append({"type": "variant_query", "lang": "en", "text": f"Do you have {p[0]} in size L or XL?"})
    queries.append({"type": "variant_query", "lang": "hi_roman", "text": f"{p[0]} mein kya sizes available hain?"})
    
    # ===== TYPE 15: Urgency/Emotional Query =====
    queries.append({"type": "urgency", "lang": "en", "text": f"I need {p[0]} urgently for tomorrow, can you deliver that fast?"})
    
    # ===== TYPE 16: Negative/Complaint Query =====
    queries.append({"type": "complaint", "lang": "en", "text": f"I received a damaged {p[0]}, what should I do?"})
    
    return queries


# ============================================================
# Response Evaluation
# ============================================================
def evaluate_response(query_type: str, response: Dict, lang: str, bot_category: str) -> Dict:
    """Evaluate response quality based on query type."""
    ev = {
        "score": 0,
        "max_score": 10,
        "issues": [],
        "passed": True,
        "notes": "",
    }
    
    content = response.get("content", "").strip()
    error = response.get("error")
    sources = response.get("sources", [])
    products = response.get("products", [])
    suggestions = response.get("suggestions", [])
    is_rate_limited = response.get("is_rate_limited", False)
    
    # Rate limit is not a bot quality issue
    if is_rate_limited:
        ev["score"] = -1  # Special marker: skip from scoring
        ev["issues"].append("RATE_LIMITED")
        ev["notes"] = "Skipped - rate limit hit"
        return ev
    
    if error:
        ev["score"] = 0
        ev["passed"] = False
        ev["issues"].append(f"ERROR: {error}")
        return ev
    
    if not content:
        ev["score"] = 0
        ev["passed"] = False
        ev["issues"].append("Empty response")
        return ev
    
    # Type-specific evaluation
    if query_type == "greeting":
        if len(content) > 20:
            ev["score"] = 8
        else:
            ev["score"] = 5
            ev["issues"].append("Short greeting")
        if suggestions:
            ev["score"] = min(10, ev["score"] + 1)
            ev["notes"] = f"Suggestions: {suggestions[:3]}"
    
    elif query_type in ["product_browse", "specific_product"]:
        if products:
            ev["score"] = 9
            ev["notes"] = f"{len(products)} products returned"
            # Check product data quality
            good_products = sum(1 for p in products if p.get("name") and p.get("url"))
            if good_products == len(products):
                ev["score"] = 10
                ev["notes"] += " (all have name+url)"
        elif sources:
            ev["score"] = 5
            ev["issues"].append("Sources found but no product cards")
        else:
            ev["score"] = 2
            ev["passed"] = False
            ev["issues"].append("No products/sources for product query")
    
    elif query_type == "price_query":
        if products:
            has_prices = sum(1 for p in products if p.get("price"))
            if has_prices:
                ev["score"] = 9
                ev["notes"] = f"{len(products)} products, {has_prices} with prices"
            else:
                ev["score"] = 6
                ev["issues"].append("Products returned but without price data")
        elif "price" in content.lower() or "₹" in content or "rs" in content.lower():
            ev["score"] = 5
            ev["notes"] = "Price mentioned in text but no product cards"
        else:
            ev["score"] = 2
            ev["passed"] = False
            ev["issues"].append("No price info for price query")
    
    elif query_type == "non_product":
        if sources:
            ev["score"] = 8
            ev["notes"] = f"Found {len(sources)} relevant sources"
        elif any(kw in content.lower() for kw in ["return", "shipping", "delivery", "policy", "refund", "cash on delivery", "cod"]):
            ev["score"] = 6
            ev["notes"] = "Relevant info in text, no source citations"
        elif "sorry" in content.lower() or "don't have" in content.lower() or "currently" in content.lower():
            ev["score"] = 4
            ev["notes"] = "Bot acknowledged lack of info"
        else:
            ev["score"] = 3
            ev["issues"].append("Poor non-product response")
    
    elif query_type == "irrelevant":
        rejection_markers = [
            "not related", "can't help", "outside", "scope", "don't have",
            "sorry", "cannot", "not able", "beyond", "irrelevant", "unrelated",
            "assist with", "not something", "IRRELEVANT", "MISSING",
            "not relevant", "out of scope", "unable to help", "only help with",
            "only assist", "specifically", "related to"
        ]
        is_rejected = any(m.lower() in content.lower() for m in rejection_markers)
        if is_rejected:
            ev["score"] = 9
            ev["notes"] = "Correctly identified as irrelevant"
        else:
            ev["score"] = 1
            ev["passed"] = False
            ev["issues"].append("FAILED to detect irrelevant query - bot tried to answer")
    
    elif query_type == "ambiguous":
        if suggestions and len(suggestions) >= 2:
            ev["score"] = 8
            ev["notes"] = f"Good suggestions for ambiguous query: {suggestions[:3]}"
        elif "recommend" in content.lower() or "suggest" in content.lower() or "popular" in content.lower():
            ev["score"] = 6
            ev["notes"] = "Provided recommendations"
        else:
            ev["score"] = 4
            ev["issues"].append("Could give better guidance for ambiguous query")
    
    elif query_type == "complex":
        addressed_aspects = 0
        if products:
            addressed_aspects += 1
        if any(kw in content.lower() for kw in ["return", "delivery", "shipping", "policy"]):
            addressed_aspects += 1
        if any(kw in content.lower() for kw in ["red", "blue", "color", "colour", "लाल", "नीला"]):
            addressed_aspects += 1
        if any(kw in content.lower() for kw in ["₹", "rs", "rupee", "price", "budget", "रुपये"]):
            addressed_aspects += 1
        
        ev["score"] = min(10, 3 + addressed_aspects * 2)
        ev["notes"] = f"Addressed {addressed_aspects}/4 aspects of complex query"
        if addressed_aspects < 2:
            ev["issues"].append("Failed to handle multi-intent complex query fully")
    
    elif query_type in ["context_start", "context_followup", "context_summary"]:
        if content and len(content) > 30:
            ev["score"] = 7
            if query_type == "context_summary" and any(kw in content.lower() for kw in ["discussed", "talked", "summary", "conversation", "asked", "showed"]):
                ev["score"] = 9
                ev["notes"] = "Good conversation summary"
            elif query_type == "context_summary":
                ev["score"] = 5
                ev["issues"].append("Summary doesn't reference earlier conversation")
            elif query_type == "context_followup":
                ev["notes"] = "Follow-up handled"
        else:
            ev["score"] = 3
            ev["issues"].append(f"Poor {query_type} handling")
    
    elif query_type == "about_brand":
        if len(content) > 50 and (sources or any(kw in content.lower() for kw in ["about", "founded", "brand", "company", "sell", "offer"])):
            ev["score"] = 8
            ev["notes"] = "Good brand info"
        elif len(content) > 30:
            ev["score"] = 5
            ev["notes"] = "Some brand info"
        else:
            ev["score"] = 2
            ev["issues"].append("No brand information found")
    
    elif query_type == "unsupported_lang":
        rejection_markers = ["support", "language", "sorry", "english", "hindi", "gujarati",
                             "not support", "available in", "only", "can help in", "communicate"]
        detected = any(m.lower() in content.lower() for m in rejection_markers)
        if detected:
            ev["score"] = 8
            ev["notes"] = "Detected unsupported language"
        elif content and len(content) > 20:
            # It responded anyway - check if it responded in the unsupported language or English
            ev["score"] = 4
            ev["notes"] = "Responded but didn't warn about unsupported language"
            ev["issues"].append("No warning about unsupported language")
        else:
            ev["score"] = 2
            ev["issues"].append("Poor handling of unsupported language")
    
    elif query_type == "suggestions_test":
        if suggestions and len(suggestions) >= 3:
            ev["score"] = 9
            ev["notes"] = f"Great suggestions: {suggestions}"
        elif suggestions and len(suggestions) >= 1:
            ev["score"] = 6
            ev["notes"] = f"Some suggestions: {suggestions}"
        else:
            ev["score"] = 3
            ev["issues"].append("No suggestions generated")
    
    elif query_type == "comparison":
        if products and len(products) >= 2:
            ev["score"] = 9
            ev["notes"] = f"Comparison with {len(products)} products"
        elif "cheapest" in content.lower() or "expensive" in content.lower() or "difference" in content.lower():
            ev["score"] = 6
            ev["notes"] = "Comparison discussed in text"
        else:
            ev["score"] = 3
            ev["issues"].append("Poor comparison handling")
    
    elif query_type == "variant_query":
        if any(kw in content.lower() for kw in ["size", "l", "xl", "m", "available", "variant", "option"]):
            ev["score"] = 7
            ev["notes"] = "Size/variant info provided"
        else:
            ev["score"] = 3
            ev["issues"].append("No size/variant info")
    
    elif query_type == "urgency":
        if any(kw in content.lower() for kw in ["delivery", "shipping", "express", "urgent", "fast", "next day", "tomorrow"]):
            ev["score"] = 7
            ev["notes"] = "Addressed urgency"
        else:
            ev["score"] = 3
            ev["issues"].append("Didn't address urgency/delivery speed")
    
    elif query_type == "complaint":
        if any(kw in content.lower() for kw in ["sorry", "return", "refund", "exchange", "contact", "help", "support", "damaged"]):
            ev["score"] = 8
            ev["notes"] = "Good complaint handling"
        else:
            ev["score"] = 3
            ev["issues"].append("Poor complaint/damage handling")
    
    # Bonus for suggestions (when appropriate)
    if suggestions and query_type not in ["irrelevant", "unsupported_lang"]:
        ev["score"] = min(10, ev["score"] + 0.5)
    
    # Check for "undefined" bug
    if "undefined" in content:
        ev["issues"].append("Contains 'undefined' text")
        ev["score"] = max(0, ev["score"] - 2)
    
    if ev["score"] < 4:
        ev["passed"] = False
    
    return ev


# ============================================================
# Test Result Tracking
# ============================================================
class BotTestResult:
    def __init__(self, name: str, bot_id: str, category: str, url: str, pages: int):
        self.name = name
        self.bot_id = bot_id
        self.category = category
        self.url = url
        self.pages = pages
        self.query_results = []
        self.crawl_info = {}
    
    def add_query(self, qtype: str, lang: str, text: str, response: Dict, evaluation: Dict):
        self.query_results.append({
            "type": qtype,
            "lang": lang,
            "query": text,
            "response_content": response.get("content", "")[:600],
            "sources_count": len(response.get("sources", [])),
            "products_count": len(response.get("products", [])),
            "suggestions": response.get("suggestions", []),
            "products": response.get("products", [])[:5],
            "error": response.get("error"),
            "is_rate_limited": response.get("is_rate_limited", False),
            "status_messages": response.get("status_messages", []),
            "evaluation": evaluation,
        })


# ============================================================
# Main Test Runner
# ============================================================
def run_tests():
    global all_keys_exhausted
    
    print("=" * 80)
    print("  COMPREHENSIVE CHATBOT TESTING WITH MULTI-KEY ROTATION")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  GROQ Keys Available: {len(GROQ_KEYS)}")
    print("=" * 80)
    
    # Step 1: Login
    print("\n[STEP 1] Logging in...")
    token = login()
    print(f"  Logged in as {EMAIL}")
    
    all_results: List[BotTestResult] = []
    crawl_tracking = []
    
    # Step 2: Start crawling new sites (run in background while testing existing)
    print(f"\n[STEP 2] Starting crawls for {len(SITES_TO_CRAWL)} new sites...")
    for site in SITES_TO_CRAWL:
        try:
            # Check if chatbot already exists
            bots = list_chatbots(token)
            existing = [b for b in bots if site["name"].lower().replace(" ", "") in b["name"].lower().replace(" ", "")]
            
            if existing:
                bot_id = existing[0]["id"]
                print(f"  {site['name']}: Already exists ({bot_id})")
                # Check if already has pages
                ks = get_knowledge_sources(token, bot_id)
                has_pages = False
                for s in (ks if isinstance(ks, list) else []):
                    pc = s.get("pages_found", 0)
                    if pc and pc > 0:
                        has_pages = True
                        print(f"    Already has {pc} pages, skipping crawl")
                        break
                if has_pages:
                    continue
            else:
                bot = create_chatbot(token, f"Test-{site['name']}")
                bot_id = bot["id"]
                print(f"  {site['name']}: Created chatbot ({bot_id})")
            
            # Start crawl
            crawl_resp = start_crawl(token, bot_id, site["url"])
            source_id = crawl_resp.get("id") or crawl_resp.get("source_id") or crawl_resp.get("knowledge_source_id")
            
            if not source_id:
                ks = get_knowledge_sources(token, bot_id)
                if isinstance(ks, list) and ks:
                    source_id = ks[-1].get("id")
            
            if source_id:
                print(f"  {site['name']}: Crawl started (source: {source_id})")
                crawl_tracking.append({
                    "bot_id": bot_id,
                    "source_id": source_id,
                    "site": site,
                })
            else:
                print(f"  {site['name']}: Could not get source ID")
        except Exception as e:
            print(f"  {site['name']}: Error - {e}")
    
    # Step 3: Test existing chatbots while crawls run in background
    print(f"\n[STEP 3] Testing {len(EXISTING_BOTS)} existing chatbots...")
    
    for bot_info in EXISTING_BOTS:
        if all_keys_exhausted:
            print(f"\n  ALL KEYS EXHAUSTED - stopping tests")
            break
        
        print(f"\n  {'='*60}")
        print(f"  TESTING: {bot_info['name']} ({bot_info['category']})")
        print(f"  URL: {bot_info['url']} | Pages: {bot_info['pages']}")
        print(f"  {'='*60}")
        
        result = BotTestResult(
            bot_info["name"], bot_info["id"],
            bot_info["category"], bot_info["url"], bot_info["pages"]
        )
        
        queries = get_queries_for_bot(bot_info["name"], bot_info["category"])
        session_id = None
        consecutive_rate_limits = 0
        
        for q in queries:
            if all_keys_exhausted:
                break
            
            # Maintain session for context queries
            use_session = None
            if q["type"] in ["context_followup", "context_summary"]:
                use_session = session_id
            elif q["type"] == "context_start":
                session_id = None  # Reset session for new context chain
            
            print(f"    [{q['type']}][{q['lang']}] {q['text'][:55]}...", end="", flush=True)
            
            resp = send_chat_message(bot_info["id"], q["text"], use_session)
            
            # Track session
            if resp.get("session_id"):
                if q["type"] == "context_start":
                    session_id = resp["session_id"]
                elif q["type"] in ["context_followup", "context_summary"] and not session_id:
                    session_id = resp["session_id"]
            
            # Handle rate limiting
            if resp.get("is_rate_limited"):
                consecutive_rate_limits += 1
                print(f" [RATE LIMITED key#{current_key_index+1}]")
                
                if consecutive_rate_limits >= 2:
                    # Try switching key
                    if not switch_groq_key():
                        # All keys exhausted
                        evaluation = evaluate_response(q["type"], resp, q["lang"], bot_info["category"])
                        result.add_query(q["type"], q["lang"], q["text"], resp, evaluation)
                        break
                    
                    # Re-login after restart
                    try:
                        token = login()
                    except:
                        time.sleep(10)
                        token = login()
                    
                    consecutive_rate_limits = 0
                    
                    # Retry current query with new key
                    print(f"    [{q['type']}][{q['lang']}] RETRY: {q['text'][:45]}...", end="", flush=True)
                    resp = send_chat_message(bot_info["id"], q["text"], use_session)
                    
                    if resp.get("is_rate_limited"):
                        print(f" [STILL RATE LIMITED]")
                    elif resp.get("error"):
                        print(f" [ERROR]")
                    else:
                        consecutive_rate_limits = 0
                        score = evaluate_response(q["type"], resp, q["lang"], bot_info["category"])["score"]
                        icon = "+" if score >= 5 else "-"
                        print(f" [{icon} {score}/10]")
                else:
                    time.sleep(DELAY_AFTER_RATE_LIMIT)
            else:
                consecutive_rate_limits = 0
                evaluation = evaluate_response(q["type"], resp, q["lang"], bot_info["category"])
                score = evaluation["score"]
                icon = "+" if score >= 5 else "-"
                print(f" [{icon} {score}/10]")
            
            evaluation = evaluate_response(q["type"], resp, q["lang"], bot_info["category"])
            result.add_query(q["type"], q["lang"], q["text"], resp, evaluation)
            
            time.sleep(DELAY_BETWEEN_MSGS)
        
        all_results.append(result)
        
        # Save intermediate results
        _save_intermediate(all_results)
        print(f"\n  Completed {bot_info['name']}: {len(result.query_results)} queries tested")
    
    # Step 4: Check crawl status and stop at ~150 pages
    if crawl_tracking and not all_keys_exhausted:
        print(f"\n[STEP 4] Checking crawl status for {len(crawl_tracking)} sites...")
        
        for ct in crawl_tracking:
            try:
                status = get_crawl_status(token, ct["source_id"])
                pages = status.get("pages_crawled", status.get("pages_found", 0))
                cs = status.get("status", "unknown")
                print(f"  {ct['site']['name']}: {pages} pages, status={cs}")
                
                if pages >= MAX_CRAWL_PAGES and cs not in ["completed", "failed", "stopped"]:
                    print(f"    -> Stopping crawl at {pages} pages")
                    try:
                        stop_crawl(token, ct["source_id"])
                    except:
                        pass
                
                ct["pages"] = pages
                ct["status"] = cs
            except Exception as e:
                print(f"  {ct['site']['name']}: Error checking - {e}")
                ct["pages"] = 0
                ct["status"] = "error"
        
        # Wait a bit more for active crawls
        active = [ct for ct in crawl_tracking if ct.get("status") not in ["completed", "failed", "stopped", "error"]]
        if active:
            print(f"\n  Waiting for {len(active)} active crawls (max 3 min)...")
            for wait_round in range(12):  # Max 12*15 = 180s = 3min
                time.sleep(15)
                still_active = False
                for ct in active:
                    try:
                        status = get_crawl_status(token, ct["source_id"])
                        pages = status.get("pages_crawled", status.get("pages_found", 0))
                        cs = status.get("status", "unknown")
                        ct["pages"] = pages
                        ct["status"] = cs
                        print(f"    {ct['site']['name']}: {pages} pages ({cs})")
                        
                        if pages >= MAX_CRAWL_PAGES and cs not in ["completed", "failed", "stopped"]:
                            try:
                                stop_crawl(token, ct["source_id"])
                                ct["status"] = "stopped"
                            except:
                                pass
                        
                        if cs not in ["completed", "failed", "stopped"]:
                            still_active = True
                    except:
                        pass
                
                if not still_active:
                    print("  All crawls finished!")
                    break
    
    # Step 5: Test newly crawled chatbots
    if crawl_tracking and not all_keys_exhausted:
        print(f"\n[STEP 5] Testing newly crawled chatbots...")
        
        for ct in crawl_tracking:
            if all_keys_exhausted:
                break
            
            pages = ct.get("pages", 0)
            if pages == 0:
                print(f"\n  Skipping {ct['site']['name']} - no pages crawled")
                continue
            
            site = ct["site"]
            print(f"\n  {'='*60}")
            print(f"  TESTING: {site['name']} ({site['category']})")
            print(f"  URL: {site['url']} | Pages: {pages}")
            print(f"  {'='*60}")
            
            result = BotTestResult(site["name"], ct["bot_id"], site["category"], site["url"], pages)
            queries = get_queries_for_bot(site["name"], site["category"])
            session_id = None
            consecutive_rate_limits = 0
            
            for q in queries:
                if all_keys_exhausted:
                    break
                
                use_session = None
                if q["type"] in ["context_followup", "context_summary"]:
                    use_session = session_id
                elif q["type"] == "context_start":
                    session_id = None
                
                print(f"    [{q['type']}][{q['lang']}] {q['text'][:55]}...", end="", flush=True)
                
                resp = send_chat_message(ct["bot_id"], q["text"], use_session)
                
                if resp.get("session_id"):
                    if q["type"] == "context_start":
                        session_id = resp["session_id"]
                    elif not session_id:
                        session_id = resp["session_id"]
                
                if resp.get("is_rate_limited"):
                    consecutive_rate_limits += 1
                    print(f" [RATE LIMITED]")
                    
                    if consecutive_rate_limits >= 2:
                        if not switch_groq_key():
                            evaluation = evaluate_response(q["type"], resp, q["lang"], site["category"])
                            result.add_query(q["type"], q["lang"], q["text"], resp, evaluation)
                            break
                        try:
                            token = login()
                        except:
                            time.sleep(10)
                            token = login()
                        consecutive_rate_limits = 0
                        
                        print(f"    [{q['type']}][{q['lang']}] RETRY...", end="", flush=True)
                        resp = send_chat_message(ct["bot_id"], q["text"], use_session)
                        if not resp.get("is_rate_limited"):
                            consecutive_rate_limits = 0
                    else:
                        time.sleep(DELAY_AFTER_RATE_LIMIT)
                else:
                    consecutive_rate_limits = 0
                
                evaluation = evaluate_response(q["type"], resp, q["lang"], site["category"])
                result.add_query(q["type"], q["lang"], q["text"], resp, evaluation)
                
                score = evaluation["score"]
                if score >= 0:
                    icon = "+" if score >= 5 else "-"
                    if not resp.get("is_rate_limited"):
                        pass  # Already printed
                
                time.sleep(DELAY_BETWEEN_MSGS)
            
            all_results.append(result)
            _save_intermediate(all_results)
    
    # Step 6: Generate report
    print(f"\n[STEP 6] Generating analysis report...")
    generate_report(all_results, crawl_tracking)
    
    print("\n" + "=" * 80)
    print("  TESTING COMPLETE!")
    print(f"  Total bots tested: {len(all_results)}")
    total_qs = sum(len(r.query_results) for r in all_results)
    print(f"  Total queries: {total_qs}")
    print(f"  Keys used: {current_key_index + 1}/{len(GROQ_KEYS)}")
    print(f"  Keys exhausted: {len(rate_limited_keys)}")
    print("=" * 80)


def _save_intermediate(results: List[BotTestResult]):
    """Save intermediate results to JSON."""
    try:
        data = []
        for r in results:
            data.append({
                "name": r.name, "bot_id": r.bot_id, "category": r.category,
                "url": r.url, "pages": r.pages,
                "query_results": r.query_results,
            })
        with open("chatbot_test_intermediate.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except:
        pass


# ============================================================
# Report Generation
# ============================================================
def generate_report(results: List[BotTestResult], crawl_tracking: List[Dict]):
    """Generate comprehensive Markdown analysis report."""
    
    lines = []
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Filter out rate-limited queries for scoring
    def valid_queries(result):
        return [q for q in result.query_results if q["evaluation"]["score"] >= 0]
    
    total_valid = sum(len(valid_queries(r)) for r in results)
    total_rate_limited = sum(1 for r in results for q in r.query_results if q.get("is_rate_limited"))
    total_passed = sum(1 for r in results for q in valid_queries(r) if q["evaluation"]["passed"])
    total_failed = total_valid - total_passed
    all_scores = [q["evaluation"]["score"] for r in results for q in valid_queries(r)]
    avg_score = sum(all_scores) / max(len(all_scores), 1)
    
    lines.append("# Comprehensive Chatbot Testing Report")
    lines.append(f"\n**Generated:** {ts}")
    lines.append(f"**Total Sites Tested:** {len(results)}")
    lines.append(f"**Total Queries Sent:** {sum(len(r.query_results) for r in results)}")
    lines.append(f"**Valid Queries (non rate-limited):** {total_valid}")
    lines.append(f"**Rate-Limited Queries (skipped):** {total_rate_limited}")
    lines.append(f"**Pass Rate:** {total_passed}/{total_valid} ({100*total_passed/max(total_valid,1):.1f}%)")
    lines.append(f"**Fail Rate:** {total_failed}/{total_valid} ({100*total_failed/max(total_valid,1):.1f}%)")
    lines.append(f"**Average Score:** {avg_score:.1f}/10")
    lines.append(f"**GROQ Keys Used:** {current_key_index+1} of {len(GROQ_KEYS)}")
    lines.append(f"**Keys Exhausted:** {len(rate_limited_keys)}")
    
    # ============ EXECUTIVE SUMMARY ============
    lines.append("\n---\n## Executive Summary\n")
    
    # Score by Query Type
    lines.append("### Scores by Query Type\n")
    lines.append("| Query Type | Avg Score | Pass Rate | Tested | Status |")
    lines.append("|---|---|---|---|---|")
    
    type_data = {}
    for r in results:
        for q in valid_queries(r):
            qt = q["type"]
            if qt not in type_data:
                type_data[qt] = {"scores": [], "passed": 0}
            type_data[qt]["scores"].append(q["evaluation"]["score"])
            if q["evaluation"]["passed"]:
                type_data[qt]["passed"] += 1
    
    for qt in sorted(type_data.keys(), key=lambda x: sum(type_data[x]["scores"])/max(len(type_data[x]["scores"]),1), reverse=True):
        d = type_data[qt]
        avg = sum(d["scores"]) / max(len(d["scores"]), 1)
        pr = 100 * d["passed"] / max(len(d["scores"]), 1)
        icon = "GOOD" if avg >= 7 else "FAIR" if avg >= 4 else "POOR"
        lines.append(f"| {qt} | {avg:.1f}/10 | {pr:.0f}% | {len(d['scores'])} | {icon} |")
    
    # Score by Language
    lines.append("\n### Scores by Language\n")
    lines.append("| Language | Avg Score | Pass Rate | Tested |")
    lines.append("|---|---|---|---|")
    
    lang_data = {}
    lang_names = {"en": "English", "hi": "Hindi (Devanagari)", "hi_roman": "Hindi (Romanized)", 
                  "gu": "Gujarati", "fr": "French", "ja": "Japanese"}
    for r in results:
        for q in valid_queries(r):
            lg = q["lang"]
            if lg not in lang_data:
                lang_data[lg] = {"scores": [], "passed": 0}
            lang_data[lg]["scores"].append(q["evaluation"]["score"])
            if q["evaluation"]["passed"]:
                lang_data[lg]["passed"] += 1
    
    for lg in sorted(lang_data.keys()):
        d = lang_data[lg]
        avg = sum(d["scores"]) / max(len(d["scores"]), 1)
        pr = 100 * d["passed"] / max(len(d["scores"]), 1)
        lines.append(f"| {lang_names.get(lg, lg)} | {avg:.1f}/10 | {pr:.0f}% | {len(d['scores'])} |")
    
    # Score by Site
    lines.append("\n### Scores by Site\n")
    lines.append("| Site | Category | Pages | Avg Score | Pass Rate | Queries | Rate Limited |")
    lines.append("|---|---|---|---|---|---|---|")
    
    for r in results:
        vq = valid_queries(r)
        rl = sum(1 for q in r.query_results if q.get("is_rate_limited"))
        if vq:
            scores = [q["evaluation"]["score"] for q in vq]
            avg = sum(scores) / len(scores)
            passed = sum(1 for q in vq if q["evaluation"]["passed"])
            pr = 100 * passed / len(vq)
            status = "GOOD" if avg >= 7 else "FAIR" if avg >= 4 else "POOR"
            lines.append(f"| {r.name} | {r.category} | {r.pages} | {avg:.1f}/10 | {pr:.0f}% | {len(vq)} | {rl} |")
        else:
            lines.append(f"| {r.name} | {r.category} | {r.pages} | N/A | N/A | 0 | {rl} |")
    
    # ============ CRAWL ANALYSIS ============
    lines.append("\n---\n## Crawl Analysis\n")
    
    lines.append("### Existing Chatbots (Pre-crawled)\n")
    for bot in EXISTING_BOTS:
        lines.append(f"- **{bot['name']}** — {bot['url']} — {bot['pages']} pages — {bot['category']}")
    
    if crawl_tracking:
        lines.append("\n### Newly Crawled Sites\n")
        for ct in crawl_tracking:
            pages = ct.get("pages", 0)
            status = ct.get("status", "unknown")
            icon = "OK" if pages > 0 else "FAILED"
            lines.append(f"- **{ct['site']['name']}** [{icon}]")
            lines.append(f"  - URL: {ct['site']['url']}")
            lines.append(f"  - Pages Crawled: {pages}")
            lines.append(f"  - Status: {status}")
    
    # ============ DETAILED RESULTS PER SITE ============
    lines.append("\n---\n## Detailed Results Per Site\n")
    
    for r in results:
        lines.append(f"### {r.name} ({r.category})")
        lines.append(f"**URL:** {r.url} | **Pages:** {r.pages} | **Chatbot ID:** `{r.bot_id}`\n")
        
        vq = valid_queries(r)
        if not vq and not r.query_results:
            lines.append("_No queries tested_\n")
            continue
        
        # Summary stats
        if vq:
            scores = [q["evaluation"]["score"] for q in vq]
            avg = sum(scores) / len(scores)
            passed = sum(1 for q in vq if q["evaluation"]["passed"])
            lines.append(f"**Summary:** Avg Score {avg:.1f}/10 | Passed {passed}/{len(vq)} | Rate Limited {len(r.query_results) - len(vq)}\n")
        
        lines.append("| # | Type | Lang | Query | Score | Prods | Srcs | Suggestions | Issues |")
        lines.append("|---|---|---|---|---|---|---|---|---|")
        
        for i, q in enumerate(r.query_results, 1):
            ev = q["evaluation"]
            if ev["score"] < 0:
                score_str = "SKIP"
            else:
                score_str = f"{ev['score']}/10"
            issues = "; ".join(ev["issues"]) if ev["issues"] else "-"
            suggs = ", ".join(q["suggestions"][:2]) if q["suggestions"] else "-"
            query_short = q["query"][:45].replace("|", "/").replace("\n", " ")
            lines.append(
                f"| {i} | {q['type']} | {q['lang']} | {query_short} | {score_str} | "
                f"{q['products_count']} | {q['sources_count']} | {suggs[:50]} | {issues[:70]} |"
            )
        lines.append("")
    
    # ============ PRODUCT DISPLAY ANALYSIS ============
    lines.append("\n---\n## Product Display Analysis\n")
    lines.append("How well product cards are returned for product-related queries.\n")
    
    product_types = ["product_browse", "specific_product", "price_query", "complex", "comparison", "variant_query"]
    
    for r in results:
        p_queries = [q for q in valid_queries(r) if q["type"] in product_types]
        if not p_queries:
            continue
        
        lines.append(f"### {r.name} ({r.category})")
        total_pq = len(p_queries)
        with_prods = sum(1 for q in p_queries if q["products_count"] > 0)
        lines.append(f"- Product queries tested: {total_pq}")
        lines.append(f"- Queries returning products: {with_prods}/{total_pq} ({100*with_prods/max(total_pq,1):.0f}%)")
        
        for q in p_queries:
            lines.append(f"\n  **Q:** \"{q['query'][:60]}\" [{q['type']}, {q['lang']}]")
            lines.append(f"  **Score:** {q['evaluation']['score']}/10 | **Products:** {q['products_count']} | **Sources:** {q['sources_count']}")
            if q["products"]:
                for p in q["products"][:3]:
                    pname = p.get("name", p.get("title", "?"))[:50]
                    pprice = p.get("price", "N/A")
                    purl = p.get("url", "N/A")[:60]
                    lines.append(f"  - {pname} | Price: {pprice} | {purl}")
            if q["evaluation"]["issues"]:
                lines.append(f"  Issues: {'; '.join(q['evaluation']['issues'])}")
        lines.append("")
    
    # ============ SUGGESTIONS ANALYSIS ============
    lines.append("\n---\n## Suggestions Analysis\n")
    
    with_sugg = 0
    without_sugg = 0
    all_suggs = []
    
    for r in results:
        for q in valid_queries(r):
            if q["type"] not in ["irrelevant", "unsupported_lang"]:
                if q["suggestions"]:
                    with_sugg += 1
                    all_suggs.extend(q["suggestions"])
                else:
                    without_sugg += 1
    
    total_eligible = with_sugg + without_sugg
    lines.append(f"- Queries with suggestions: {with_sugg}/{total_eligible} ({100*with_sugg/max(total_eligible,1):.0f}%)")
    lines.append(f"- Queries without suggestions: {without_sugg}/{total_eligible}")
    
    if all_suggs:
        lines.append(f"\n**Sample suggestions (first 30):**")
        for s in all_suggs[:30]:
            lines.append(f"- {s}")
    
    # ============ ISSUES & FAILURES ============
    lines.append("\n---\n## Issues and Failures Summary\n")
    
    all_issues = []
    for r in results:
        for q in valid_queries(r):
            for issue in q["evaluation"]["issues"]:
                all_issues.append({
                    "site": r.name,
                    "type": q["type"],
                    "lang": q["lang"],
                    "query": q["query"][:55],
                    "issue": issue,
                    "score": q["evaluation"]["score"],
                })
    
    if all_issues:
        # Group by issue type
        issue_groups = {}
        for iss in all_issues:
            key = iss["issue"][:60]
            if key not in issue_groups:
                issue_groups[key] = []
            issue_groups[key].append(iss)
        
        lines.append(f"**Total issues found:** {len(all_issues)}\n")
        
        for issue_key in sorted(issue_groups.keys(), key=lambda k: -len(issue_groups[k])):
            items = issue_groups[issue_key]
            lines.append(f"### Issue: {issue_key} ({len(items)} occurrences)")
            lines.append("| Site | Query Type | Language | Query | Score |")
            lines.append("|---|---|---|---|---|")
            for item in items[:15]:
                lines.append(f"| {item['site']} | {item['type']} | {item['lang']} | {item['query'][:40]} | {item['score']}/10 |")
            if len(items) > 15:
                lines.append(f"| ... | ... | ... | +{len(items)-15} more | ... |")
            lines.append("")
    else:
        lines.append("No issues found!\n")
    
    # ============ SAMPLE RESPONSES ============
    lines.append("\n---\n## Sample Responses\n")
    lines.append("Representative responses for each query type.\n")
    
    shown_types = set()
    for r in results:
        for q in valid_queries(r):
            tkey = q["type"]
            if tkey not in shown_types:
                shown_types.add(tkey)
                lines.append(f"### Query Type: {tkey}")
                lines.append(f"**Site:** {r.name} | **Lang:** {q['lang']} | **Score:** {q['evaluation']['score']}/10")
                lines.append(f"**Query:** \"{q['query'][:80]}\"")
                resp_text = q["response_content"][:500] if q["response_content"] else "(empty)"
                lines.append(f"\n**Bot Response:**\n```\n{resp_text}\n```\n")
                if q["suggestions"]:
                    lines.append(f"**Suggestions:** {q['suggestions']}")
                if q["products"]:
                    lines.append(f"**Products:** {q['products_count']} returned")
                    for p in q["products"][:2]:
                        lines.append(f"- {p.get('name', p.get('title','?'))[:60]} | {p.get('price', 'N/A')}")
                lines.append("")
    
    # ============ CONVERSATION CONTEXT ANALYSIS ============
    lines.append("\n---\n## Conversation Context Analysis\n")
    lines.append("Testing whether the bot maintains conversation context across messages.\n")
    
    for r in results:
        context_qs = [q for q in valid_queries(r) if q["type"] in ["context_start", "context_followup", "context_summary"]]
        if not context_qs:
            continue
        
        lines.append(f"### {r.name}")
        for q in context_qs:
            lines.append(f"\n**[{q['type']}]** \"{q['query'][:60]}\"")
            lines.append(f"Score: {q['evaluation']['score']}/10")
            resp_short = q["response_content"][:300] if q["response_content"] else "(empty)"
            lines.append(f"```\n{resp_short}\n```")
            if q["evaluation"]["issues"]:
                lines.append(f"Issues: {'; '.join(q['evaluation']['issues'])}")
        lines.append("")
    
    # ============ LANGUAGE HANDLING ANALYSIS ============
    lines.append("\n---\n## Multi-Language Handling Analysis\n")
    
    for lang_key in ["hi", "hi_roman", "gu", "fr", "ja"]:
        lang_name = lang_names.get(lang_key, lang_key)
        lang_qs = [q for r in results for q in valid_queries(r) if q["lang"] == lang_key]
        if not lang_qs:
            continue
        
        avg = sum(q["evaluation"]["score"] for q in lang_qs) / max(len(lang_qs), 1)
        passed = sum(1 for q in lang_qs if q["evaluation"]["passed"])
        
        lines.append(f"### {lang_name}")
        lines.append(f"- Queries: {len(lang_qs)} | Avg Score: {avg:.1f}/10 | Passed: {passed}/{len(lang_qs)}")
        
        # Show sample
        for q in lang_qs[:3]:
            lines.append(f"  - **Q:** \"{q['query'][:50]}\" -> Score: {q['evaluation']['score']}/10")
            if q["response_content"]:
                lines.append(f"    Response: {q['response_content'][:150]}...")
        lines.append("")
    
    # ============ RECOMMENDATIONS ============
    lines.append("\n---\n## Recommendations and Improvements\n")
    
    recommendations = []
    
    # Analyze each area
    if type_data.get("irrelevant"):
        irr_avg = sum(type_data["irrelevant"]["scores"]) / len(type_data["irrelevant"]["scores"])
        if irr_avg < 6:
            recommendations.append({
                "priority": "HIGH", "area": "Irrelevant Query Detection",
                "problem": f"Average score {irr_avg:.1f}/10 for irrelevant queries. Bot tries to answer off-topic questions.",
                "fix": "1) Strengthen system prompt to firmly decline off-topic queries. 2) Add confidence threshold — when retrieval scores are very low across all chunks, default to 'outside my knowledge'. 3) If query analysis detects intent='irrelevant', short-circuit to a polite decline without KB search."
            })
    
    if type_data.get("product_browse"):
        pb_avg = sum(type_data["product_browse"]["scores"]) / len(type_data["product_browse"]["scores"])
        if pb_avg < 7:
            recommendations.append({
                "priority": "HIGH", "area": "Product Card Display",
                "problem": f"Product browsing score {pb_avg:.1f}/10. Product cards may not be extracted from crawled content.",
                "fix": "1) Improve product extraction — parse JSON-LD, Open Graph, and microdata from crawled pages. 2) Detect product pages by URL patterns (/product/, /p/, /item/). 3) Store structured product data (name, price, image, URL) during crawl for reliable product card display."
            })
    
    if total_eligible > 0 and with_sugg / total_eligible < 0.6:
        recommendations.append({
            "priority": "MEDIUM", "area": "Suggestion Generation",
            "problem": f"Only {100*with_sugg/total_eligible:.0f}% of eligible queries got suggestions.",
            "fix": "1) Ensure LLM prompt always requests 3 contextual follow-up suggestions. 2) Add fallback suggestion generation when LLM doesn't include them. 3) Use cache-based popular queries as fallback suggestions."
        })
    
    # Language gap
    en_qs = [q for r in results for q in valid_queries(r) if q["lang"] == "en"]
    hi_qs = [q for r in results for q in valid_queries(r) if q["lang"] in ["hi", "hi_roman"]]
    gu_qs = [q for r in results for q in valid_queries(r) if q["lang"] == "gu"]
    
    en_avg = sum(q["evaluation"]["score"] for q in en_qs) / max(len(en_qs), 1) if en_qs else 0
    hi_avg = sum(q["evaluation"]["score"] for q in hi_qs) / max(len(hi_qs), 1) if hi_qs else 0
    gu_avg = sum(q["evaluation"]["score"] for q in gu_qs) / max(len(gu_qs), 1) if gu_qs else 0
    
    if hi_qs and hi_avg < en_avg - 1:
        recommendations.append({
            "priority": "HIGH", "area": "Hindi Performance Gap",
            "problem": f"Hindi avg {hi_avg:.1f} vs English avg {en_avg:.1f}. Hindi queries underperform.",
            "fix": "1) Ensure query translation in unified LLM call produces good English queries for KB search. 2) Add Hindi few-shot examples in system prompt. 3) Consider bilingual embedding model."
        })
    
    if gu_qs and gu_avg < en_avg - 1:
        recommendations.append({
            "priority": "MEDIUM", "area": "Gujarati Performance Gap",
            "problem": f"Gujarati avg {gu_avg:.1f} vs English avg {en_avg:.1f}.",
            "fix": "Same as Hindi recommendations. Gujarati may need extra translation quality checks."
        })
    
    # Context handling
    if type_data.get("context_summary"):
        cs_avg = sum(type_data["context_summary"]["scores"]) / len(type_data["context_summary"]["scores"])
        if cs_avg < 6:
            recommendations.append({
                "priority": "MEDIUM", "area": "Conversation Context/Summary",
                "problem": f"Conversation summary score {cs_avg:.1f}/10. Bot doesn't leverage conversation history well.",
                "fix": "1) Review conversation summary generation — ensure it captures key topics discussed. 2) Pass summary to LLM with explicit instruction to reference it. 3) Test that follow-up queries properly resolve references."
            })
    
    # Non-product queries
    if type_data.get("non_product"):
        np_avg = sum(type_data["non_product"]["scores"]) / len(type_data["non_product"]["scores"])
        if np_avg < 6:
            recommendations.append({
                "priority": "MEDIUM", "area": "Non-Product Query Handling",
                "problem": f"Policy/info queries score {np_avg:.1f}/10.",
                "fix": "1) Ensure crawler follows links to /policy, /faq, /shipping, /about pages. 2) Prioritize these pages in crawl. 3) Add explicit FAQ extraction from crawled content."
            })
    
    # Rate limiting
    if total_rate_limited > 0:
        recommendations.append({
            "priority": "HIGH", "area": "Rate Limiting / API Key Management",
            "problem": f"{total_rate_limited} queries were rate-limited.",
            "fix": "1) Implement API key rotation in the chat service itself. 2) Add request queuing and backoff. 3) Consider using a cheaper/unlimited LLM for simple queries (greetings, irrelevant detection)."
        })
    
    # Crawl issues
    crawl_failures = [ct for ct in crawl_tracking if ct.get("pages", 0) == 0 or ct.get("status") == "failed"]
    if crawl_failures:
        recommendations.append({
            "priority": "HIGH", "area": "Crawl Failures",
            "problem": f"{len(crawl_failures)} sites failed to crawl: {', '.join(ct['site']['name'] for ct in crawl_failures)}",
            "fix": "1) Auto-detect sitemap.xml and use it as crawl source. 2) Better JS rendering for SPA sites. 3) User-agent rotation. 4) Give clear warnings about blocked/JS-heavy sites. 5) Automatic retry with headless browser for failed HTML-only crawls."
        })
    
    recommendations.append({
        "priority": "LOW", "area": "General Improvements",
        "problem": "General observations from testing.",
        "fix": "1) Add confidence scores in API response for debugging. 2) Improve response formatting consistency. 3) Add response quality logging. 4) Consider caching frequent queries within same chatbot."
    })
    
    for rec in sorted(recommendations, key=lambda x: {"HIGH": 0, "MEDIUM": 1, "LOW": 2}[x["priority"]]):
        icon = {"HIGH": "[HIGH]", "MEDIUM": "[MEDIUM]", "LOW": "[LOW]"}[rec["priority"]]
        lines.append(f"### {icon} {rec['area']}")
        lines.append(f"**Problem:** {rec['problem']}")
        lines.append(f"**Fix:** {rec['fix']}\n")
    
    # ============ WRITE REPORT ============
    report_content = "\n".join(lines)
    report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "CHATBOT_TEST_REPORT.md")
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
    print(f"  Report saved: {report_path}")
    
    # Save raw JSON data too
    raw_data = []
    for r in results:
        raw_data.append({
            "name": r.name, "bot_id": r.bot_id, "category": r.category,
            "url": r.url, "pages": r.pages, "query_results": r.query_results,
        })
    
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chatbot_test_raw_data.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(raw_data, f, indent=2, ensure_ascii=False, default=str)
    print(f"  Raw data saved: {json_path}")


if __name__ == "__main__":
    # Fix Windows console encoding for Hindi/Gujarati/Japanese text
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    run_tests()
