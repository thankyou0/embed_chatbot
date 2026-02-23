"""
Comprehensive Chatbot Testing Suite v3 — Post-Fix Validation
=============================================================
Tests language handling fixes + suggestion quality + missing info detection.
Uses GROQ key rotation alternately to avoid rate limits.
Stops when all keys are exhausted.

Bots tested:
  - ramraj (en, gu) — test Hindi rejection, Gujarati response
  - kriyanta (en, gu) — test Hindi rejection
  - zevaramaze (en, hi, gu) — test all 3 languages
  - 2-3 test/crawled chatbots with custom language configs
"""
import requests
import json
import time
import sys
import os
import re
import io
from datetime import datetime
from typing import Dict, List, Optional, Any

# Fix Windows UTF-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ============================================================
# Configuration
# ============================================================
BASE_URL = "http://localhost:8000/api/v1"
EMAIL = "max@gmail.com"
PASSWORD = "12345678"

DELAY_BETWEEN_MSGS = 3  # seconds between messages
DELAY_BETWEEN_BOTS = 5  # seconds between bots
consecutive_rate_limits = 0
MAX_CONSECUTIVE_RATE_LIMITS = 10  # Stop if 10 rate limits in a row


# ============================================================
# GROQ Key Rotation — handled SERVER-SIDE (round-robin across 6 keys)
# No .env changes or container restarts needed!
# ============================================================
def handle_rate_limit() -> bool:
    """Handle rate limit by waiting. Returns False if should stop."""
    global consecutive_rate_limits
    consecutive_rate_limits += 1
    if consecutive_rate_limits >= MAX_CONSECUTIVE_RATE_LIMITS:
        print(f"\n  >>> {MAX_CONSECUTIVE_RATE_LIMITS} consecutive rate limits — stopping <<<")
        return False
    wait = min(30, 5 * consecutive_rate_limits)
    print(f"  Rate limited (#{consecutive_rate_limits}) — waiting {wait}s (server rotates keys automatically)...")
    time.sleep(wait)
    return True


def reset_rate_limit_counter():
    """Reset consecutive rate limit counter on successful response."""
    global consecutive_rate_limits
    consecutive_rate_limits = 0
# ============================================================
BOTS_TO_TEST = [
    # Main production bots
    {
        "id": "182f88cd-02d8-4c94-824d-b41432847400",
        "name": "ramraj",
        "category": "Fashion/Clothing",
        "set_languages": ["en", "gu"],  # Only English and Gujarati — Hindi should be REJECTED
        "products": ["shirts", "dhotis", "cotton shirts", "formal shirts"],
    },
    {
        "id": "1cb18dc0-4909-409d-ab03-0436524fcec4",
        "name": "kriyanta",
        "category": "Tech/Startup",
        "set_languages": ["en", "gu"],  # Only English and Gujarati
        "products": ["services", "solutions", "portfolio", "projects"],
    },
    {
        "id": "e79b3754-006d-45d5-b21d-2391710e08ca",
        "name": "zevaramaze",
        "category": "Jewelry",
        "set_languages": ["en", "hi", "gu"],  # All three languages
        "products": ["bracelets", "necklaces", "rings", "earrings"],
    },
    # Test/Crawled chatbots
    {
        "id": "e23fcc6f-7a02-4b09-8d49-95c00a57d852",
        "name": "beardbrand",
        "category": "Grooming",
        "set_languages": ["en"],  # English only
        "products": ["beard oil", "beard balm", "grooming kit", "utility balm"],
    },
    {
        "id": "99fc3604-99e7-4cd0-a2a6-509ac08d9fd0",
        "name": "deathwish",
        "category": "Coffee/Beverage",
        "set_languages": ["en", "hi"],  # English and Hindi
        "products": ["coffee", "ground coffee", "K-cups", "death cups"],
    },
    {
        "id": "799637f9-391b-4b9d-84cb-5fdd17cdf109",
        "name": "tentree",
        "category": "Fashion/Eco",
        "set_languages": ["en", "gu"],  # English and Gujarati — Hindi rejected
        "products": ["t-shirts", "hoodies", "joggers", "jackets"],
    },
]


# ============================================================
# Rate Limit Handling — key rotation is SERVER-SIDE (round-robin 6 keys)
# ============================================================
consecutive_rate_limits = 0
MAX_CONSECUTIVE_RATE_LIMITS = 10
all_keys_exhausted = False


