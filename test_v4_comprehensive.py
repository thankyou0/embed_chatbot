"""
Comprehensive Chatbot Testing Suite v4 — OpenRouter + Full Algorithm Analysis
===============================================================================
Tests ALL aspects of the chatbot system with maximum query coverage.
Uses OpenRouter (Gemini 2.0 Flash) as primary — no rate limits.

Categories tested:
  1. Greetings & casual conversation
  2. Product browsing (general + specific)
  3. Price filtering (under/above/between)
  4. Color/attribute filtering
  5. Non-product queries (policies, contact, shipping)
  6. Irrelevant query rejection
  7. Unsupported language rejection
  8. Missing info detection (fabrication check)
  9. Suggestion quality
  10. Continuation/follow-up queries
  11. Romanized text (transliteration)
  12. Mixed-language queries
  13. Ambiguous/vague queries
  14. Comparison queries
  15. Edge cases (empty, single word, special chars)
  16. Currency/price format validation

Bots: ramraj, kriyanta, zevaramaze, beardbrand, deathwish, tentree
"""
import requests
import json
import time
import sys
import os
import re
import io
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

# Fix Windows UTF-8 encoding
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# ============================================================
# Configuration
# ============================================================
BASE_URL = "http://localhost:8000/api/v1"
EMAIL = "max@gmail.com"
PASSWORD = "12345678"

DELAY_BETWEEN_MSGS = 1.5  # OpenRouter = no rate limits, can go faster
DELAY_BETWEEN_BOTS = 3
consecutive_rate_limits = 0
MAX_CONSECUTIVE_RATE_LIMITS = 15
all_keys_exhausted = False


def handle_rate_limit() -> bool:
    global consecutive_rate_limits, all_keys_exhausted
    consecutive_rate_limits += 1
    if consecutive_rate_limits >= MAX_CONSECUTIVE_RATE_LIMITS:
        all_keys_exhausted = True
        print(f"\n  >>> {MAX_CONSECUTIVE_RATE_LIMITS} consecutive rate limits — stopping <<<")
        return False
    wait = min(20, 3 * consecutive_rate_limits)
    print(f"  Rate limited (#{consecutive_rate_limits}) — waiting {wait}s...")
    time.sleep(wait)
    return True


def reset_rate_limit_counter():
    global consecutive_rate_limits
    consecutive_rate_limits = 0


# ============================================================
# Bot Configuration — diverse language setups
# ============================================================
BOTS_TO_TEST = [
    {
        "id": "182f88cd-02d8-4c94-824d-b41432847400",
        "name": "ramraj",
        "category": "Fashion/Clothing (Indian)",
        "set_languages": ["en", "gu"],
        "products": ["shirts", "dhotis", "cotton shirts", "formal shirts", "kurta"],
        "brand_keywords": ["ramraj", "cotton", "shirt", "clothing"],
        "currency": "INR",
    },
    {
        "id": "1cb18dc0-4909-409d-ab03-0436524fcec4",
        "name": "kriyanta",
        "category": "Tech/Startup",
        "set_languages": ["en", "gu"],
        "products": ["services", "solutions", "web development", "app development"],
        "brand_keywords": ["kriyanta", "service", "tech", "develop"],
        "currency": "INR",
    },
    {
        "id": "e79b3754-006d-45d5-b21d-2391710e08ca",
        "name": "zevaramaze",
        "category": "Jewelry",
        "set_languages": ["en", "hi", "gu"],
        "products": ["bracelets", "necklaces", "rings", "earrings", "pendants"],
        "brand_keywords": ["zevara", "jewelry", "jewellery", "bracelet", "ring"],
        "currency": "INR",
    },
    {
        "id": "e23fcc6f-7a02-4b09-8d49-95c00a57d852",
        "name": "beardbrand",
        "category": "Grooming/Lifestyle",
        "set_languages": ["en"],
        "products": ["beard oil", "beard balm", "utility balm", "grooming kit", "wash"],
        "brand_keywords": ["beardbrand", "beard", "grooming", "oil", "balm"],
        "currency": "USD",
    },
    {
        "id": "99fc3604-99e7-4cd0-a2a6-509ac08d9fd0",
        "name": "deathwish",
        "category": "Coffee/Beverage",
        "set_languages": ["en", "hi"],
        "products": ["coffee", "ground coffee", "K-cups", "death cups", "cold brew"],
        "brand_keywords": ["deathwish", "death wish", "coffee", "brew"],
        "currency": "USD",
    },
    {
        "id": "799637f9-391b-4b9d-84cb-5fdd17cdf109",
        "name": "tentree",
        "category": "Fashion/Eco-friendly",
        "set_languages": ["en", "gu"],
        "products": ["t-shirts", "hoodies", "joggers", "jackets", "sweaters"],
        "brand_keywords": ["tentree", "sustainable", "eco", "organic"],
        "currency": "USD",
    },
]


# ============================================================
# API Helpers
# ============================================================
def login() -> str:
    for attempt in range(5):
        try:
            resp = requests.post(f"{BASE_URL}/auth/login",
                                 json={"email": EMAIL, "password": PASSWORD}, timeout=30)
            resp.raise_for_status()
            return resp.json()["access_token"]
        except:
            if attempt < 4:
                time.sleep(5)
            else:
                raise


def configure_bot_languages(token: str, bot_id: str, languages: List[str]) -> bool:
    try:
        resp = requests.patch(
            f"{BASE_URL}/chatbots/{bot_id}/appearance",
            json={"languages": languages},
            headers={"Authorization": f"Bearer {token}"},
            timeout=15
        )
        return resp.status_code in [200, 201]
    except:
        return False


