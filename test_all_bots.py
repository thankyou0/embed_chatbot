"""
Comprehensive Test of All 8 Chatbots with Multi-Key Rotation
============================================================
Tests 5 existing + 3 newly crawled bots with 43 diverse query types.
Uses 6 GROQ keys with rotation on rate limit, no Docker restart needed
since keys have reset.
"""
import requests
import json
import time
import sys
import os
import re
import subprocess
import io
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

# Fix Windows UTF-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ============================================================
# Configuration
# ============================================================
BASE_URL = "http://localhost:8000/api/v1"
EMAIL = "max@gmail.com"
PASSWORD = "12345678"
ENV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")

GROQ_KEYS = [
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
]

current_key_index = 0
rate_limited_keys = set()
all_keys_exhausted = False
DELAY_BETWEEN_MSGS = 2

# ============================================================
# All 8 Bots to Test
# ============================================================
ALL_BOTS = [
    # Existing 5
    {"id": "182f88cd-02d8-4c94-824d-b41432847400", "name": "ramraj", "url": "https://ramrajcotton.in", "category": "Fashion/Clothing", "pages": 256},
    {"id": "e9f5fd28-cfe1-4456-994e-46aeb154388f", "name": "truff", "url": "https://truff.com", "category": "Food/Condiments", "pages": 262},
    {"id": "1cb18dc0-4909-409d-ab03-0436524fcec4", "name": "kriyanta", "url": "https://www.kriyanta.com", "category": "Tech/Startup", "pages": 803},
    {"id": "868f937e-8559-446d-b7c8-ff630ec7fd79", "name": "kids", "url": "https://www.cheaperzonetoys.com", "category": "Kids/Toys", "pages": 102},
    {"id": "e79b3754-006d-45d5-b21d-2391710e08ca", "name": "zevaramaze", "url": "https://zevaramaze.com", "category": "Jewelry", "pages": 276},
    # New 3
    {"id": "e23fcc6f-7a02-4b09-8d49-95c00a57d852", "name": "beardbrand", "url": "https://www.beardbrand.com", "category": "Grooming", "pages": 57},
    {"id": "99fc3604-99e7-4cd0-a2a6-509ac08d9fd0", "name": "deathwish", "url": "https://www.deathwishcoffee.com", "category": "Coffee/Beverage", "pages": 185},
    {"id": "799637f9-391b-4b9d-84cb-5fdd17cdf109", "name": "tentree", "url": "https://www.tentree.com", "category": "Fashion/Eco", "pages": 200},
]


# ============================================================
# GROQ Key Rotation
# ============================================================
def switch_groq_key() -> bool:
    global current_key_index, all_keys_exhausted
    rate_limited_keys.add(current_key_index)
    
    for i in range(len(GROQ_KEYS)):
        candidate = (current_key_index + 1 + i) % len(GROQ_KEYS)
        if candidate not in rate_limited_keys:
            current_key_index = candidate
            print(f"\n    >>> SWITCHING TO GROQ KEY #{candidate+1}/{len(GROQ_KEYS)} <<<")
            _update_env_and_restart()
            return True
    
    all_keys_exhausted = True
    print(f"\n    >>> ALL {len(GROQ_KEYS)} GROQ KEYS EXHAUSTED <<<")
    return False


def _update_env_and_restart():
    new_key = GROQ_KEYS[current_key_index]
    with open(ENV_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    content = re.sub(r'^GROQ_API_KEY\s*=\s*.*$', f'GROQ_API_KEY ={new_key}', content, flags=re.MULTILINE)
    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"    Updated .env with key #{current_key_index+1}: ...{new_key[-8:]}")
    print(f"    Restarting docker API container...")
    try:
        subprocess.run(["docker-compose", "up", "-d", "api"], cwd=os.path.dirname(os.path.abspath(__file__)), capture_output=True, text=True, timeout=60)
    except Exception as e:
        print(f"    Warning: docker restart issue: {e}")
    
    print(f"    Waiting for API...")
    for attempt in range(30):
        try:
            resp = requests.get(f"{BASE_URL}/health", timeout=5)
            if resp.status_code == 200:
                print(f"    API ready after {(attempt+1)*3}s")
                return
        except:
            pass
        time.sleep(3)
    for attempt in range(10):
        try:
            resp = requests.post(f"{BASE_URL}/auth/login", json={"email": EMAIL, "password": PASSWORD}, timeout=10)
            if resp.status_code in [200, 401, 422]:
                print(f"    API ready")
                return
        except:
            pass
        time.sleep(3)