def handle_rate_limit() -> bool:
    """Handle rate limit by waiting. Returns False if should stop."""
    global consecutive_rate_limits, all_keys_exhausted
    consecutive_rate_limits += 1
    if consecutive_rate_limits >= MAX_CONSECUTIVE_RATE_LIMITS:
        all_keys_exhausted = True
        print(f"\n  >>> {MAX_CONSECUTIVE_RATE_LIMITS} consecutive rate limits — ALL KEYS EXHAUSTED, stopping <<<")
        return False
    wait = min(30, 5 * consecutive_rate_limits)
    print(f"  Rate limited (#{consecutive_rate_limits}) — waiting {wait}s (server rotates 6 keys automatically)...")
    time.sleep(wait)
    return True


def reset_rate_limit_counter():
    global consecutive_rate_limits
    consecutive_rate_limits = 0


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
    """Set the allowed languages for a bot via the appearance API."""
    try:
        resp = requests.patch(
            f"{BASE_URL}/chatbots/{bot_id}/appearance",
            json={"languages": languages},
            headers={"Authorization": f"Bearer {token}"},
            timeout=15
        )
        if resp.status_code in [200, 201]:
            print(f"  Configured languages: {languages}")
            return True
        else:
            print(f"  Warning: Language config returned {resp.status_code}: {resp.text[:200]}")
            return False
    except Exception as e:
        print(f"  Warning: Language config failed: {e}")
        return False


def send_chat_message(chatbot_id: str, message: str, session_id: Optional[str] = None) -> Dict:
    data = {"message": message, "is_preview": "true"}
    if session_id:
        data["session_id"] = session_id

    result = {
        "content": "", "sources": [], "suggestions": [], "products": [],
        "session_id": None, "error": None, "status_messages": [],
        "is_rate_limited": False
    }

    try:
        resp = requests.post(f"{BASE_URL}/chat/{chatbot_id}/message/stream",
                             data=data, stream=True, timeout=90)
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

    # Detect rate limit
    full_text = (result["content"] + " " + str(result.get("error", ""))).lower()
    rate_phrases = ["rate limit", "too many requests", "try again in a few minutes",
                    "getting a lot of requests", "rate_limit_exceeded", "429"]
    if any(p in full_text for p in rate_phrases):
        result["is_rate_limited"] = True

    return result