def send_chat_message(token: str, chatbot_id: str, message: str, session_id: Optional[str] = None) -> Dict:
    data = {"message": message, "is_preview": "true"}
    if session_id:
        data["session_id"] = session_id

    result = {
        "content": "", "sources": [], "suggestions": [], "products": [],
        "session_id": None, "error": None, "status_messages": [],
        "is_rate_limited": False, "is_irrelevant": False, "is_missing_info": False,
    }

    try:
        resp = requests.post(
            f"{BASE_URL}/chat/{chatbot_id}/message/stream",
            headers={"Authorization": f"Bearer {token}"},
            data=data, stream=True, timeout=90
        )
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        result["error"] = str(e)
        return result

    try:
        for line in resp.iter_lines(decode_unicode=True):
            if not line or not line.startswith("data: "):
                continue
            try:
                event = json.loads(line[6:])
                etype = event.get("type")
                if etype == "session":
                    result["session_id"] = event.get("session_id")
                elif etype == "status":
                    result["status_messages"].append(event.get("status", ""))
                elif etype == "content":
                    result["content"] += event.get("content", "")
                elif etype == "done":
                    result["sources"] = event.get("sources", [])
                    result["suggestions"] = event.get("suggestions", [])
                    result["products"] = event.get("products", [])
                    result["is_irrelevant"] = event.get("is_irrelevant", False)
                    result["is_missing_info"] = event.get("is_missing_info", False)
                elif etype == "error":
                    result["error"] = event.get("error", "Unknown error")
            except json.JSONDecodeError:
                pass
    except Exception as e:
        result["error"] = f"Stream error: {str(e)}"

    # Detect rate limit from response content
    full_text = (result["content"] + " " + str(result.get("error", ""))).lower()
    rate_phrases = ["rate limit", "too many requests", "try again in a few minutes",
                    "getting a lot of requests", "rate_limit_exceeded", "429"]
    if any(p in full_text for p in rate_phrases):
        result["is_rate_limited"] = True

    return result