# ============================================================
# API Helpers
# ============================================================
def login() -> str:
    for attempt in range(5):
        try:
            resp = requests.post(f"{BASE_URL}/auth/login", json={"email": EMAIL, "password": PASSWORD}, timeout=30)
            resp.raise_for_status()
            return resp.json()["access_token"]
        except:
            if attempt < 4:
                time.sleep(5)
            else:
                raise


def send_chat_message(chatbot_id: str, message: str, session_id: Optional[str] = None) -> Dict:
    data = {"message": message}
    if session_id:
        data["session_id"] = session_id
    
    result = {"content": "", "sources": [], "suggestions": [], "products": [], "session_id": None, "error": None, "status_messages": [], "raw_events": [], "is_rate_limited": False}
    
    try:
        resp = requests.post(f"{BASE_URL}/chat/{chatbot_id}/message/stream", data=data, stream=True, timeout=90)
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
    
    rate_limit_phrases = ["rate limit", "too many requests", "try again in a few minutes", "getting a lot of requests", "rate_limit_exceeded", "429", "please try again", "lot of requests right now"]
    full_text = (result["content"] + " " + str(result.get("error", ""))).lower()
    if any(phrase in full_text for phrase in rate_limit_phrases):
        result["is_rate_limited"] = True
    
    return result