# ============================================================
# Query Builder — language-aware, optimized for each bot's config
# ============================================================
def build_queries_for_bot(bot: Dict) -> List[Dict]:
    """Build test queries tailored to the bot's language config and category."""
    langs = bot["set_languages"]
    p = bot["products"]
    name = bot["name"]
    queries = []

    has_en = "en" in langs
    has_hi = "hi" in langs
    has_gu = "gu" in langs

    # ── 1. Greetings (2-3 per bot, only in supported languages) ──
    if has_en:
        queries.append({"type": "greeting", "lang": "en", "query": "Hi there! What can you help me with?"})
    if has_hi:
        queries.append({"type": "greeting", "lang": "hi", "query": "नमस्ते! आप मेरी कैसे मदद कर सकते हैं?"})
    if has_gu:
        queries.append({"type": "greeting", "lang": "gu", "query": "નમસ્તે! તમે મને કેવી રીતે મદદ કરી શકો?"})

    # ── 2. Product Browse (2-3) ──
    if has_en:
        queries.append({"type": "product_browse", "lang": "en", "query": f"Show me your best {p[0]}"})
        queries.append({"type": "product_browse", "lang": "en", "query": f"What {p[1]} do you have?"})
    if has_hi:
        queries.append({"type": "product_browse", "lang": "hi", "query": f"आपके पास कौन से {p[0]} उपलब्ध हैं?"})
    if has_gu:
        queries.append({"type": "product_browse", "lang": "gu", "query": f"તમારી પાસે કયા {p[0]} છે?"})

    # ── 3. Specific Product (2) ──
    if has_en:
        queries.append({"type": "specific_product", "lang": "en", "query": f"I'm looking for a premium {p[2]}"})
    if has_hi:
        queries.append({"type": "specific_product", "lang": "hi", "query": f"मुझे {p[0]} चाहिए जो बहुत अच्छी क्वालिटी का हो"})

    # ── 4. Price Queries (2) ──
    if has_en:
        queries.append({"type": "price_query", "lang": "en", "query": f"Show me {p[0]} under $50"})
    if has_hi:
        queries.append({"type": "price_query", "lang": "hi", "query": f"500 रुपये से कम के {p[0]} बताओ"})

    # ── 5. Non-product queries (2) ──
    if has_en:
        queries.append({"type": "non_product", "lang": "en", "query": "What is your return policy?"})
    if has_hi:
        queries.append({"type": "non_product", "lang": "hi", "query": "रिटर्न पॉलिसी क्या है?"})

    # ── 6. Irrelevant queries (2 — test rejection, one in English, one in Hindi if supported) ──
    if has_en:
        queries.append({"type": "irrelevant", "lang": "en", "query": "Can you write me a Python script to sort a list?"})
    if has_hi:
        queries.append({"type": "irrelevant", "lang": "hi", "query": "भारत का प्रधानमंत्री कौन है?"})
    elif has_gu:
        queries.append({"type": "irrelevant", "lang": "gu", "query": "ભારતના વડાપ્રધાન કોણ છે?"})

    # ── 7. Unsupported Language Tests (2-3 with NON-supported languages) ──
    # Always test French (Latin script - tricky because it looks like English to script detection)
    queries.append({"type": "unsupported_lang", "lang": "fr", "query": "Bonjour, montrez-moi vos produits les plus populaires"})
    # Test Japanese (CJK - clearly different script)
    queries.append({"type": "unsupported_lang", "lang": "ja", "query": "こんにちは、人気商品を教えてください"})
    # If Hindi is NOT supported, test Hindi as unsupported
    if not has_hi:
        queries.append({"type": "unsupported_lang_hindi", "lang": "hi", "query": "नमस्ते! आपके पास कौन से शर्ट्स उपलब्ध हैं?"})
        queries.append({"type": "unsupported_lang_hindi", "lang": "hi", "query": "500 रुपये से कम के shirts बताओ"})
    # If Gujarati is NOT supported, test Gujarati as unsupported
    if not has_gu:
        queries.append({"type": "unsupported_lang_gujarati", "lang": "gu", "query": "નમસ્તે! તમારી પાસે કયા products છે?"})

    # ── 8. Suggestion Quality Tests (2) ──
    if has_en:
        queries.append({"type": "suggestions_test", "lang": "en", "query": f"I'm new here, what kind of {p[0]} do you sell?"})
    if has_hi:
        queries.append({"type": "suggestions_test", "lang": "hi", "query": "यहां क्या-क्या मिलता है?"})

    # ── 9. Missing Info Detection (2 — queries bot likely can't answer from its data) ──
    if has_en:
        queries.append({"type": "missing_info", "lang": "en", "query": "What are the exact fabric materials and GSM for each of your products?"})
        queries.append({"type": "missing_info", "lang": "en", "query": "Can you show me your product warranty certificates?"})

    # ── 10. About Brand (1) ──
    if has_en:
        queries.append({"type": "about_brand", "lang": "en", "query": f"Tell me about {name} and what you sell"})

    return queries