# ============================================================
# MASSIVE Query Builder — analyzes EVERY aspect of the algorithm
# ============================================================
def build_queries_for_bot(bot: Dict) -> List[Dict]:
    """Build exhaustive test queries per bot."""
    langs = bot["set_languages"]
    p = bot["products"]
    name = bot["name"]
    queries = []

    has_en = "en" in langs
    has_hi = "hi" in langs
    has_gu = "gu" in langs

    # ==== 1. GREETINGS (5-8 per bot, multi-language) ====
    if has_en:
        queries.append({"type": "greeting", "lang": "en", "query": "Hi there!"})
        queries.append({"type": "greeting", "lang": "en", "query": "Hey, what's up?"})
        queries.append({"type": "greeting", "lang": "en", "query": "Good morning! Can you help me?"})
    if has_hi:
        queries.append({"type": "greeting", "lang": "hi", "query": "नमस्ते!"})
        queries.append({"type": "greeting", "lang": "hi", "query": "हेलो, कैसे हो?"})
    if has_gu:
        queries.append({"type": "greeting", "lang": "gu", "query": "નમસ્તે! કેમ છો?"})
        queries.append({"type": "greeting", "lang": "gu", "query": "હેલો! મને હેલ્પ કરો"})

    # ==== 2. PRODUCT BROWSING - General (6-10) ====
    if has_en:
        queries.append({"type": "product_browse", "lang": "en", "query": f"Show me your {p[0]}"})
        queries.append({"type": "product_browse", "lang": "en", "query": f"What {p[1]} do you have?"})
        queries.append({"type": "product_browse", "lang": "en", "query": f"I want to browse your collection"})
        queries.append({"type": "product_browse", "lang": "en", "query": f"What's popular right now?"})
        queries.append({"type": "product_browse", "lang": "en", "query": f"Show me your best sellers"})
    if has_hi:
        queries.append({"type": "product_browse", "lang": "hi", "query": f"आपके पास कौन से {p[0]} हैं?"})
        queries.append({"type": "product_browse", "lang": "hi", "query": f"मुझे {p[1]} दिखाओ"})
        queries.append({"type": "product_browse", "lang": "hi", "query": "सबसे ज्यादा बिकने वाले products दिखाओ"})
    if has_gu:
        queries.append({"type": "product_browse", "lang": "gu", "query": f"તમારા {p[0]} બતાવો"})
        queries.append({"type": "product_browse", "lang": "gu", "query": f"શું {p[1]} available છે?"})
        queries.append({"type": "product_browse", "lang": "gu", "query": "તમારા best selling products કયા છે?"})

    # ==== 3. SPECIFIC PRODUCT SEARCH (5-7) ====
    if has_en:
        queries.append({"type": "specific_product", "lang": "en", "query": f"I need a premium {p[0]}"})
        queries.append({"type": "specific_product", "lang": "en", "query": f"Looking for {p[2]} for daily use"})
        queries.append({"type": "specific_product", "lang": "en", "query": f"Do you have {p[3]} in stock?"})
    if has_hi:
        queries.append({"type": "specific_product", "lang": "hi", "query": f"मुझे {p[0]} चाहिए जो comfortable हो"})
    if has_gu:
        queries.append({"type": "specific_product", "lang": "gu", "query": f"મને {p[0]} જોઈએ છે"})

    # ==== 4. PRICE FILTERING (8-12) ====
    if has_en:
        queries.append({"type": "price_filter", "lang": "en", "query": f"Show me {p[0]} under $50"})
        queries.append({"type": "price_filter", "lang": "en", "query": f"{p[0]} between $20 and $100"})
        queries.append({"type": "price_filter", "lang": "en", "query": f"What's the cheapest {p[1]}?"})
        queries.append({"type": "price_filter", "lang": "en", "query": f"Budget {p[0]} under 500"})
        queries.append({"type": "price_filter", "lang": "en", "query": f"Most expensive {p[0]} you have?"})
    if has_hi:
        queries.append({"type": "price_filter", "lang": "hi", "query": f"500 रुपये से कम के {p[0]} बताओ"})
        queries.append({"type": "price_filter", "lang": "hi", "query": f"1000 से 2000 रुपये वाले {p[0]}"})
    if has_gu:
        queries.append({"type": "price_filter", "lang": "gu", "query": f"₹500 થી ઓછા {p[0]} બતાવો"})
        queries.append({"type": "price_filter", "lang": "gu", "query": f"સસ્તા {p[0]} છે?"})

    # ==== 5. COLOR/ATTRIBUTE FILTERING (5-8) ====
    if has_en:
        queries.append({"type": "color_filter", "lang": "en", "query": f"Show me {p[0]} in blue"})
        queries.append({"type": "color_filter", "lang": "en", "query": f"Do you have black {p[0]}?"})
        queries.append({"type": "color_filter", "lang": "en", "query": f"I want a red {p[1]}"})
    if has_hi:
        queries.append({"type": "color_filter", "lang": "hi", "query": f"काले रंग के {p[0]} दिखाओ"})
    if has_gu:
        queries.append({"type": "color_filter", "lang": "gu", "query": f"લાલ રંગના {p[0]} બતાવો"})

    # ==== 6. NON-PRODUCT QUERIES (8-12) ====
    if has_en:
        queries.append({"type": "non_product", "lang": "en", "query": "What is your return policy?"})
        queries.append({"type": "non_product", "lang": "en", "query": "How long does shipping take?"})
        queries.append({"type": "non_product", "lang": "en", "query": "Do you offer free delivery?"})
        queries.append({"type": "non_product", "lang": "en", "query": "What payment methods do you accept?"})
        queries.append({"type": "non_product", "lang": "en", "query": "Where are you located?"})
        queries.append({"type": "non_product", "lang": "en", "query": "Do you have a physical store?"})
    if has_hi:
        queries.append({"type": "non_product", "lang": "hi", "query": "रिटर्न पॉलिसी क्या है?"})
        queries.append({"type": "non_product", "lang": "hi", "query": "delivery कितने दिन में होती है?"})
    if has_gu:
        queries.append({"type": "non_product", "lang": "gu", "query": "રિટર્ન પોલિસી શું છે?"})
        queries.append({"type": "non_product", "lang": "gu", "query": "ડિલિવરી કેટલા દિવસમાં થાય?"})

    # ==== 7. IRRELEVANT QUERIES (8-12 — tests rejection accuracy) ====
    irrelevant_queries_en = [
        "Can you write me a Python script to sort a list?",
        "Who is the Prime Minister of India?",
        "What is the capital of France?",
        "Tell me a joke about programming",
        "Explain quantum physics to me",
        "What's the weather like today?",
        "Who won the FIFA World Cup 2022?",
        "How do I make pasta at home?",
        "What is blockchain technology?",
        "Solve this math: 25 x 48",
    ]
    irrelevant_queries_hi = [
        "भारत का प्रधानमंत्री कौन है?",
        "पायथन स्क्रिप्ट लिखो",
        "चांद पर कौन गया था?",
    ]
    irrelevant_queries_gu = [
        "ભારતના વડાપ્રધાન કોણ છે?",
        "મને એક જોક કહો",
    ]

    if has_en:
        for q in irrelevant_queries_en:
            queries.append({"type": "irrelevant", "lang": "en", "query": q})
    if has_hi:
        for q in irrelevant_queries_hi:
            queries.append({"type": "irrelevant", "lang": "hi", "query": q})
    elif has_gu:
        for q in irrelevant_queries_gu:
            queries.append({"type": "irrelevant", "lang": "gu", "query": q})

    # ==== 8. UNSUPPORTED LANGUAGE REJECTION (4-6) ====
    queries.append({"type": "unsupported_lang", "lang": "fr", "query": "Bonjour, montrez-moi vos produits les plus populaires"})
    queries.append({"type": "unsupported_lang", "lang": "ja", "query": "こんにちは、人気商品を教えてください"})
    queries.append({"type": "unsupported_lang", "lang": "es", "query": "Hola, muéstrame tus productos más vendidos"})
    queries.append({"type": "unsupported_lang", "lang": "zh", "query": "你好，给我看看你们最好的产品"})

    if not has_hi:
        queries.append({"type": "unsupported_lang_hindi", "lang": "hi", "query": f"नमस्ते! आपके पास कौन से {p[0]} हैं?"})
        queries.append({"type": "unsupported_lang_hindi", "lang": "hi", "query": "500 रुपये से कम में क्या मिलेगा?"})
    if not has_gu:
        queries.append({"type": "unsupported_lang_gujarati", "lang": "gu", "query": f"તમારી પાસે કયા {p[0]} છે?"})

    # ==== 9. MISSING INFO DETECTION (6-8 — fabrication test) ====
    if has_en:
        queries.append({"type": "missing_info", "lang": "en", "query": "Show me your product warranty certificates"})
        queries.append({"type": "missing_info", "lang": "en", "query": "What is the GSM rating of your cotton fabric?"})
        queries.append({"type": "missing_info", "lang": "en", "query": "What are your CEO's contact details?"})
        queries.append({"type": "missing_info", "lang": "en", "query": "What year was your company founded?"})
        queries.append({"type": "missing_info", "lang": "en", "query": "Can you show your ISO certification?"})
        queries.append({"type": "missing_info", "lang": "en", "query": "What's the thread count of your premium fabric?"})
    if has_hi:
        queries.append({"type": "missing_info", "lang": "hi", "query": "आपकी कंपनी का GSTIN नंबर क्या है?"})
    if has_gu:
        queries.append({"type": "missing_info", "lang": "gu", "query": "તમારી company નો GST number શું છે?"})

    # ==== 10. SUGGESTION QUALITY (3-4) ====
    if has_en:
        queries.append({"type": "suggestions_test", "lang": "en", "query": f"I'm new here, what {p[0]} do you sell?"})
        queries.append({"type": "suggestions_test", "lang": "en", "query": "What do you recommend for a gift?"})
    if has_hi:
        queries.append({"type": "suggestions_test", "lang": "hi", "query": "यहां क्या-क्या मिलता है?"})
    if has_gu:
        queries.append({"type": "suggestions_test", "lang": "gu", "query": "gift માટે શું recommend કરો?"})

    # ==== 11. ROMANIZED/TRANSLITERATED QUERIES (5-8) ====
    if has_hi:
        queries.append({"type": "romanized", "lang": "hi-Latn", "query": f"mujhe {p[0]} dikhao"})
        queries.append({"type": "romanized", "lang": "hi-Latn", "query": "saste wale products batao"})
        queries.append({"type": "romanized", "lang": "hi-Latn", "query": "kya discount chal raha hai?"})
    if has_gu:
        queries.append({"type": "romanized", "lang": "gu-Latn", "query": f"mane {p[0]} batavo"})
        queries.append({"type": "romanized", "lang": "gu-Latn", "query": "sasta wala shu chhe?"})
        queries.append({"type": "romanized", "lang": "gu-Latn", "query": "tamari best products batavo"})

    # ==== 12. MIXED LANGUAGE (4-6) ====
    if has_en and has_hi:
        queries.append({"type": "mixed_lang", "lang": "hi-mix", "query": f"Mujhe {p[0]} chahiye blue color mein"})
        queries.append({"type": "mixed_lang", "lang": "hi-mix", "query": "price range kya hai aapka?"})
    if has_en and has_gu:
        queries.append({"type": "mixed_lang", "lang": "gu-mix", "query": f"Mane {p[0]} joiye affordable wala"})
        queries.append({"type": "mixed_lang", "lang": "gu-mix", "query": "tumhare best products shu chhe?"})

    # ==== 13. AMBIGUOUS/VAGUE QUERIES (5-7) ====
    if has_en:
        queries.append({"type": "ambiguous", "lang": "en", "query": "something nice"})
        queries.append({"type": "ambiguous", "lang": "en", "query": "I need help"})
        queries.append({"type": "ambiguous", "lang": "en", "query": "What do you have?"})
        queries.append({"type": "ambiguous", "lang": "en", "query": "show me options"})
        queries.append({"type": "ambiguous", "lang": "en", "query": "gift ideas"})

    # ==== 14. COMPARISON/DECISION QUERIES (4-6) ====
    if has_en:
        queries.append({"type": "comparison", "lang": "en", "query": f"Which {p[0]} is better quality?"})
        queries.append({"type": "comparison", "lang": "en", "query": f"What's the difference between your {p[0]} and {p[1]}?"})
        queries.append({"type": "comparison", "lang": "en", "query": f"Which {p[0]} would you recommend?"})

    # ==== 15. EDGE CASES (8-12) ====
    queries.append({"type": "edge_case", "lang": "en", "query": "ok"})
    queries.append({"type": "edge_case", "lang": "en", "query": "thanks"})
    queries.append({"type": "edge_case", "lang": "en", "query": "yes"})
    queries.append({"type": "edge_case", "lang": "en", "query": "no"})
    queries.append({"type": "edge_case", "lang": "en", "query": "hmm"})
    queries.append({"type": "edge_case", "lang": "en", "query": "???"})
    queries.append({"type": "edge_case", "lang": "en", "query": "lol"})
    queries.append({"type": "edge_case", "lang": "en", "query": f"{p[0]}"})  # single product word

    # ==== 16. ABOUT BRAND (2-3) ====
    if has_en:
        queries.append({"type": "about_brand", "lang": "en", "query": f"Tell me about {name}"})
        queries.append({"type": "about_brand", "lang": "en", "query": "Who are you and what do you sell?"})
    if has_hi:
        queries.append({"type": "about_brand", "lang": "hi", "query": f"{name} के बारे में बताओ"})

    # ==== 17. NEGATIVE/COMPLAINT QUERIES (3-5) ====
    if has_en:
        queries.append({"type": "complaint", "lang": "en", "query": "Your products are too expensive"})
        queries.append({"type": "complaint", "lang": "en", "query": "I had a bad experience with my last order"})
        queries.append({"type": "complaint", "lang": "en", "query": "Why is the quality so poor?"})

    # ==== 18. PRICE FORMAT VALIDATION (4-6 — specifically tests $₹ bug fix) ====
    if has_en:
        queries.append({"type": "price_format", "lang": "en", "query": f"Show me {p[0]} with prices"})
        queries.append({"type": "price_format", "lang": "en", "query": "What's the price range of your products?"})
    if has_hi:
        queries.append({"type": "price_format", "lang": "hi", "query": f"{p[0]} का price क्या है?"})
    if has_gu:
        queries.append({"type": "price_format", "lang": "gu", "query": f"{p[0]} ની price શું છે?"})

    return queries