# ============================================================
# Query Templates  
# ============================================================
def get_queries_for_bot(bot_name: str, category: str) -> List[Dict]:
    product_map = {
        "Fashion/Clothing": {"products": ["shirts", "dhotis", "cotton shirts", "formal shirts"], "brand_items": "cotton clothing"},
        "Food/Condiments": {"products": ["hot sauce", "truffle sauce", "pasta sauce", "condiments"], "brand_items": "premium sauces"},
        "Tech/Startup": {"products": ["services", "solutions", "portfolio", "projects"], "brand_items": "technology services"},
        "Kids/Toys": {"products": ["toys", "board games", "action figures", "puzzles"], "brand_items": "kids toys"},
        "Jewelry": {"products": ["bracelets", "necklaces", "rings", "earrings"], "brand_items": "jewelry and accessories"},
        "Grooming": {"products": ["beard oil", "beard balm", "grooming kit", "utility balm"], "brand_items": "men's grooming"},
        "Coffee/Beverage": {"products": ["coffee", "ground coffee", "K-cups", "death cups"], "brand_items": "coffee and beverages"},
        "Fashion/Eco": {"products": ["t-shirts", "hoodies", "joggers", "jackets"], "brand_items": "sustainable clothing"},
    }
    
    pdata = product_map.get(category, {"products": ["products", "items", "goods", "offerings"], "brand_items": "products"})
    p = pdata["products"]
    
    queries = []
    
    # Greetings (3)
    queries.append({"type": "greeting", "lang": "en", "text": "Hi there! What can you help me with?"})
    queries.append({"type": "greeting", "lang": "hi", "text": "नमस्ते! आप मेरी कैसे मदद कर सकते हैं?"})
    queries.append({"type": "greeting", "lang": "hi_roman", "text": "hello bhai, kya help kar sakte ho?"})
    
    # Product Browse (4)
    queries.append({"type": "product_browse", "lang": "en", "text": f"Show me your best {p[0]}"})
    queries.append({"type": "product_browse", "lang": "en", "text": f"What {p[1]} do you have available?"})
    queries.append({"type": "product_browse", "lang": "hi", "text": f"आपके पास कौन से {p[0]} उपलब्ध हैं?"})
    queries.append({"type": "product_browse", "lang": "gu", "text": f"તમારી પાસે કયા {p[0]} છે?"})
    
    # Specific Product (4)
    queries.append({"type": "specific_product", "lang": "en", "text": f"I'm looking for a black {p[0]}"})
    queries.append({"type": "specific_product", "lang": "en", "text": f"Do you have any premium {p[2]}?"})
    queries.append({"type": "specific_product", "lang": "hi", "text": f"मुझे {p[0]} चाहिए जो बहुत अच्छी क्वालिटी का हो"})
    queries.append({"type": "specific_product", "lang": "hi_roman", "text": f"best quality {p[0]} dikhao"})
    
    # Price Queries (4)
    queries.append({"type": "price_query", "lang": "en", "text": f"Show me {p[0]} under $30"})
    queries.append({"type": "price_query", "lang": "en", "text": f"What's the price range for your {p[1]}?"})
    queries.append({"type": "price_query", "lang": "hi", "text": f"500 रुपये से कम के {p[0]} बताओ"})
    queries.append({"type": "price_query", "lang": "gu", "text": f"$50 થી ઓછા {p[0]} બતાવો"})
    
    # Non-product queries (4)
    queries.append({"type": "non_product", "lang": "en", "text": "What is your return policy?"})
    queries.append({"type": "non_product", "lang": "en", "text": "How long does shipping take?"})
    queries.append({"type": "non_product", "lang": "en", "text": "Do you offer cash on delivery?"})
    queries.append({"type": "non_product", "lang": "hi", "text": "रिटर्न पॉलिसी क्या है?"})
    
    # Irrelevant (4)
    queries.append({"type": "irrelevant", "lang": "en", "text": "What is the capital of France?"})
    queries.append({"type": "irrelevant", "lang": "en", "text": "Can you write me a Python script to sort a list?"})
    queries.append({"type": "irrelevant", "lang": "hi", "text": "भारत का प्रधानमंत्री कौन है?"})
    queries.append({"type": "irrelevant", "lang": "en", "text": "What's the weather like in Tokyo today?"})
    
    # Ambiguous (3)
    queries.append({"type": "ambiguous", "lang": "en", "text": "I want something nice for a gift"})
    queries.append({"type": "ambiguous", "lang": "en", "text": "What do you recommend for someone new?"})
    queries.append({"type": "ambiguous", "lang": "hi", "text": "कुछ अच्छा बताओ ना"})
    
    # Complex (2)
    queries.append({"type": "complex", "lang": "en", "text": f"I need a gift for my sister, she likes {p[0]} in red or blue, budget around $50, and also tell me about your return policy"})
    queries.append({"type": "complex", "lang": "hi", "text": f"मेरी बहन के लिए {p[0]} चाहिए, लाल या नीला रंग, 2000 रुपये से कम, और delivery कितने दिन में होगी?"})
    
    # Context/Follow-up (4, sequential)
    queries.append({"type": "context_start", "lang": "en", "text": f"Show me your most popular {p[0]}"})
    queries.append({"type": "context_followup", "lang": "en", "text": "Do you have this in a different color?"})
    queries.append({"type": "context_followup", "lang": "en", "text": "What about a larger size?"})
    queries.append({"type": "context_summary", "lang": "en", "text": "Can you summarize what we've talked about so far?"})
    
    # About Brand (2)
    queries.append({"type": "about_brand", "lang": "en", "text": f"Tell me about {bot_name} and what you sell"})
    queries.append({"type": "about_brand", "lang": "hi", "text": f"{bot_name} के बारे में बताओ"})
    
    # Unsupported Language (2)
    queries.append({"type": "unsupported_lang", "lang": "fr", "text": "Bonjour, montrez-moi vos produits les plus populaires"})
    queries.append({"type": "unsupported_lang", "lang": "ja", "text": "こんにちは、人気商品を教えてください"})
    
    # Suggestions Quality (2)
    queries.append({"type": "suggestions_test", "lang": "en", "text": "I'm new here, what kind of things do you sell?"})
    queries.append({"type": "suggestions_test", "lang": "hi", "text": "यहां क्या-क्या मिलता है?"})
    
    # Comparison (1)
    queries.append({"type": "comparison", "lang": "en", "text": f"What's the difference between your cheapest and most expensive {p[0]}?"})
    
    # Variant (2)
    queries.append({"type": "variant_query", "lang": "en", "text": f"Do you have {p[0]} in size L or XL?"})
    queries.append({"type": "variant_query", "lang": "hi_roman", "text": f"{p[0]} mein kya sizes available hain?"})
    
    # Urgency (1)
    queries.append({"type": "urgency", "lang": "en", "text": f"I need {p[0]} urgently for tomorrow, can you deliver?"})
    
    # Complaint (1)
    queries.append({"type": "complaint", "lang": "en", "text": f"I received a damaged {p[0]}, what should I do?"})
    
    return queries  # 43 queries per bot