# ============================================================
# Evaluation Engine
# ============================================================
def evaluate_response(query: Dict, response: Dict, bot: Dict) -> Dict:
    """Evaluate a response against expected behaviour."""
    ev = {
        "score": 0, "max_score": 10, "issues": [],
        "passed": True, "notes": "",
        "language_correct": True, "suggestion_quality": None,
        "missing_info_detected": None, "products_with_issues": []
    }

    content = response.get("content", "").strip()
    error = response.get("error")
    sources = response.get("sources", [])
    products = response.get("products", [])
    suggestions = response.get("suggestions", [])
    is_rate_limited = response.get("is_rate_limited", False)
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

    # ── Language correctness check ──
    has_devanagari = any('\u0900' <= c <= '\u097F' for c in content)
    has_gujarati = any('\u0A80' <= c <= '\u0AFF' for c in content)

    # If query is in a supported language, check response language matches
    if qlang == "hi" and "hi" in allowed_langs:
        # Expect Hindi (Devanagari) response
        if not has_devanagari:
            ev["language_correct"] = False
            ev["issues"].append("Expected Hindi (Devanagari) response but got non-Hindi")
    elif qlang == "gu" and "gu" in allowed_langs:
        # Expect Gujarati response
        if not has_gujarati:
            ev["language_correct"] = False
            ev["issues"].append("Expected Gujarati response but got non-Gujarati")
    elif qlang == "hi" and "hi" not in allowed_langs:
        # Hindi query on non-Hindi bot: expect REJECTION message
        if has_devanagari or has_gujarati:
            ev["language_correct"] = False
            ev["issues"].append("Hindi query on non-Hindi bot got non-English response (should be rejected)")
    elif qlang == "gu" and "gu" not in allowed_langs:
        if has_gujarati or has_devanagari:
            ev["language_correct"] = False
            ev["issues"].append("Gujarati query on non-Gujarati bot got script response (should be rejected)")

    # CRITICAL: If query language is supported but response is in WRONG script
    if qlang == "hi" and "hi" in allowed_langs and has_gujarati and not has_devanagari:
        ev["language_correct"] = False
        ev["issues"].append("CRITICAL: Hindi query got GUJARATI response instead of Hindi")
        ev["score"] = 1
        ev["passed"] = False
        return ev

    if qlang == "gu" and "gu" in allowed_langs and has_devanagari and not has_gujarati:
        ev["language_correct"] = False
        ev["issues"].append("CRITICAL: Gujarati query got HINDI response instead of Gujarati")
        ev["score"] = 1
        ev["passed"] = False
        return ev

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
            ev["notes"] = f"{len(products)} products returned"
            # Check product data quality
            for prod in products[:5]:
                issues = []
                if not prod.get("image"):
                    issues.append("missing_image")
                if not prod.get("price"):
                    issues.append("missing_price")
                if not prod.get("name") or prod.get("name") == "Product":
                    issues.append("generic_name")
                if prod.get("price"):
                    price = str(prod["price"])
                    if re.match(r'^(inr|rs)\s', price, re.IGNORECASE):
                        issues.append(f"inconsistent_price_format: {price}")
                if issues:
                    ev["products_with_issues"].append({"name": prod.get("name", "?"), "issues": issues})
            if ev["products_with_issues"]:
                ev["score"] = max(7, ev["score"] - 1)
                ev["issues"].append(f"{len(ev['products_with_issues'])} products have data quality issues")
        elif any(kw in content_lower for kw in ["product", "item", "available", "here are", "check out"]):
            ev["score"] = 6
            ev["notes"] = "Mentioned products textually but no carousel"
        else:
            ev["score"] = 4
            ev["issues"].append("No products returned or mentioned")

    elif qtype == "price_query":
        price_patterns = [r'₹\d+', r'\$\d+', r'\d+\s*(rs|rupees)', r'price', r'range', r'cost']
        if any(re.search(p, content_lower) for p in price_patterns) or products:
            ev["score"] = 8
        else:
            ev["score"] = 4
            ev["issues"].append("No price info in response")

    elif qtype == "non_product":
        policy_kw = ["return", "shipping", "delivery", "refund", "policy", "exchange",
                      "days", "business days", "cod", "cash"]
        if any(kw in content_lower for kw in policy_kw):
            ev["score"] = 8
        elif "missing_info" in content_lower or "[[missing_info]]" in content_lower:
            ev["score"] = 7
            ev["notes"] = "Correctly flagged as missing info"
        else:
            ev["score"] = 4
            ev["issues"].append("No policy information found")

    elif qtype == "irrelevant":
        irrelevant_marker = "[[irrelevant]]" in content_lower
        rejection_kw = ["can't help", "cannot help", "not related", "outside",
                         "don't have info", "beyond", "only help", "specifically",
                         "not supported", "sorry"]
        if irrelevant_marker or any(kw in content_lower for kw in rejection_kw):
            ev["score"] = 9
            ev["notes"] = "Correctly rejected irrelevant query"
        elif len(content) < 100:
            ev["score"] = 6
            ev["notes"] = "Short response (likely deflection)"
        else:
            ev["score"] = 2
            ev["passed"] = False
            ev["issues"].append("Bot answered irrelevant question instead of rejecting")

    elif qtype in ("unsupported_lang", "unsupported_lang_hindi", "unsupported_lang_gujarati"):
        # Expect a rejection message mentioning "not supported"
        rejection_kw = ["not supported", "supported language", "can help you in",
                         "please ask", "configured to support", "not supported for this chatbot"]
        if any(kw in content_lower for kw in rejection_kw):
            ev["score"] = 10
            ev["notes"] = "Correctly rejected unsupported language with clear message"
        elif any(kw in content_lower for kw in ["sorry", "apolog", "cannot"]):
            ev["score"] = 6
            ev["notes"] = "Apologetic but unclear rejection"
            ev["issues"].append("No clear 'not supported' language warning")
        else:
            ev["score"] = 1
            ev["passed"] = False
            ev["issues"].append("CRITICAL: No language rejection — responded in unsupported language")

    elif qtype == "suggestions_test":
        if suggestions and len(suggestions) >= 2:
            # Check suggestion quality
            suggestion_quality = _evaluate_suggestions(suggestions, content, bot)
            ev["suggestion_quality"] = suggestion_quality
            ev["score"] = suggestion_quality["score"]
            ev["notes"] = suggestion_quality["notes"]
            if suggestion_quality["issues"]:
                ev["issues"].extend(suggestion_quality["issues"])
        elif suggestions:
            ev["score"] = 5
            ev["notes"] = f"Only {len(suggestions)} suggestion(s)"
        else:
            ev["score"] = 3
            ev["issues"].append("No suggestions returned")

    elif qtype == "missing_info":
        # Expect [[MISSING_INFO]] marker or honest "I don't have" response
        missing_marker = "[[missing_info]]" in content_lower
        honest_kw = ["don't have", "not available", "don't have that info",
                      "no information", "couldn't find", "not in our", "missing"]
        if missing_marker:
            ev["score"] = 10
            ev["missing_info_detected"] = True
            ev["notes"] = "Correctly flagged [[MISSING_INFO]]"
        elif any(kw in content_lower for kw in honest_kw):
            ev["score"] = 7
            ev["missing_info_detected"] = True
            ev["notes"] = "Honestly said info not available (no marker)"
        else:
            ev["score"] = 2
            ev["missing_info_detected"] = False
            ev["passed"] = False
            ev["issues"].append("Bot fabricated info instead of flagging missing data")

    elif qtype == "about_brand":
        if len(content) > 50:
            ev["score"] = 8
        else:
            ev["score"] = 5

    else:
        ev["score"] = 5  # Default for unknown types

    ev["passed"] = ev["score"] >= 5
    return ev