# ============================================================
# Evaluation Engine
# ============================================================
def evaluate_response(query: Dict, response: Dict, bot: Dict) -> Dict:
    ev = {
        "score": 0, "max_score": 10, "issues": [],
        "passed": True, "notes": "",
        "language_correct": True, "suggestion_quality": None,
        "missing_info_detected": None, "products_with_issues": [],
        "price_format_ok": True,
    }

    content = response.get("content", "").strip()
    error = response.get("error")
    products = response.get("products", [])
    suggestions = response.get("suggestions", [])
    is_rate_limited = response.get("is_rate_limited", False)
    is_irrelevant = response.get("is_irrelevant", False)
    is_missing_info = response.get("is_missing_info", False)
    qtype = query["type"]
    qlang = query["lang"]
    allowed_langs = bot["set_languages"]

    if is_rate_limited:
        ev["score"] = -1
        ev["issues"].append("RATE_LIMITED")
        ev["notes"] = "Skipped - rate limit"
        return ev

    if error and not content:
        ev["score"] = 0
        ev["passed"] = False
        ev["issues"].append(f"ERROR: {str(error)[:100]}")
        return ev

    if not content:
        ev["score"] = 0
        ev["passed"] = False
        ev["issues"].append("Empty response")
        return ev

    content_lower = content.lower()
    has_devanagari = any('\u0900' <= c <= '\u097F' for c in content)
    has_gujarati = any('\u0A80' <= c <= '\u0AFF' for c in content)

    # ── Language correctness ──
    base_lang = qlang.split("-")[0]  # "hi-Latn" -> "hi", "gu-mix" -> "gu"
    if base_lang == "hi" and "hi" in allowed_langs:
        if not has_devanagari and qlang not in ("hi-Latn", "hi-mix"):
            ev["language_correct"] = False
            ev["issues"].append("Expected Hindi response but got non-Hindi")
    elif base_lang == "gu" and "gu" in allowed_langs:
        if not has_gujarati and qlang not in ("gu-Latn", "gu-mix"):
            ev["language_correct"] = False
            ev["issues"].append("Expected Gujarati response but got non-Gujarati")

    # CRITICAL: Wrong script (Hindi→Gujarati or vice versa)
    if base_lang == "hi" and "hi" in allowed_langs and has_gujarati and not has_devanagari:
        ev["language_correct"] = False
        ev["issues"].append("CRITICAL: Hindi query got GUJARATI response")
        ev["score"] = 1
        ev["passed"] = False
        return ev
    if base_lang == "gu" and "gu" in allowed_langs and has_devanagari and not has_gujarati:
        ev["language_correct"] = False
        ev["issues"].append("CRITICAL: Gujarati query got HINDI response")
        ev["score"] = 1
        ev["passed"] = False
        return ev

    # ── Price format validation (check for $₹ double symbol) ──
    for prod in products:
        price = str(prod.get("price", ""))
        if re.search(r'[\$€£].*₹|₹.*[\$€£]', price):
            ev["price_format_ok"] = False
            ev["issues"].append(f"PRICE BUG: Double currency symbol in '{price}'")
        if re.search(r'^(inr|rs)', price, re.IGNORECASE):
            ev["price_format_ok"] = False
            ev["issues"].append(f"PRICE FORMAT: Text prefix in '{price}'")

    # ── Type-specific evaluation ──
    if qtype == "greeting":
        ev["score"] = 8 if len(content) > 20 else 5
        if suggestions:
            ev["score"] = min(10, ev["score"] + 1)
        if ev["language_correct"]:
            ev["score"] = min(10, ev["score"] + 1)

    elif qtype in ("product_browse", "specific_product"):
        if products:
            ev["score"] = 9
            ev["notes"] = f"{len(products)} products"
            for prod in products[:5]:
                issues = []
                if not prod.get("image"):
                    issues.append("missing_image")
                if not prod.get("price"):
                    issues.append("missing_price")
                if not prod.get("name") or prod.get("name") == "Product":
                    issues.append("generic_name")
                if issues:
                    ev["products_with_issues"].append({"name": prod.get("name", "?")[:30], "issues": issues})
            if ev["products_with_issues"]:
                ev["score"] = max(7, ev["score"] - 1)
        elif any(kw in content_lower for kw in ["product", "item", "available", "here are", "check out", "collection"]):
            ev["score"] = 6
            ev["notes"] = "Mentioned products textually"
        else:
            ev["score"] = 4
            ev["issues"].append("No products returned or mentioned")

    elif qtype in ("price_filter", "price_format"):
        price_ok = any(re.search(p, content_lower) for p in [r'₹\d+', r'\$\d+', r'\d+', r'price', r'range', r'cost'])
        if products and price_ok:
            ev["score"] = 9
        elif products:
            ev["score"] = 7
        elif price_ok:
            ev["score"] = 6
        else:
            ev["score"] = 4
            ev["issues"].append("No price info")
        if not ev["price_format_ok"]:
            ev["score"] = max(2, ev["score"] - 3)

    elif qtype == "color_filter":
        if products:
            ev["score"] = 8
            ev["notes"] = f"{len(products)} products"
        elif any(kw in content_lower for kw in ["color", "colour", "available", "option"]):
            ev["score"] = 6
        else:
            ev["score"] = 4

    elif qtype == "non_product":
        policy_kw = ["return", "shipping", "delivery", "refund", "policy", "exchange",
                      "days", "business days", "payment", "free", "located", "store", "address"]
        if any(kw in content_lower for kw in policy_kw):
            ev["score"] = 8
        elif is_missing_info or "don't have" in content_lower:
            ev["score"] = 7
            ev["notes"] = "Correctly flagged as missing info"
        else:
            ev["score"] = 4

    elif qtype == "irrelevant":
        rejection_kw = ["can't help", "cannot help", "not related", "outside",
                         "only help", "specifically", "can only", "don't have info",
                         "not supported", "sorry", "i can only"]
        is_rejected = is_irrelevant or any(kw in content_lower for kw in rejection_kw)
        gives_answer = len(content) > 200  # Long responses likely include the answer
        
        if is_rejected and not gives_answer:
            ev["score"] = 10
            ev["notes"] = "Correctly rejected"
        elif is_rejected:
            ev["score"] = 7
            ev["notes"] = "Rejected but response too long (may include partial answer)"
        elif len(content) < 100:
            ev["score"] = 6
            ev["notes"] = "Short response (likely deflection)"
        else:
            ev["score"] = 2
            ev["passed"] = False
            ev["issues"].append("Bot answered irrelevant question instead of rejecting")

    elif qtype in ("unsupported_lang", "unsupported_lang_hindi", "unsupported_lang_gujarati"):
        rejection_kw = ["not supported", "supported language", "can help you in",
                         "please ask", "configured", "available in"]
        if any(kw in content_lower for kw in rejection_kw):
            ev["score"] = 10
            ev["notes"] = "Correctly rejected unsupported language"
        elif is_irrelevant:
            ev["score"] = 8
            ev["notes"] = "Flagged irrelevant (language detection worked)"
        elif any(kw in content_lower for kw in ["sorry", "apolog", "cannot"]):
            ev["score"] = 6
            ev["notes"] = "Apologetic but unclear rejection"
        else:
            ev["score"] = 1
            ev["passed"] = False
            ev["issues"].append("CRITICAL: No language rejection")

    elif qtype == "missing_info":
        if is_missing_info:
            ev["score"] = 10
            ev["missing_info_detected"] = True
            ev["notes"] = "Correctly flagged [[MISSING_INFO]]"
        elif any(kw in content_lower for kw in ["don't have", "not available", "no information",
                                                   "couldn't find", "not in our", "i don't", "unable"]):
            ev["score"] = 7
            ev["missing_info_detected"] = True
            ev["notes"] = "Honestly said info unavailable (no marker)"
        else:
            ev["score"] = 2
            ev["missing_info_detected"] = False
            ev["passed"] = False
            ev["issues"].append("Bot fabricated info instead of flagging missing")

    elif qtype == "suggestions_test":
        if suggestions and len(suggestions) >= 2:
            sq = _evaluate_suggestions(suggestions, content, bot)
            ev["suggestion_quality"] = sq
            ev["score"] = sq["score"]
            ev["notes"] = sq["notes"]
            if sq["issues"]:
                ev["issues"].extend(sq["issues"])
        elif suggestions:
            ev["score"] = 5
        else:
            ev["score"] = 3
            ev["issues"].append("No suggestions returned")

    elif qtype == "romanized":
        # Romanized input should be understood and responded to in the correct language
        if content and len(content) > 20:
            ev["score"] = 8
            ev["notes"] = "Response received for romanized input"
        else:
            ev["score"] = 4
            ev["issues"].append("Poor response to romanized input")

    elif qtype == "mixed_lang":
        if content and len(content) > 20:
            ev["score"] = 7
            ev["notes"] = "Handled mixed-language query"
        else:
            ev["score"] = 4

    elif qtype == "ambiguous":
        if content and len(content) > 20:
            ev["score"] = 7
            ev["notes"] = "Handled ambiguous query"
            if products or suggestions:
                ev["score"] = 8
        else:
            ev["score"] = 4

    elif qtype == "comparison":
        if products and len(products) >= 2:
            ev["score"] = 9
            ev["notes"] = f"Showed {len(products)} products for comparison"
        elif len(content) > 50:
            ev["score"] = 7
            ev["notes"] = "Textual comparison"
        else:
            ev["score"] = 4

    elif qtype == "edge_case":
        if content and len(content) > 5:
            ev["score"] = 7
            ev["notes"] = "Handled edge case gracefully"
        else:
            ev["score"] = 5

    elif qtype == "about_brand":
        brand_kw = bot.get("brand_keywords", [])
        if any(kw in content_lower for kw in brand_kw):
            ev["score"] = 8
        elif len(content) > 50:
            ev["score"] = 7
        else:
            ev["score"] = 5

    elif qtype == "complaint":
        sympathetic_kw = ["sorry", "understand", "apologize", "help", "assist", "concern", "feedback"]
        if any(kw in content_lower for kw in sympathetic_kw):
            ev["score"] = 8
            ev["notes"] = "Empathetic response"
        elif len(content) > 30:
            ev["score"] = 6
        else:
            ev["score"] = 4

    else:
        ev["score"] = 5

    ev["passed"] = ev["score"] >= 5
    return ev