# ============================================================
# Response Evaluation
# ============================================================
def evaluate_response(query_type: str, response: Dict, lang: str, bot_category: str) -> Dict:
    ev = {"score": 0, "max_score": 10, "issues": [], "passed": True, "notes": ""}
    
    content = response.get("content", "").strip()
    error = response.get("error")
    sources = response.get("sources", [])
    products = response.get("products", [])
    suggestions = response.get("suggestions", [])
    is_rate_limited = response.get("is_rate_limited", False)
    
    if is_rate_limited:
        ev["score"] = -1
        ev["issues"].append("RATE_LIMITED")
        ev["notes"] = "Skipped - rate limit"
        return ev
    
    if error:
        ev["score"] = 0
        ev["passed"] = False
        ev["issues"].append(f"ERROR: {error[:100]}")
        return ev
    
    if not content:
        ev["score"] = 0
        ev["passed"] = False
        ev["issues"].append("Empty response")
        return ev
    
    content_lower = content.lower()
    
    if query_type == "greeting":
        ev["score"] = 8 if len(content) > 20 else 5
        if suggestions:
            ev["score"] = min(10, ev["score"] + 1)
        if lang == "hi" and any(c > '\u0900' and c < '\u097F' for c in content):
            ev["score"] = min(10, ev["score"] + 1)
            ev["notes"] = "Hindi response detected"
    
    elif query_type in ["product_browse", "specific_product"]:
        if products:
            ev["score"] = 9
            ev["notes"] = f"{len(products)} products returned"
        elif any(kw in content_lower for kw in ["product", "item", "available", "offer", "here are", "check out"]):
            ev["score"] = 7
            ev["notes"] = "Mentioned products textually"
        else:
            ev["score"] = 4
            ev["issues"].append("No products returned or mentioned")
        if lang in ["hi", "gu"] and ev["score"] >= 7:
            ev["score"] = min(10, ev["score"] + 1)
    
    elif query_type == "price_query":
        price_patterns = [r'\$\d+', r'₹\d+', r'\d+\s*(rs|rupees|dollars)', r'price', r'range', r'cost', r'budget']
        if any(re.search(p, content_lower) for p in price_patterns):
            ev["score"] = 8
        elif products:
            ev["score"] = 7
            ev["notes"] = "Products shown (likely with prices)"
        else:
            ev["score"] = 4
            ev["issues"].append("No price info in response")
    
    elif query_type == "non_product":
        policy_kw = ["return", "shipping", "delivery", "refund", "policy", "exchange", "days", "business days", "cod", "cash"]
        if any(kw in content_lower for kw in policy_kw):
            ev["score"] = 8
        elif len(content) > 50:
            ev["score"] = 5
            ev["notes"] = "Response given but unclear policy info"
        else:
            ev["score"] = 3
            ev["issues"].append("No policy information found")
    
    elif query_type == "irrelevant":
        rejection_kw = ["can't help", "cannot help", "outside", "not related", "don't have", "beyond", "only help", "specifically", "trained", "assist with"]
        if any(kw in content_lower for kw in rejection_kw):
            ev["score"] = 9
            ev["notes"] = "Correctly rejected irrelevant query"
        elif len(content) < 100:
            ev["score"] = 6
            ev["notes"] = "Short response (may be polite deflection)"
        else:
            ev["score"] = 2
            ev["issues"].append("Bot answered irrelevant question instead of rejecting")
    
    elif query_type == "ambiguous":
        if suggestions or "recommend" in content_lower or "popular" in content_lower or "would you like" in content_lower:
            ev["score"] = 8
            ev["notes"] = "Provided recommendations or asked to clarify"
        elif products:
            ev["score"] = 7
        else:
            ev["score"] = 4
            ev["issues"].append("Didn't guide user or ask for clarification")
    
    elif query_type == "complex":
        aspects = 0
        if products or any(kw in content_lower for kw in ["product", "option", "recommend"]):
            aspects += 1
        if any(kw in content_lower for kw in ["color", "red", "blue", "laal", "neela"]):
            aspects += 1
        if any(kw in content_lower for kw in ["price", "budget", "cost", "$", "₹", "rupee"]):
            aspects += 1
        if any(kw in content_lower for kw in ["return", "shipping", "delivery", "exchange"]):
            aspects += 1
        ev["score"] = min(10, 3 + aspects * 2)
        ev["notes"] = f"Addressed {aspects}/4 aspects"
    
    elif query_type in ["context_start"]:
        ev["score"] = 7 if len(content) > 30 else 4
        if products:
            ev["score"] = 9
    
    elif query_type == "context_followup":
        if len(content) > 30 and not any(kw in content_lower for kw in ["i don't understand", "could you clarify", "what do you mean"]):
            ev["score"] = 8
            ev["notes"] = "Maintained context"
        else:
            ev["score"] = 4
            ev["issues"].append("May have lost conversation context")
    
    elif query_type == "context_summary":
        if any(kw in content_lower for kw in ["discussed", "talked about", "so far", "earlier", "previous", "mentioned", "asked"]):
            ev["score"] = 9
            ev["notes"] = "Good summary of conversation"
        elif len(content) > 50:
            ev["score"] = 6
        else:
            ev["score"] = 3
            ev["issues"].append("Failed to summarize conversation")
    
    elif query_type == "about_brand":
        if any(kw in content_lower for kw in ["about", "brand", "founded", "mission", "company", "we are", "our"]):
            ev["score"] = 8
        else:
            ev["score"] = 4
            ev["issues"].append("Didn't provide brand info")
    
    elif query_type == "unsupported_lang":
        if any(kw in content_lower for kw in ["sorry", "english", "hindi", "support", "language", "apologies"]):
            ev["score"] = 8
            ev["notes"] = "Acknowledged language limitation"
        elif len(content) > 30:
            ev["score"] = 5
            ev["notes"] = "Responded but may not have addressed language issue"
        else:
            ev["score"] = 3
    
    elif query_type == "suggestions_test":
        if suggestions:
            ev["score"] = 9
            ev["notes"] = f"Suggestions: {suggestions[:3]}"
        elif products:
            ev["score"] = 7
        else:
            ev["score"] = 5
            ev["issues"].append("No suggestions provided")
    
    elif query_type == "comparison":
        if any(kw in content_lower for kw in ["cheapest", "expensive", "difference", "compare", "vs", "versus", "range"]):
            ev["score"] = 9
        elif products and len(products) >= 2:
            ev["score"] = 8
        else:
            ev["score"] = 4
            ev["issues"].append("No comparison given")
    
    elif query_type == "variant_query":
        if any(kw in content_lower for kw in ["size", "variant", "l", "xl", "available in", "comes in"]):
            ev["score"] = 8
        elif products:
            ev["score"] = 7
        else:
            ev["score"] = 4
    
    elif query_type == "urgency":
        if any(kw in content_lower for kw in ["delivery", "ship", "express", "fast", "urgent", "tomorrow", "overnight"]):
            ev["score"] = 8
        else:
            ev["score"] = 4
            ev["issues"].append("Didn't address urgency")
    
    elif query_type == "complaint":
        if any(kw in content_lower for kw in ["sorry", "apologize", "return", "refund", "exchange", "contact", "support", "help"]):
            ev["score"] = 8
        else:
            ev["score"] = 3
            ev["issues"].append("Didn't handle complaint properly")
    
    else:
        ev["score"] = 5
    
    ev["passed"] = ev["score"] >= 5
    return ev