def _evaluate_suggestions(suggestions: List, response_content: str, bot: Dict) -> Dict:
    """Evaluate suggestion quality — are they relevant, specific, and useful?"""
    result = {"score": 5, "notes": "", "issues": [], "details": []}
    products = bot["products"]
    bot_name = bot["name"]

    if not suggestions:
        result["score"] = 0
        result["issues"].append("No suggestions")
        return result

    total_quality = 0
    for i, s in enumerate(suggestions[:3]):
        sug_text = s if isinstance(s, str) else str(s)
        sug_lower = sug_text.lower()
        quality = 0
        notes = []

        # Length check (6-14 words ideal)
        words = sug_text.split()
        if 4 <= len(words) <= 18:
            quality += 2
        elif len(words) < 4:
            notes.append("too_short")
        else:
            notes.append("too_long")

        # Relevance to bot's domain
        product_relevant = any(p.lower() in sug_lower for p in products)
        generic_useful = any(kw in sug_lower for kw in
            ["product", "show", "price", "recommend", "popular", "best", "color",
             "size", "discount", "delivery", "return", "collection", "new", "option"])
        if product_relevant:
            quality += 3
            notes.append("product_relevant")
        elif generic_useful:
            quality += 2
            notes.append("generically_useful")
        else:
            quality += 1
            notes.append("possibly_generic")

        # Check if it's from user's perspective
        user_perspective = any(kw in sug_lower for kw in
            ["i ", "my ", "me ", "show me", "can you", "do you", "what", "how", "which"])
        if user_perspective:
            quality += 1
            notes.append("user_perspective")

        total_quality += quality
        result["details"].append({"text": sug_text, "quality": quality, "notes": notes})

    avg_quality = total_quality / min(len(suggestions), 3)
    if avg_quality >= 5:
        result["score"] = 10
        result["notes"] = "Excellent suggestions"
    elif avg_quality >= 4:
        result["score"] = 8
        result["notes"] = "Good suggestions"
    elif avg_quality >= 3:
        result["score"] = 6
        result["notes"] = "Decent suggestions"
    else:
        result["score"] = 4
        result["notes"] = "Weak suggestions"
        result["issues"].append("Suggestions lack relevance or specificity")

    return result