def _evaluate_suggestions(suggestions: List, content: str, bot: Dict) -> Dict:
    result = {"score": 5, "notes": "", "issues": [], "details": []}
    products = bot["products"]

    if not suggestions:
        result["score"] = 0
        result["issues"].append("No suggestions")
        return result

    total_quality = 0
    for s in suggestions[:3]:
        sug_text = s if isinstance(s, str) else str(s)
        sug_lower = sug_text.lower()
        quality = 0
        notes = []

        words = sug_text.split()
        if 4 <= len(words) <= 18:
            quality += 2
        elif len(words) < 4:
            notes.append("too_short")
        else:
            notes.append("too_long")

        if any(p.lower() in sug_lower for p in products):
            quality += 3
            notes.append("product_relevant")
        elif any(kw in sug_lower for kw in ["product", "show", "price", "recommend", "popular", "best",
                                              "color", "size", "discount", "delivery", "return", "collection"]):
            quality += 2
            notes.append("generic_useful")
        else:
            quality += 1

        if any(kw in sug_lower for kw in ["i", "my", "me", "show me", "can you", "do you", "what", "how", "which"]):
            quality += 1
            notes.append("user_perspective")

        total_quality += quality
        result["details"].append({"text": sug_text[:50], "quality": quality, "notes": notes})

    avg = total_quality / min(len(suggestions), 3)
    if avg >= 5:
        result["score"] = 10
        result["notes"] = "Excellent suggestions"
    elif avg >= 4:
        result["score"] = 8
        result["notes"] = "Good suggestions"
    elif avg >= 3:
        result["score"] = 6
        result["notes"] = "Decent suggestions"
    else:
        result["score"] = 4
        result["notes"] = "Weak suggestions"
        result["issues"].append("Low relevance")
    return result