# ============================================================
# Report Generation
# ============================================================
def generate_report(all_results: List[Dict], start_time: datetime):
    """Generate comprehensive markdown report."""
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    total_queries = len(all_results)
    valid_results = [r for r in all_results if r["eval"]["score"] >= 0]
    errors = [r for r in all_results if r["eval"]["score"] == 0 and not r["response"].get("is_rate_limited")]
    rate_limited = [r for r in all_results if r["response"].get("is_rate_limited")]
    
    avg_score = sum(r["eval"]["score"] for r in valid_results) / max(len(valid_results), 1)
    
    report = []
    report.append("# Comprehensive Chatbot Testing Report (Round 2)")
    report.append(f"\n**Generated:** {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"**Duration:** {int(duration)}s ({int(duration/60)}m)")
    report.append(f"**Total Queries:** {total_queries}")
    report.append(f"**Valid Scored:** {len(valid_results)}")
    report.append(f"**Rate Limited:** {len(rate_limited)}")
    report.append(f"**Errors:** {len(errors)}")
    report.append(f"**Overall Average Score:** {avg_score:.1f}/10\n")
    
    # ===== KEY FINDINGS =====
    report.append("## Key Findings Summary\n")
    
    # By bot
    report.append("### Per-Bot Performance\n")
    report.append("| Bot | Category | Pages | Queries | Avg Score | Best Type | Worst Type |")
    report.append("|-----|----------|-------|---------|-----------|-----------|------------|")
    
    for bot in ALL_BOTS:
        bot_results = [r for r in valid_results if r["bot_name"] == bot["name"]]
        if not bot_results:
            continue
        bot_avg = sum(r["eval"]["score"] for r in bot_results) / len(bot_results)
        
        # Best/worst by type
        type_scores = {}
        for r in bot_results:
            t = r["query_type"]
            if t not in type_scores:
                type_scores[t] = []
            type_scores[t].append(r["eval"]["score"])
        
        type_avgs = {t: sum(s)/len(s) for t, s in type_scores.items()}
        best_type = max(type_avgs, key=type_avgs.get) if type_avgs else "-"
        worst_type = min(type_avgs, key=type_avgs.get) if type_avgs else "-"
        
        report.append(f"| {bot['name']} | {bot['category']} | {bot['pages']} | {len(bot_results)} | {bot_avg:.1f} | {best_type} ({type_avgs.get(best_type,0):.0f}) | {worst_type} ({type_avgs.get(worst_type,0):.0f}) |")
    
    # By query type
    report.append("\n### Per-Query-Type Performance\n")
    report.append("| Query Type | Count | Avg Score | Pass Rate | Common Issues |")
    report.append("|------------|-------|-----------|-----------|---------------|")
    
    type_groups = {}
    for r in valid_results:
        t = r["query_type"]
        if t not in type_groups:
            type_groups[t] = []
        type_groups[t].append(r)
    
    for t in sorted(type_groups.keys(), key=lambda x: sum(r["eval"]["score"] for r in type_groups[x])/len(type_groups[x]), reverse=True):
        grp = type_groups[t]
        avg = sum(r["eval"]["score"] for r in grp) / len(grp)
        passed = sum(1 for r in grp if r["eval"]["passed"]) / len(grp) * 100
        all_issues = []
        for r in grp:
            all_issues.extend(r["eval"]["issues"])
        top_issues = list(set(all_issues))[:2]
        report.append(f"| {t} | {len(grp)} | {avg:.1f} | {passed:.0f}% | {', '.join(top_issues) if top_issues else 'None'} |")
    
    # By language
    report.append("\n### Per-Language Performance\n")
    report.append("| Language | Count | Avg Score | Pass Rate |")
    report.append("|----------|-------|-----------|-----------|")
    
    lang_groups = {}
    for r in valid_results:
        l = r["lang"]
        if l not in lang_groups:
            lang_groups[l] = []
        lang_groups[l].append(r)
    
    for l in sorted(lang_groups.keys(), key=lambda x: sum(r["eval"]["score"] for r in lang_groups[x])/len(lang_groups[x]), reverse=True):
        grp = lang_groups[l]
        avg = sum(r["eval"]["score"] for r in grp) / len(grp)
        passed = sum(1 for r in grp if r["eval"]["passed"]) / len(grp) * 100
        report.append(f"| {l} | {len(grp)} | {avg:.1f} | {passed:.0f}% |")
    
    # ===== DETAILED RESULTS =====
    report.append("\n\n## Detailed Results by Bot\n")
    
    for bot in ALL_BOTS:
        bot_results = [r for r in all_results if r["bot_name"] == bot["name"]]
        if not bot_results:
            continue
        
        bot_valid = [r for r in bot_results if r["eval"]["score"] >= 0]
        bot_avg = sum(r["eval"]["score"] for r in bot_valid) / max(len(bot_valid), 1)
        
        report.append(f"\n### {bot['name']} ({bot['category']}) - {bot['url']}")
        report.append(f"- **Pages Crawled:** {bot['pages']}")
        report.append(f"- **Queries Tested:** {len(bot_results)}")
        report.append(f"- **Average Score:** {bot_avg:.1f}/10\n")
        
        report.append("| # | Type | Lang | Query | Score | Issues/Notes |")
        report.append("|---|------|------|-------|-------|--------------|")
        
        for i, r in enumerate(bot_results, 1):
            score_str = f"{r['eval']['score']}/10" if r['eval']['score'] >= 0 else "RATE_LIMITED"
            notes = "; ".join(r["eval"]["issues"] + ([r["eval"]["notes"]] if r["eval"]["notes"] else []))[:80]
            query_short = r["query"][:50] + "..." if len(r["query"]) > 50 else r["query"]
            report.append(f"| {i} | {r['query_type']} | {r['lang']} | {query_short} | {score_str} | {notes} |")
    
    # ===== QUALITY ISSUES =====
    report.append("\n\n## Top Quality Issues\n")
    
    low_scores = [r for r in valid_results if r["eval"]["score"] <= 4]
    if low_scores:
        report.append("### Low-Scoring Queries (Score <= 4)\n")
        report.append("| Bot | Type | Lang | Query | Score | Issue |")
        report.append("|-----|------|------|-------|-------|-------|")
        for r in sorted(low_scores, key=lambda x: x["eval"]["score"]):
            issues = "; ".join(r["eval"]["issues"])[:60]
            report.append(f"| {r['bot_name']} | {r['query_type']} | {r['lang']} | {r['query'][:40]}... | {r['eval']['score']}/10 | {issues} |")
    
    # ===== RECOMMENDATIONS =====
    report.append("\n\n## Recommendations\n")
    
    # Analyze patterns
    type_avgs = {}
    for t, grp in type_groups.items():
        type_avgs[t] = sum(r["eval"]["score"] for r in grp) / len(grp)
    
    weak_types = [t for t, avg in type_avgs.items() if avg < 5.0]
    
    if weak_types:
        report.append("### Weak Query Types (avg < 5.0)")
        for t in weak_types:
            report.append(f"- **{t}** ({type_avgs[t]:.1f}/10): Needs improvement in handling this query type")
    
    lang_avgs = {}
    for l, grp in lang_groups.items():
        lang_avgs[l] = sum(r["eval"]["score"] for r in grp) / len(grp)
    
    weak_langs = [l for l, avg in lang_avgs.items() if avg < 5.0]
    if weak_langs:
        report.append("\n### Weak Languages (avg < 5.0)")
        for l in weak_langs:
            report.append(f"- **{l}** ({lang_avgs[l]:.1f}/10): Language support needs improvement")
    
    report.append("\n### General Recommendations")
    report.append("1. **Irrelevant Query Detection**: Bot should consistently reject off-topic queries")
    report.append("2. **Multilingual Support**: Hindi Devanagari and Gujarati need better handling")
    report.append("3. **Product Return**: More queries should return structured product cards")
    report.append("4. **Suggestion Generation**: Ensure follow-up suggestions are always provided")
    report.append("5. **Context Retention**: Conversation history should maintain context across turns")
    report.append("6. **Complaint Handling**: Bot should show empathy and provide clear resolution steps")
    
    # ===== CRAWL ANALYSIS =====
    report.append("\n\n## Crawling Analysis\n")
    report.append("### Crawl Success Rate")
    report.append("| Attempt | Site | Result | Reason |")
    report.append("|---------|------|--------|--------|")
    report.append("| Round 1 | Boat Lifestyle | FAILED (0 pages) | JS-heavy SPA - httpx cannot render JavaScript |")
    report.append("| Round 1 | Sugar Cosmetics | FAILED (0 pages) | JS-heavy SPA |")
    report.append("| Round 1 | Mokobara | FAILED (0 pages) | JS-heavy SPA |")
    report.append("| Round 2 | 10 Shopify stores | FAILED (0 pages) | 10 simultaneous crawls caused OOM crash |")
    report.append("| Round 3 | Beardbrand | SUCCESS (57 pages) | Sequential crawl, SSR content available |")
    report.append("| Round 3 | Death Wish Coffee | SUCCESS (185 pages) | Sequential crawl, rich content |")
    report.append("| Round 3 | Tentree | SUCCESS (200 pages) | Sequential crawl, hit page quota |")
    report.append("\n**Key Crawl Findings:**")
    report.append("- Crawler uses httpx (plain HTTP), NO headless browser - all JS-heavy sites fail silently")
    report.append("- Running 10+ crawls simultaneously crashes the API container (OOM)")
    report.append("- Sequential crawling of 1-2 sites at a time works reliably")
    report.append("- Sites with sitemaps get discovered and crawled even if main page is JS-heavy")
    report.append("- Background task pattern means container restarts kill active crawls")
    
    report_text = "\n".join(report)
    
    with open("CHATBOT_TEST_REPORT_V2.md", "w", encoding="utf-8") as f:
        f.write(report_text)
    
    print(f"\n  Report saved to CHATBOT_TEST_REPORT_V2.md")
    return report_text


# ============================================================
# Main Test Runner
# ============================================================
def main():
    global all_keys_exhausted
    
    start_time = datetime.now()
    print("=" * 70)
    print("COMPREHENSIVE CHATBOT TESTING - ROUND 2")
    print(f"Testing {len(ALL_BOTS)} bots with 43 queries each")
    print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    token = login()
    print(f"Logged in successfully\n")
    
    all_results = []
    
    for bot_idx, bot in enumerate(ALL_BOTS):
        if all_keys_exhausted:
            print(f"\n>>> All GROQ keys exhausted. Stopping.")
            break
        
        print(f"\n{'='*60}")
        print(f"[{bot_idx+1}/{len(ALL_BOTS)}] Testing: {bot['name']} ({bot['category']})")
        print(f"  URL: {bot['url']} | Pages: {bot['pages']}")
        print(f"{'='*60}")
        
        queries = get_queries_for_bot(bot["name"], bot["category"])
        session_id = None
        rate_limit_retries = 0
        
        for q_idx, query in enumerate(queries):
            if all_keys_exhausted:
                break
            
            # Handle session context
            if query["type"] == "context_start":
                session_id = f"session-{bot['name']}-{int(time.time())}"
            current_session = session_id if query["type"] in ["context_start", "context_followup", "context_summary"] else None
            
            print(f"  [{q_idx+1}/{len(queries)}] {query['type']}({query['lang']}): {query['text'][:50]}...", end=" ")
            
            response = send_chat_message(bot["id"], query["text"], current_session)
            
            # Handle rate limiting
            if response.get("is_rate_limited"):
                print("RATE LIMITED!", end=" ")
                if switch_groq_key():
                    # Re-login after restart
                    token = login()
                    # Retry this query
                    print("Retrying...", end=" ")
                    response = send_chat_message(bot["id"], query["text"], current_session)
                    if response.get("is_rate_limited"):
                        print("Still limited!")
                    else:
                        print(f"OK ({len(response.get('content',''))} chars)")
                else:
                    print("ALL KEYS EXHAUSTED")
                    break
            else:
                content_len = len(response.get("content", ""))
                if response.get("error"):
                    print(f"ERROR: {response['error'][:50]}")
                else:
                    print(f"OK ({content_len} chars)")
            
            # Evaluate
            ev = evaluate_response(query["type"], response, query["lang"], bot["category"])
            
            all_results.append({
                "bot_name": bot["name"],
                "bot_id": bot["id"],
                "category": bot["category"],
                "query_type": query["type"],
                "lang": query["lang"],
                "query": query["text"],
                "response": {
                    "content": response.get("content", "")[:500],
                    "sources_count": len(response.get("sources", [])),
                    "products_count": len(response.get("products", [])),
                    "suggestions": response.get("suggestions", []),
                    "error": response.get("error"),
                    "is_rate_limited": response.get("is_rate_limited", False),
                },
                "eval": ev,
            })
            
            time.sleep(DELAY_BETWEEN_MSGS)
        
        # Save intermediate results
        with open("test_results_v2_intermediate.json", "w", encoding="utf-8") as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False, default=str)
        
        bot_valid = [r for r in all_results if r["bot_name"] == bot["name"] and r["eval"]["score"] >= 0]
        if bot_valid:
            bot_avg = sum(r["eval"]["score"] for r in bot_valid) / len(bot_valid)
            print(f"\n  >>> {bot['name']} avg score: {bot_avg:.1f}/10 ({len(bot_valid)} queries)")
    
    # Generate report
    print(f"\n{'='*60}")
    print("GENERATING REPORT...")
    print(f"{'='*60}")
    
    generate_report(all_results, start_time)
    
    # Save raw data
    with open("test_results_v2_raw.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False, default=str)
    print(f"  Raw data saved to test_results_v2_raw.json")
    
    # Final summary
    valid = [r for r in all_results if r["eval"]["score"] >= 0]
    if valid:
        overall_avg = sum(r["eval"]["score"] for r in valid) / len(valid)
        print(f"\n{'='*60}")
        print(f"FINAL: {len(all_results)} queries, {len(valid)} scored, avg: {overall_avg:.1f}/10")
        print(f"{'='*60}")


if __name__ == "__main__":
    main()