# ============================================================
# Main Test Runner
# ============================================================
def run_tests():
    global all_keys_exhausted

    print("=" * 70)
    print("CHATBOT COMPREHENSIVE TEST SUITE v3 — Post-Fix Validation")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Bots: {len(BOTS_TO_TEST)} | GROQ key rotation: server-side (6 keys)")
    print("=" * 70)

    # Login
    token = login()
    print(f"Logged in successfully")

    # Configure languages for each bot
    print("\n--- Configuring bot languages ---")
    for bot in BOTS_TO_TEST:
        print(f"Bot: {bot['name']} ({bot['id'][:8]})")
        configure_bot_languages(token, bot["id"], bot["set_languages"])

    # Give API a moment after config changes
    time.sleep(2)

    all_results = []

    for bot_idx, bot in enumerate(BOTS_TO_TEST):
        if all_keys_exhausted:
            print(f"\n>>> ALL KEYS EXHAUSTED — stopping test <<<")
            break

        print(f"\n{'='*60}")
        print(f"BOT {bot_idx+1}/{len(BOTS_TO_TEST)}: {bot['name']} ({bot['category']})")
        print(f"Languages: {bot['set_languages']}")
        print(f"{'='*60}")

        queries = build_queries_for_bot(bot)
        print(f"Total queries: {len(queries)}")

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

            qtype = query["type"]
            qlang = query["lang"]
            qtext = query["query"]

            print(f"\n  [{q_idx+1}/{len(queries)}] {qtype} ({qlang}): {qtext[:60]}...")

            # Send message
            resp = send_chat_message(bot["id"], qtext, session_id)

            # Handle rate limit
            if resp["is_rate_limited"]:
                success = handle_rate_limit()
                if not success:
                    break
                # Retry this query
                resp = send_chat_message(bot["id"], qtext, session_id)
                if resp["is_rate_limited"]:
                    print(f"  Still rate limited after wait, skipping")
            else:
                reset_rate_limit_counter()

            # Preserve session for follow-ups
            if resp.get("session_id"):
                session_id = resp["session_id"]

            # Evaluate
            evaluation = evaluate_response(query, resp, bot)

            # Print result summary
            score_str = f"{evaluation['score']}/10" if evaluation['score'] >= 0 else "SKIP"
            status = "PASS" if evaluation['passed'] else "FAIL"
            print(f"  → {status} ({score_str})")
            if evaluation["issues"]:
                for issue in evaluation["issues"]:
                    print(f"    ⚠ {issue}")
            if evaluation.get("notes"):
                print(f"    ℹ {evaluation['notes']}")
            if evaluation.get("language_correct") is False:
                print(f"    ❌ LANGUAGE MISMATCH")

            # Product details
            products = resp.get("products", [])
            if products:
                missing_img = sum(1 for p in products if not p.get("image"))
                missing_price = sum(1 for p in products if not p.get("price"))
                if missing_img or missing_price:
                    print(f"    📦 Products: {len(products)} total, {missing_img} missing images, {missing_price} missing prices")

            # Suggestion preview
            suggestions = resp.get("suggestions", [])
            if suggestions:
                for s in suggestions[:3]:
                    stext = s if isinstance(s, str) else str(s)
                    print(f"    💡 \"{stext[:60]}\"")

            # Store result
            bot_result["query_results"].append({
                "type": qtype,
                "lang": qlang,
                "query": qtext,
                "response_content": resp.get("content", "")[:500],
                "full_response_length": len(resp.get("content", "")),
                "sources_count": len(resp.get("sources", [])),
                "products_count": len(resp.get("products", [])),
                "products": [p if isinstance(p, dict) else {} for p in (resp.get("products", []))[:5]],
                "suggestions": suggestions,
                "error": resp.get("error"),
                "is_rate_limited": resp.get("is_rate_limited", False),
                "evaluation": evaluation,
            })

            time.sleep(DELAY_BETWEEN_MSGS)

        all_results.append(bot_result)
        if bot_idx < len(BOTS_TO_TEST) - 1:
            print(f"\n  Waiting {DELAY_BETWEEN_BOTS}s before next bot...")
            time.sleep(DELAY_BETWEEN_BOTS)

    # Save raw data
    raw_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_v3_raw_data.json")
    with open(raw_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nRaw data saved: {raw_file}")

    # Generate report
    generate_report(all_results)


# ============================================================
# Report Generator
# ============================================================
def generate_report(all_results: List[Dict]):
    report_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "CHATBOT_TEST_V3_REPORT.md")

    lines = []
    lines.append("# Chatbot Test Suite v3 — Post-Fix Validation Report")
    lines.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**Bots tested:** {len(all_results)}")

    total_queries = 0
    total_passed = 0
    total_failed = 0
    total_skipped = 0
    critical_issues = []
    language_issues = []
    suggestion_analysis = []
    missing_info_analysis = []
    product_quality_issues = []
    poorly_performing_queries = []

    for bot in all_results:
        bot_passed = 0
        bot_failed = 0
        bot_skipped = 0

        for qr in bot["query_results"]:
            ev = qr["evaluation"]
            total_queries += 1
            if ev["score"] == -1:
                total_skipped += 1
                bot_skipped += 1
            elif ev["passed"]:
                total_passed += 1
                bot_passed += 1
            else:
                total_failed += 1
                bot_failed += 1

                # Collect poorly performing queries
                poorly_performing_queries.append({
                    "bot": bot["name"],
                    "type": qr["type"],
                    "lang": qr["lang"],
                    "query": qr["query"],
                    "score": ev["score"],
                    "issues": ev["issues"],
                    "response_preview": qr["response_content"][:200],
                })

            # Collect critical issues
            for issue in ev.get("issues", []):
                if "CRITICAL" in issue:
                    critical_issues.append({
                        "bot": bot["name"], "query": qr["query"][:60],
                        "issue": issue
                    })

            # Language analysis
            if ev.get("language_correct") is False:
                language_issues.append({
                    "bot": bot["name"], "query": qr["query"][:60],
                    "lang": qr["lang"], "issues": ev["issues"]
                })

            # Suggestion analysis
            if ev.get("suggestion_quality"):
                suggestion_analysis.append({
                    "bot": bot["name"], "query": qr["query"][:60],
                    "quality": ev["suggestion_quality"]
                })

            # Missing info detection
            if ev.get("missing_info_detected") is not None:
                missing_info_analysis.append({
                    "bot": bot["name"], "query": qr["query"][:60],
                    "detected": ev["missing_info_detected"],
                    "score": ev["score"]
                })

            # Product quality
            if ev.get("products_with_issues"):
                product_quality_issues.append({
                    "bot": bot["name"], "query": qr["query"][:60],
                    "products": ev["products_with_issues"]
                })

    # ── Summary ──
    lines.append(f"\n## Summary")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total queries | {total_queries} |")
    lines.append(f"| Passed | {total_passed} ({total_passed*100//max(total_queries,1)}%) |")
    lines.append(f"| Failed | {total_failed} ({total_failed*100//max(total_queries,1)}%) |")
    lines.append(f"| Skipped (rate limit) | {total_skipped} |")

    # ── Per-Bot Results ──
    lines.append(f"\n## Per-Bot Results")
    for bot in all_results:
        results = bot["query_results"]
        passed = sum(1 for r in results if r["evaluation"]["passed"] and r["evaluation"]["score"] >= 0)
        failed = sum(1 for r in results if not r["evaluation"]["passed"] and r["evaluation"]["score"] >= 0)
        skipped = sum(1 for r in results if r["evaluation"]["score"] == -1)
        avg_score = 0
        scored = [r["evaluation"]["score"] for r in results if r["evaluation"]["score"] >= 0]
        if scored:
            avg_score = sum(scored) / len(scored)

        lines.append(f"\n### {bot['name']} ({bot['category']})")
        lines.append(f"- **Languages configured:** {bot['configured_languages']}")
        lines.append(f"- **Queries:** {len(results)} | Passed: {passed} | Failed: {failed} | Skipped: {skipped}")
        lines.append(f"- **Average score:** {avg_score:.1f}/10")
        lines.append(f"")
        lines.append(f"| # | Type | Lang | Query | Score | Status | Issues |")
        lines.append(f"|---|------|------|-------|-------|--------|--------|")
        for i, qr in enumerate(results):
            ev = qr["evaluation"]
            score_str = f"{ev['score']}/10" if ev['score'] >= 0 else "SKIP"
            status = "✅" if ev["passed"] else ("⏭️" if ev["score"] == -1 else "❌")
            issues = "; ".join(ev.get("issues", []))[:80] or "-"
            query_short = qr["query"][:50].replace("|", "\\|")
            lines.append(f"| {i+1} | {qr['type']} | {qr['lang']} | {query_short} | {score_str} | {status} | {issues} |")

    # ── Critical Issues ──
    if critical_issues:
        lines.append(f"\n## 🚨 Critical Issues")
        for ci in critical_issues:
            lines.append(f"- **{ci['bot']}**: {ci['issue']} — Query: \"{ci['query']}\"")

    # ── Language Handling Analysis ──
    lines.append(f"\n## Language Handling Analysis")
    if language_issues:
        lines.append(f"\n### ❌ Language Mismatches ({len(language_issues)})")
        for li in language_issues:
            lines.append(f"- **{li['bot']}** ({li['lang']}): \"{li['query']}\" — {'; '.join(li['issues'])}")
    else:
        lines.append(f"\n### ✅ All language handling correct!")

    # ── Unsupported Language Rejection ──
    lines.append(f"\n### Unsupported Language Rejection Tests")
    unsupported_results = []
    for bot in all_results:
        for qr in bot["query_results"]:
            if "unsupported_lang" in qr["type"]:
                unsupported_results.append({
                    "bot": bot["name"],
                    "type": qr["type"],
                    "lang": qr["lang"],
                    "query": qr["query"][:50],
                    "score": qr["evaluation"]["score"],
                    "passed": qr["evaluation"]["passed"],
                    "response": qr["response_content"][:100],
                })
    if unsupported_results:
        lines.append(f"| Bot | Lang | Query | Score | Rejected? | Response Preview |")
        lines.append(f"|-----|------|-------|-------|-----------|-----------------|")
        for ur in unsupported_results:
            rejected = "✅ Yes" if ur["score"] >= 6 else "❌ No"
            resp_preview = ur["response"][:60].replace("|", "\\|").replace("\n", " ")
            lines.append(f"| {ur['bot']} | {ur['lang']} | {ur['query'][:40]} | {ur['score']}/10 | {rejected} | {resp_preview} |")

    # ── Suggestion Quality Analysis ──
    lines.append(f"\n## Suggestion Quality Analysis")
    if suggestion_analysis:
        lines.append(f"| Bot | Query | Score | Quality | Details |")
        lines.append(f"|-----|-------|-------|---------|---------|")
        for sa in suggestion_analysis:
            q = sa["quality"]
            details = []
            for d in q.get("details", []):
                notes_str = ", ".join(d.get("notes", []))
                details.append(f"[{d.get('quality', '?')}/6] \"{d.get('text', '?')[:40]}\" ({notes_str})")
            details_str = " | ".join(details[:3])
            lines.append(f"| {sa['bot']} | {sa['query'][:30]} | {q['score']}/10 | {q['notes']} | {details_str[:80]} |")
    else:
        lines.append("No suggestion quality tests completed.")

    # ── Missing Info Detection ──
    lines.append(f"\n## Missing Info Detection")
    if missing_info_analysis:
        lines.append(f"| Bot | Query | Detected? | Score | Notes |")
        lines.append(f"|-----|-------|-----------|-------|-------|")
        for mi in missing_info_analysis:
            detected = "✅ Yes" if mi["detected"] else "❌ No (fabricated)"
            lines.append(f"| {mi['bot']} | {mi['query'][:40]} | {detected} | {mi['score']}/10 | |")
    else:
        lines.append("No missing info tests completed.")

    # ── Product Data Quality ──
    lines.append(f"\n## Product Data Quality Issues")
    if product_quality_issues:
        for pqi in product_quality_issues:
            lines.append(f"\n**{pqi['bot']}** — Query: \"{pqi['query']}\"")
            for prod in pqi["products"]:
                lines.append(f"- {prod['name']}: {', '.join(prod['issues'])}")
    else:
        lines.append("No product data quality issues found.")

    # ── Poorly Performing Queries ──
    lines.append(f"\n## Poorly Performing Queries (Score < 5)")
    if poorly_performing_queries:
        lines.append(f"\nThese query TYPES consistently fail and need attention:\n")
        # Group by type
        type_fails = {}
        for ppq in poorly_performing_queries:
            t = ppq["type"]
            if t not in type_fails:
                type_fails[t] = []
            type_fails[t].append(ppq)

        for qtype, fails in sorted(type_fails.items(), key=lambda x: -len(x[1])):
            lines.append(f"\n### `{qtype}` — {len(fails)} failure(s)")
            for f in fails:
                lines.append(f"- **{f['bot']}** ({f['lang']}): \"{f['query'][:50]}\" → Score: {f['score']}/10")
                if f["issues"]:
                    lines.append(f"  - Issues: {'; '.join(f['issues'][:3])}")
                if f["response_preview"]:
                    preview = f["response_preview"][:100].replace("\n", " ")
                    lines.append(f"  - Response: \"{preview}...\"")
    else:
        lines.append("All queries scored 5/10 or better! 🎉")

    # Write report
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\nReport saved: {report_file}")
    print(f"\nFinal Summary: {total_passed} passed, {total_failed} failed, {total_skipped} skipped out of {total_queries}")


if __name__ == "__main__":
    run_tests()