# ============================================================
# Main Test Runner
# ============================================================
def run_tests():
    global all_keys_exhausted

    print("=" * 70)
    print("CHATBOT TEST SUITE v4 — OpenRouter + Full Algorithm Analysis")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Bots: {len(BOTS_TO_TEST)} | Provider: OpenRouter (Gemini 2.0 Flash)")
    print("=" * 70)

    token = login()
    print(f"Logged in successfully")

    # Configure languages
    print("\n--- Configuring bot languages ---")
    for bot in BOTS_TO_TEST:
        ok = configure_bot_languages(token, bot["id"], bot["set_languages"])
        status = "OK" if ok else "WARN"
        print(f"  {bot['name']}: {bot['set_languages']} [{status}]")
    time.sleep(2)

    # Count total queries
    total_q = sum(len(build_queries_for_bot(b)) for b in BOTS_TO_TEST)
    print(f"\nTotal queries planned: {total_q}")

    all_results = []
    query_counter = 0

    for bot_idx, bot in enumerate(BOTS_TO_TEST):
        if all_keys_exhausted:
            break

        queries = build_queries_for_bot(bot)
        print(f"\n{'='*60}")
        print(f"BOT {bot_idx+1}/{len(BOTS_TO_TEST)}: {bot['name']} ({bot['category']})")
        print(f"Languages: {bot['set_languages']} | Queries: {len(queries)}")
        print(f"{'='*60}")

        bot_result = {
            "name": bot["name"],
            "bot_id": bot["id"],
            "category": bot["category"],
            "configured_languages": bot["set_languages"],
            "query_results": [],
        }

        session_id = None

        for q_idx, query in enumerate(queries):
            if all_keys_exhausted:
                break

            query_counter += 1
            qtype = query["type"]
            qlang = query["lang"]
            qtext = query["query"]

            print(f"\n  [{query_counter}/{total_q}] {qtype} ({qlang}): {qtext[:55]}...")

            resp = send_chat_message(token, bot["id"], qtext, session_id)

            if resp["is_rate_limited"]:
                if not handle_rate_limit():
                    break
                resp = send_chat_message(token, bot["id"], qtext, session_id)
                if resp["is_rate_limited"]:
                    print(f"    Still rate limited, skipping")
            else:
                reset_rate_limit_counter()

            if resp.get("session_id"):
                session_id = resp["session_id"]

            evaluation = evaluate_response(query, resp, bot)

            # Print compact result
            score_str = f"{evaluation['score']}/10" if evaluation['score'] >= 0 else "SKIP"
            status = "PASS" if evaluation['passed'] else "FAIL"
            symbol = "✓" if evaluation['passed'] else "✗"
            print(f"    {symbol} {status} ({score_str})", end="")
            if evaluation.get("notes"):
                print(f" — {evaluation['notes']}", end="")
            print()
            if evaluation["issues"]:
                for issue in evaluation["issues"][:2]:
                    print(f"      ⚠ {issue}")

            bot_result["query_results"].append({
                "type": qtype,
                "lang": qlang,
                "query": qtext,
                "response_content": resp.get("content", "")[:500],
                "full_length": len(resp.get("content", "")),
                "sources_count": len(resp.get("sources", [])),
                "products_count": len(resp.get("products", [])),
                "products": [p for p in resp.get("products", [])[:5]],
                "suggestions": resp.get("suggestions", []),
                "is_irrelevant": resp.get("is_irrelevant", False),
                "is_missing_info": resp.get("is_missing_info", False),
                "error": resp.get("error"),
                "is_rate_limited": resp.get("is_rate_limited", False),
                "evaluation": evaluation,
            })

            time.sleep(DELAY_BETWEEN_MSGS)

        all_results.append(bot_result)
        if bot_idx < len(BOTS_TO_TEST) - 1:
            print(f"\n  Next bot in {DELAY_BETWEEN_BOTS}s...")
            time.sleep(DELAY_BETWEEN_BOTS)

    # Save raw data
    raw_file = "test_v4_raw_data.json"
    with open(raw_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nRaw data saved: {raw_file}")

    generate_report(all_results)


# ============================================================
# Report Generator
# ============================================================
def generate_report(all_results: List[Dict]):
    report_file = "CHATBOT_TEST_V4_REPORT.md"

    lines = []
    lines.append("# Chatbot Test Suite v4 — OpenRouter + Full Algorithm Analysis")
    lines.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**LLM Provider:** OpenRouter (google/gemini-2.0-flash-001)")
    lines.append(f"**Bots tested:** {len(all_results)}")

    total_queries = 0
    total_passed = 0
    total_failed = 0
    total_skipped = 0
    type_stats = {}  # qtype -> {passed, failed, total, avg_score}
    critical_issues = []
    language_issues = []
    price_issues = []
    missing_info_results = []
    poorly_performing = []

    for bot in all_results:
        for qr in bot["query_results"]:
            ev = qr["evaluation"]
            total_queries += 1
            qtype = qr["type"]

            if qtype not in type_stats:
                type_stats[qtype] = {"passed": 0, "failed": 0, "skipped": 0, "scores": []}

            if ev["score"] == -1:
                total_skipped += 1
                type_stats[qtype]["skipped"] += 1
            elif ev["passed"]:
                total_passed += 1
                type_stats[qtype]["passed"] += 1
                type_stats[qtype]["scores"].append(ev["score"])
            else:
                total_failed += 1
                type_stats[qtype]["failed"] += 1
                type_stats[qtype]["scores"].append(ev["score"])
                poorly_performing.append({
                    "bot": bot["name"], "type": qtype, "lang": qr["lang"],
                    "query": qr["query"], "score": ev["score"],
                    "issues": ev["issues"], "response": qr["response_content"][:200],
                })

            for issue in ev.get("issues", []):
                if "CRITICAL" in issue:
                    critical_issues.append({"bot": bot["name"], "query": qr["query"][:60], "issue": issue})
            if ev.get("language_correct") is False:
                language_issues.append({"bot": bot["name"], "query": qr["query"][:60], "lang": qr["lang"], "issues": ev["issues"]})
            if not ev.get("price_format_ok", True):
                price_issues.append({"bot": bot["name"], "query": qr["query"][:60], "issues": ev["issues"]})
            if ev.get("missing_info_detected") is not None:
                missing_info_results.append({
                    "bot": bot["name"], "query": qr["query"][:50],
                    "detected": ev["missing_info_detected"], "score": ev["score"],
                })

    # ── EXECUTIVE SUMMARY ──
    pass_rate = total_passed * 100 // max(total_queries, 1)
    lines.append(f"\n## Executive Summary")
    lines.append(f"\n| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total queries | **{total_queries}** |")
    lines.append(f"| Passed (≥5/10) | **{total_passed}** ({pass_rate}%) |")
    lines.append(f"| Failed (<5/10) | **{total_failed}** ({total_failed*100//max(total_queries,1)}%) |")
    lines.append(f"| Skipped (rate limit) | {total_skipped} |")
    lines.append(f"| Critical issues | {len(critical_issues)} |")
    lines.append(f"| Language mismatches | {len(language_issues)} |")
    lines.append(f"| Price format bugs | {len(price_issues)} |")

    # ── SCORE BY QUERY TYPE ──
    lines.append(f"\n## Score Breakdown by Query Type")
    lines.append(f"\n| Query Type | Total | Passed | Failed | Avg Score | Pass Rate |")
    lines.append(f"|------------|-------|--------|--------|-----------|-----------|")
    for qtype in sorted(type_stats.keys()):
        st = type_stats[qtype]
        total = st["passed"] + st["failed"] + st["skipped"]
        avg = sum(st["scores"]) / len(st["scores"]) if st["scores"] else 0
        rate = st["passed"] * 100 // max(st["passed"] + st["failed"], 1)
        lines.append(f"| {qtype} | {total} | {st['passed']} | {st['failed']} | {avg:.1f} | {rate}% |")

    # ── PER-BOT RESULTS ──
    lines.append(f"\n## Per-Bot Results")
    for bot in all_results:
        results = bot["query_results"]
        scored = [r["evaluation"]["score"] for r in results if r["evaluation"]["score"] >= 0]
        passed = sum(1 for s in scored if s >= 5)
        failed = sum(1 for s in scored if s < 5)
        skipped = sum(1 for r in results if r["evaluation"]["score"] == -1)
        avg = sum(scored) / len(scored) if scored else 0

        lines.append(f"\n### {bot['name']} ({bot['category']})")
        lines.append(f"- **Languages:** {bot['configured_languages']}")
        lines.append(f"- **Queries:** {len(results)} | Pass: {passed} | Fail: {failed} | Skip: {skipped}")
        lines.append(f"- **Average score:** {avg:.1f}/10")
        lines.append(f"")
        lines.append(f"| # | Type | Lang | Query | Score | Status | Notes |")
        lines.append(f"|---|------|------|-------|-------|--------|-------|")
        for i, qr in enumerate(results):
            ev = qr["evaluation"]
            score_str = f"{ev['score']}/10" if ev['score'] >= 0 else "SKIP"
            status = "✅" if ev["passed"] else ("⏭️" if ev["score"] == -1 else "❌")
            notes = "; ".join(ev.get("issues", []))[:60] or ev.get("notes", "")[:60] or "-"
            q_short = qr["query"][:45].replace("|", "\\|")
            lines.append(f"| {i+1} | {qr['type']} | {qr['lang']} | {q_short} | {score_str} | {status} | {notes} |")

    # ── CRITICAL ISSUES ──
    if critical_issues:
        lines.append(f"\n## 🚨 Critical Issues ({len(critical_issues)})")
        for ci in critical_issues:
            lines.append(f"- **{ci['bot']}**: {ci['issue']} — \"{ci['query']}\"")
    else:
        lines.append(f"\n## ✅ No Critical Issues")

    # ── PRICE FORMAT ──
    lines.append(f"\n## Price Format Validation")
    if price_issues:
        lines.append(f"\n### ❌ Price Bugs Found ({len(price_issues)})")
        for pi in price_issues:
            lines.append(f"- **{pi['bot']}**: {'; '.join(pi['issues'])} — \"{pi['query']}\"")
    else:
        lines.append(f"\n### ✅ All prices correctly formatted (no $₹ double symbol)")

    # ── LANGUAGE HANDLING ──
    lines.append(f"\n## Language Handling")
    if language_issues:
        lines.append(f"\n### Mismatches ({len(language_issues)})")
        for li in language_issues:
            lines.append(f"- **{li['bot']}** ({li['lang']}): \"{li['query']}\" — {'; '.join(li['issues'][:2])}")
    else:
        lines.append(f"\n### ✅ All language handling correct")

    # Unsupported language tests
    lines.append(f"\n### Unsupported Language Rejection")
    unsup = []
    for bot in all_results:
        for qr in bot["query_results"]:
            if "unsupported_lang" in qr["type"]:
                unsup.append({
                    "bot": bot["name"], "lang": qr["lang"],
                    "query": qr["query"][:40], "score": qr["evaluation"]["score"],
                    "passed": qr["evaluation"]["passed"],
                })
    if unsup:
        lines.append(f"| Bot | Lang | Query | Score | Rejected? |")
        lines.append(f"|-----|------|-------|-------|-----------|")
        for u in unsup:
            ok = "✅" if u["score"] >= 6 else "❌"
            lines.append(f"| {u['bot']} | {u['lang']} | {u['query']} | {u['score']}/10 | {ok} |")

    # ── MISSING INFO ──
    lines.append(f"\n## Missing Info Detection")
    if missing_info_results:
        detected_count = sum(1 for m in missing_info_results if m["detected"])
        total_mi = len(missing_info_results)
        lines.append(f"\nDetection rate: **{detected_count}/{total_mi}** ({detected_count*100//max(total_mi,1)}%)")
        lines.append(f"\n| Bot | Query | Detected? | Score |")
        lines.append(f"|-----|-------|-----------|-------|")
        for mi in missing_info_results:
            det = "✅" if mi["detected"] else "❌ Fabricated"
            lines.append(f"| {mi['bot']} | {mi['query']} | {det} | {mi['score']}/10 |")

    # ── IRRELEVANT REJECTION ──
    lines.append(f"\n## Irrelevant Query Rejection")
    irr_results = []
    for bot in all_results:
        for qr in bot["query_results"]:
            if qr["type"] == "irrelevant":
                irr_results.append({
                    "bot": bot["name"], "lang": qr["lang"],
                    "query": qr["query"][:45], "score": qr["evaluation"]["score"],
                    "passed": qr["evaluation"]["passed"],
                    "response": qr["response_content"][:80],
                })
    if irr_results:
        passed_irr = sum(1 for r in irr_results if r["passed"])
        lines.append(f"\nRejection rate: **{passed_irr}/{len(irr_results)}** ({passed_irr*100//max(len(irr_results),1)}%)")
        lines.append(f"\n| Bot | Lang | Query | Score | Response Preview |")
        lines.append(f"|-----|------|-------|-------|-----------------|")
        for ir in irr_results:
            resp = ir["response"][:60].replace("|", "\\|").replace("\n", " ")
            status = "✅" if ir["passed"] else "❌"
            lines.append(f"| {ir['bot']} | {ir['lang']} | {ir['query']} | {ir['score']}/10 {status} | {resp} |")

    # ── POORLY PERFORMING ──
    lines.append(f"\n## Poorly Performing Queries (Score < 5)")
    if poorly_performing:
        type_fails = {}
        for pp in poorly_performing:
            t = pp["type"]
            if t not in type_fails:
                type_fails[t] = []
            type_fails[t].append(pp)
        for qtype, fails in sorted(type_fails.items(), key=lambda x: -len(x[1])):
            lines.append(f"\n### `{qtype}` — {len(fails)} failures")
            for f in fails[:10]:
                lines.append(f"- **{f['bot']}** ({f['lang']}): \"{f['query'][:50]}\" → {f['score']}/10")
                if f["issues"]:
                    lines.append(f"  Issues: {'; '.join(f['issues'][:3])}")
                if f["response"]:
                    lines.append(f"  Response: \"{f['response'][:80]}...\"")
    else:
        lines.append(f"\nAll queries scored ≥5/10! 🎉")

    # ── ALGORITHM HEALTH SCORECARD ──
    lines.append(f"\n## Algorithm Health Scorecard")
    lines.append(f"\n| Capability | Status | Details |")
    lines.append(f"|------------|--------|---------|")

    capabilities = [
        ("Language Detection", "unsupported_lang"),
        ("Hindi Rejection (on non-hi bots)", "unsupported_lang_hindi"),
        ("Irrelevant Query Rejection", "irrelevant"),
        ("Missing Info Detection", "missing_info"),
        ("Product Search", "product_browse"),
        ("Price Filtering", "price_filter"),
        ("Color Filtering", "color_filter"),
        ("Greetings", "greeting"),
        ("Policy/FAQ", "non_product"),
        ("Comparison Queries", "comparison"),
        ("Edge Cases", "edge_case"),
        ("Romanized Text", "romanized"),
        ("Brand Info", "about_brand"),
    ]
    for cap_name, cap_type in capabilities:
        if cap_type in type_stats:
            st = type_stats[cap_type]
            total = st["passed"] + st["failed"]
            if total > 0:
                rate = st["passed"] * 100 // total
                avg = sum(st["scores"]) / len(st["scores"]) if st["scores"] else 0
                emoji = "✅" if rate >= 80 else ("⚠️" if rate >= 50 else "❌")
                lines.append(f"| {cap_name} | {emoji} {rate}% | {st['passed']}/{total} passed, avg {avg:.1f}/10 |")
            else:
                lines.append(f"| {cap_name} | ⏭️ | All skipped |")
        else:
            lines.append(f"| {cap_name} | - | Not tested |")

    with open(report_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\n{'='*60}")
    print(f"Report: {report_file}")
    print(f"Raw data: test_v4_raw_data.json")
    print(f"\nFinal: {total_passed} passed, {total_failed} failed, {total_skipped} skipped / {total_queries} total")
    print(f"Pass rate: {pass_rate}%")
    print(f"{'='*60}")


if __name__ == "__main__":
    run_tests()
