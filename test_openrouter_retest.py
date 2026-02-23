"""
OpenRouter Multi-Key Retest
----------------------------
Goal: Fill the Call 2 data gap for Gemini models using 4 OR keys in rotation.
Also tests gemini-2.5-flash and gemini-2.5-flash-lite via OpenRouter for Call 1.

What we already have (skip):
  - Call 1: OR-gemini-2.0-flash (21/21 complete)
  - Call 1: llama-3.1-8b (21/21 × 2 runs complete)
  - Call 2: llama-3.3-70b (21/21 complete)

What we need (retest):
  - Call 1: gemini-2.5-flash via OR (Run 1 had data, testing again for confirmation)
  - Call 1: gemini-2.5-flash-lite via OR (only tested direct API before)
  - Call 2: gemini-2.0-flash via OR (only 3/21 before, credits exhausted)
  - Call 2: gemini-2.5-flash via OR (only 1/21 from direct API)
  - Call 2: gemini-2.5-flash-lite via OR (not tested in Call 2)
"""
import asyncio, httpx, json, time, re
from itertools import cycle

# ── OpenRouter key rotation (3 fresh keys — 4th old key is exhausted) ─────────
OR_KEYS = [
    "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",  # new
    "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",  # new
    "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",  # new
]
OR_KEY_CYCLE = cycle(OR_KEYS)

OR_API = "https://openrouter.ai/api/v1/chat/completions"

# ── Models to test ─────────────────────────────────────────────────────────────
CALL1_MODELS = [
    # (display_name, OpenRouter model ID)
    ("OR-gemini-2.5-flash",       "google/gemini-2.5-flash"),
    ("OR-gemini-2.5-flash-lite",  "google/gemini-2.5-flash-lite"),
]

CALL2_MODELS = [
    ("OR-gemini-2.0-flash",       "google/gemini-2.0-flash-001"),
    ("OR-gemini-2.5-flash",       "google/gemini-2.5-flash"),
    ("OR-gemini-2.5-flash-lite",  "google/gemini-2.5-flash-lite"),
]

# ── 21 test queries (same as test_model_comparison.py) ────────────────────────
TEST_QUERIES = [
    {"type": "product_browse",  "lang": "en",      "query": "Show me your best sellers",                      "bot": "deathwish",  "expected_lang": "english",        "product": True},
    {"type": "product_browse",  "lang": "hi",      "query": "मुझे ground coffee दिखाओ",                        "bot": "deathwish",  "expected_lang": "hindi",          "product": True},
    {"type": "product_browse",  "lang": "gu",      "query": "તમારા bracelets બતાવો",                          "bot": "zevaramaze", "expected_lang": "gujarati",       "product": True},
    {"type": "price_filter",    "lang": "en",      "query": "Show me coffee under $50",                       "bot": "deathwish",  "expected_lang": "english",        "product": True},
    {"type": "price_filter",    "lang": "hi",      "query": "500 रुपये से कम के coffee बताओ",                   "bot": "deathwish",  "expected_lang": "hindi",          "product": True},
    {"type": "price_filter",    "lang": "gu",      "query": "₹500 થી ઓછા bracelets બતાવો",                   "bot": "zevaramaze", "expected_lang": "gujarati",       "product": True},
    {"type": "irrelevant",      "lang": "en",      "query": "Who is the Prime Minister of India?",            "bot": "deathwish",  "expected_lang": "english",        "product": False},
    {"type": "irrelevant",      "lang": "hi",      "query": "चांद पर कौन गया था?",                            "bot": "deathwish",  "expected_lang": "hindi",          "product": False},
    {"type": "irrelevant",      "lang": "gu",      "query": "ભારતના વડાપ્રધાન કોણ છે?",                       "bot": "zevaramaze", "expected_lang": "gujarati",       "product": False},
    {"type": "missing_info",    "lang": "en",      "query": "What are your CEO's contact details?",           "bot": "deathwish",  "expected_lang": "english",        "product": False},
    {"type": "missing_info",    "lang": "hi",      "query": "आपकी कंपनी का GSTIN नंबर क्या है?",              "bot": "deathwish",  "expected_lang": "hindi",          "product": False},
    {"type": "greeting",        "lang": "en",      "query": "Hi there!",                                      "bot": "deathwish",  "expected_lang": "english",        "product": False},
    {"type": "greeting",        "lang": "hi",      "query": "नमस्ते!",                                        "bot": "deathwish",  "expected_lang": "hindi",          "product": False},
    {"type": "greeting",        "lang": "gu",      "query": "નમસ્તે! કેમ છો?",                                "bot": "zevaramaze", "expected_lang": "gujarati",       "product": False},
    {"type": "romanized",       "lang": "hi-Latn", "query": "mujhe coffee dikhao",                            "bot": "deathwish",  "expected_lang": "hindi-latin",    "product": True},
    {"type": "romanized",       "lang": "gu-Latn", "query": "mane bracelets batavo",                          "bot": "zevaramaze", "expected_lang": "gujarati-latin", "product": True},
    {"type": "non_product",     "lang": "en",      "query": "What is your return policy?",                    "bot": "deathwish",  "expected_lang": "english",        "product": False},
    {"type": "non_product",     "lang": "hi",      "query": "delivery कितने दिन में होती है?",                 "bot": "deathwish",  "expected_lang": "hindi",          "product": False},
    {"type": "ambiguous",       "lang": "en",      "query": "something nice",                                 "bot": "deathwish",  "expected_lang": "english",        "product": False},
    {"type": "edge_case",       "lang": "en",      "query": "ok",                                             "bot": "deathwish",  "expected_lang": "english",        "product": False},
    {"type": "unsupported_lang","lang": "fr",      "query": "Bonjour, montrez-moi vos produits les plus populaires", "bot": "deathwish", "expected_lang": "other", "product": True},
]

BOT_CONFIG = {
    "deathwish": {
        "name": "Death Wish Coffee",
        "products": "Premium coffee: Death Wish Ground ($19.99), Espresso Roast ($21.99), Pumpkin Chai Latte ($15.99), Cold Brew ($14.99). Categories: Ground, Whole Bean, K-Cups, Cold Brew, Merchandise.",
        "languages": ["english", "hindi"],
    },
    "zevaramaze": {
        "name": "Zevaramaze Jewelry",
        "products": "Handmade jewelry: Silver Bangle Bracelet (₹1,499), Gold Plated Charm Bracelet (₹2,999), Pearl String Bracelet (₹899), Beaded Anklet (₹599). Categories: Bracelets, Necklaces, Earrings, Anklets.",
        "languages": ["english", "hindi", "gujarati"],
    },
}

# ── Prompt builders ────────────────────────────────────────────────────────────
def build_call1_prompt(query):
    system = """\
You are a query analysis assistant. Analyze the user's message and return ONLY valid JSON.

Return exactly this JSON structure:
{
  "language": "<detected language: english|hindi|gujarati|hindi-latin|gujarati-latin|other>",
  "continuation": <true if follow-up to previous message, else false>,
  "english_query": "<translate query to clear English>",
  "product": <true if query is about products/shopping, false otherwise>
}

Language detection rules:
- "hindi": Devanagari script (हिंदी)
- "gujarati": Gujarati script (ગુજરાતી)
- "hindi-latin": Hindi written in Latin/Roman letters (e.g. "mujhe dikhao")
- "gujarati-latin": Gujarati written in Latin/Roman letters (e.g. "mane batavo")
- "english": English
- "other": Any other language

Return ONLY the JSON object. No markdown, no explanation."""
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": query},
    ]

def build_call2_prompt(query, bot_key, expected_lang):
    bot = BOT_CONFIG[bot_key]
    lang_display = expected_lang.replace("-", " ").title()
    system = f"""\
You are an AI shopping assistant chatbot for "{bot['name']}".

PRODUCT CONTEXT:
{bot['products']}

CRITICAL RULES:
1. LANGUAGE: You MUST respond in {lang_display}. The user's detected language is {expected_lang}.
2. IRRELEVANT QUERIES: If the query is NOT about products/shopping/store info, respond ONLY with:
   "[IRRELEVANT_QUERY] I can only help with questions about {bot['name']} products and services."
   (Translate this phrase to {lang_display} if the user's language is not English)
3. MISSING INFO: If you don't have specific information requested, politely say so and suggest what you CAN help with.
4. SUGGESTIONS: At the END of EVERY response (including irrelevant ones), add EXACTLY this block:
   ---SUGGESTIONS---
   suggestion 1
   suggestion 2
   suggestion 3
   ---END---
5. NO JSON: Never output raw JSON, code blocks, or technical formatting in your response.
6. Be helpful, concise, and friendly."""
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": query},
    ]

# ── LLM caller ─────────────────────────────────────────────────────────────────
async def call_llm(client: httpx.AsyncClient, model_id: str, messages: list, key: str) -> tuple[str | None, int, str]:
    """Returns (response_text, latency_ms, status). status='ok'|'rate_limited'|'error:<msg>'"""
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/embed-chatbot",
        "X-Title": "embed-chatbot-model-test",
    }
    payload = {
        "model": model_id,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 1024,
    }
    start = time.time()
    try:
        resp = await client.post(OR_API, headers=headers, json=payload, timeout=60)
        latency = int((time.time() - start) * 1000)
        if resp.status_code == 429:
            return None, latency, "rate_limited"
        if resp.status_code == 402:
            body = resp.text[:120]
            return None, latency, f"error:HTTP 402 (credits exhausted) {body}"
        if resp.status_code != 200:
            body = resp.text[:120]
            return None, latency, f"error:HTTP {resp.status_code}: {body}"
        data = resp.json()
        if "error" in data:
            return None, latency, f"error:{data['error'].get('message','unknown')[:100]}"
        text = data["choices"][0]["message"]["content"]
        return text, latency, "ok"
    except Exception as e:
        latency = int((time.time() - start) * 1000)
        return None, latency, f"error:{str(e)[:80]}"

# ── Evaluators ─────────────────────────────────────────────────────────────────
def evaluate_call1(text: str, q: dict) -> tuple[int, dict]:
    score = 0
    d = {}
    try:
        clean = re.sub(r"```(?:json)?\s*|\s*```", "", text).strip()
        parsed = json.loads(clean)
        d["json_valid"] = True
        score += 1
    except Exception:
        d["json_valid"] = False
        return score, d

    detected = parsed.get("language", "")
    d["language_correct"] = detected == q["expected_lang"]
    score += 1 if d["language_correct"] else 0

    is_product_q = q["product"]
    detected_product = parsed.get("product", None)
    d["product_intent_correct"] = (detected_product == is_product_q)
    score += 1 if d["product_intent_correct"] else 0

    eq = parsed.get("english_query", "")
    d["english_query_quality"] = "good" if len(eq) > 2 else "poor"
    score += 1 if d["english_query_quality"] == "good" else 0

    d["parsed"] = {k: parsed.get(k) for k in ["language", "continuation", "english_query", "product"]}
    return score, d

def evaluate_call2(text: str, q: dict) -> tuple[int, dict]:
    score = 0
    d = {}
    d["has_response"] = bool(text and len(text) > 5)
    score += 1 if d["has_response"] else 0
    if not d["has_response"]:
        return score, d

    lang = q["expected_lang"]
    if lang == "hindi":
        d["lang_ok"] = sum(1 for c in text if '\u0900' <= c <= '\u097F') > 5
    elif lang == "gujarati":
        d["lang_ok"] = sum(1 for c in text if '\u0A80' <= c <= '\u0AFF') > 5
    elif lang == "other":
        d["lang_ok"] = True  # Any language acceptable for unsupported lang
    else:
        d["lang_ok"] = True  # English / latin variants — hard to validate
    score += 1 if d["lang_ok"] else 0

    if q["type"] == "irrelevant":
        d["irrel_ok"] = "[IRRELEVANT_QUERY]" in text
    else:
        d["irrel_ok"] = "[IRRELEVANT_QUERY]" not in text
    score += 1 if d["irrel_ok"] else 0

    d["sugg_ok"] = "---SUGGESTIONS---" in text and "---END---" in text
    score += 1 if d["sugg_ok"] else 0

    d["no_leak"] = '{"' not in text and '"language"' not in text and '```' not in text
    score += 1 if d["no_leak"] else 0

    return score, d

# ── Test runner ────────────────────────────────────────────────────────────────
async def run_call1_models(client: httpx.AsyncClient):
    print("\n" + "=" * 76)
    print("  CALL 1 — QUERY ANALYSIS  (OpenRouter Gemini models, 21 queries each)")
    print("=" * 76)

    all_results = {}

    for display_name, model_id in CALL1_MODELS:
        print(f"\n▶ Testing {display_name}  [{model_id}]")
        scores, latencies = [], []
        json_ok_count = lang_ok_count = prod_ok_count = 0
        rate_limited = errors = 0
        key_iter = cycle(OR_KEYS)

        for i, q in enumerate(TEST_QUERIES):
            key = next(key_iter)
            msg = build_call1_prompt(q["query"])
            text, latency, status = await call_llm(client, model_id, msg, key)

            if status == "ok":
                sc, details = evaluate_call1(text, q)
                scores.append(sc)
                latencies.append(latency)
                if details.get("json_valid"):       json_ok_count += 1
                if details.get("language_correct"): lang_ok_count += 1
                if details.get("product_intent_correct"): prod_ok_count += 1
                marks = (f"JSON:{'✓' if details.get('json_valid') else '✗'} "
                         f"Lang:{'✓' if details.get('language_correct') else '✗'} "
                         f"Prod:{'✓' if details.get('product_intent_correct') else '✗'} "
                         f"EQ:{'✓' if details.get('english_query_quality')=='good' else '✗'}")
                lang_det = details.get("parsed", {}).get("language", "?")
                print(f"  Q{i+1:02}/{len(TEST_QUERIES)} [{q['type']:13}][{q['lang']:6}] {latency:5}ms | {marks} | {sc}/4 | detected={lang_det}")
            elif status == "rate_limited":
                rate_limited += 1
                print(f"  Q{i+1:02}/{len(TEST_QUERIES)} [{q['type']:13}][{q['lang']:6}] ⏳ RATE LIMITED")
            else:
                errors += 1
                print(f"  Q{i+1:02}/{len(TEST_QUERIES)} [{q['type']:13}][{q['lang']:6}] ❌ {status[6:60]}")

            await asyncio.sleep(1.0)

        tested = len(scores)
        avg_sc = sum(scores) / tested if tested else 0
        avg_lat = sum(latencies) / tested if tested else 0

        print(f"\n  ── {display_name} summary: {tested}/21 ok | {rate_limited} rate-limited | {errors} errors")
        print(f"     Avg score: {avg_sc:.2f}/4 | Avg latency: {avg_lat:.0f}ms")
        if tested:
            print(f"     JSON:{json_ok_count/tested*100:.0f}%  Lang:{lang_ok_count/tested*100:.0f}%  Prod:{prod_ok_count/tested*100:.0f}%")

        all_results[display_name] = {
            "model_id": model_id, "tested": tested, "rate_limited": rate_limited,
            "errors": errors, "avg_score": avg_sc, "avg_latency": avg_lat,
            "json_pct": json_ok_count/tested*100 if tested else 0,
            "lang_pct": lang_ok_count/tested*100 if tested else 0,
            "prod_pct": prod_ok_count/tested*100 if tested else 0,
            "scores": scores,
        }

    return all_results

async def run_call2_models(client: httpx.AsyncClient):
    print("\n" + "=" * 76)
    print("  CALL 2 — RESPONSE GENERATION  (OpenRouter Gemini models, 21 queries each)")
    print("=" * 76)

    all_results = {}

    for display_name, model_id in CALL2_MODELS:
        print(f"\n▶ Testing {display_name}  [{model_id}]")
        scores, latencies = [], []
        rate_limited = errors = 0
        key_iter = cycle(OR_KEYS)  # fresh rotation per model

        per_query_scores = []

        for i, q in enumerate(TEST_QUERIES):
            key = next(key_iter)
            msg = build_call2_prompt(q["query"], q["bot"], q["expected_lang"])
            text, latency, status = await call_llm(client, model_id, msg, key)

            if status == "ok":
                sc, details = evaluate_call2(text, q)
                scores.append(sc)
                latencies.append(latency)
                per_query_scores.append({"query": q, "score": sc, "details": details, "latency": latency, "response": text[:300]})
                marks = (f"Lang:{'✓' if details.get('lang_ok') else '✗'} "
                         f"Irrel:{'✓' if details.get('irrel_ok') else '✗'} "
                         f"Sugg:{'✓' if details.get('sugg_ok') else '✗'} "
                         f"NoLeak:{'✓' if details.get('no_leak') else '✗'}")
                print(f"  Q{i+1:02}/{len(TEST_QUERIES)} [{q['type']:13}][{q['lang']:6}] {latency:5}ms | {marks} | {sc}/5")
            elif status == "rate_limited":
                rate_limited += 1
                per_query_scores.append({"query": q, "score": None, "status": "rate_limited"})
                print(f"  Q{i+1:02}/{len(TEST_QUERIES)} [{q['type']:13}][{q['lang']:6}] ⏳ RATE LIMITED")
            else:
                errors += 1
                per_query_scores.append({"query": q, "score": None, "status": status})
                print(f"  Q{i+1:02}/{len(TEST_QUERIES)} [{q['type']:13}][{q['lang']:6}] ❌ {status[6:60]}")

            await asyncio.sleep(1.0)

        tested = len(scores)
        avg_sc = sum(scores) / tested if tested else 0
        avg_lat = sum(latencies) / tested if tested else 0

        lang_ok   = sum(1 for pq in per_query_scores if pq.get("details", {}).get("lang_ok", False))
        irrel_ok  = sum(1 for pq in per_query_scores if pq.get("details", {}).get("irrel_ok", False))
        sugg_ok   = sum(1 for pq in per_query_scores if pq.get("details", {}).get("sugg_ok", False))
        no_leak   = sum(1 for pq in per_query_scores if pq.get("details", {}).get("no_leak", False))

        print(f"\n  ── {display_name} summary: {tested}/21 ok | {rate_limited} rate-limited | {errors} errors")
        print(f"     Avg score: {avg_sc:.2f}/5 | Avg latency: {avg_lat:.0f}ms")
        if tested:
            print(f"     Lang:{lang_ok/tested*100:.0f}%  Irrel:{irrel_ok/tested*100:.0f}%  Sugg:{sugg_ok/tested*100:.0f}%  NoLeak:{no_leak/tested*100:.0f}%")

        all_results[display_name] = {
            "model_id": model_id, "tested": tested, "rate_limited": rate_limited,
            "errors": errors, "avg_score": avg_sc, "avg_latency": avg_lat,
            "lang_pct": lang_ok/tested*100 if tested else 0,
            "irrel_pct": irrel_ok/tested*100 if tested else 0,
            "sugg_pct": sugg_ok/tested*100 if tested else 0,
            "no_leak_pct": no_leak/tested*100 if tested else 0,
            "per_query": per_query_scores,
        }

    return all_results

# ── Final comparison (merging with known prior results) ───────────────────────
def print_final_comparison(call1_new, call2_new):
    print("\n" + "=" * 76)
    print("  ══ FINAL COMPARISON (ALL DATA COMBINED) ══")
    print("=" * 76)

    # Prior data (from test_model_comparison.py run)
    prior_call1 = {
        "OR-gemini-2.0-flash":  {"tested": 21, "avg_score": 3.62, "avg_latency": 1820, "json_pct": 100, "lang_pct": 71,  "prod_pct": 95,  "source": "prev run"},
        "llama-3.1-8b (Groq)":  {"tested": 21, "avg_score": 3.33, "avg_latency": 699,  "json_pct": 100, "lang_pct": 43,  "prod_pct": 90,  "source": "prev run"},
        "gemini-2.5-flash-lite": {"tested": 19, "avg_score": 3.84, "avg_latency": 1604, "json_pct": 100, "lang_pct": 84,  "prod_pct": 100, "source": "prev run (direct API)"},
    }
    prior_call2 = {
        "llama-3.3-70b (Groq)": {"tested": 21, "avg_score": 4.76, "avg_latency": 1578, "lang_pct": 100, "irrel_pct": 100, "sugg_pct": 76,  "no_leak_pct": 100, "source": "prev run"},
    }

    print("\n  ── CALL 1: Query Analysis ──────────────────────────────────────────")
    print(f"  {'Model':<30} {'Tested':>6} {'Score':>7} {'Latency':>9} {'Lang%':>7} {'Source'}")
    print(f"  {'-'*30} {'-'*6} {'-'*7} {'-'*9} {'-'*7} {'-'*20}")
    all_c1 = {**prior_call1}
    for name, r in call1_new.items():
        if r["tested"] > 0:
            all_c1[name] = r
    for name, r in sorted(all_c1.items(), key=lambda x: -x[1].get("avg_score", 0)):
        src = r.get("source", "this run")
        lang_p = r.get("lang_pct", "?")
        print(f"  {name:<30} {r['tested']:>6} {r['avg_score']:>6.2f}/4 {r['avg_latency']:>7.0f}ms {str(lang_p)+('%' if lang_p!='?' else ''):>7} [{src}]")

    print("\n  ── CALL 2: Response Generation ─────────────────────────────────────")
    print(f"  {'Model':<30} {'Tested':>6} {'Score':>7} {'Latency':>9} {'Sugg%':>7} {'Source'}")
    print(f"  {'-'*30} {'-'*6} {'-'*7} {'-'*9} {'-'*7} {'-'*20}")
    all_c2 = {**prior_call2}
    for name, r in call2_new.items():
        if r["tested"] > 0:
            all_c2[name] = r
    for name, r in sorted(all_c2.items(), key=lambda x: (-x[1].get("avg_score", 0), x[1].get("avg_latency", 9999))):
        src = r.get("source", "this run")
        sugg_p = r.get("sugg_pct", "?")
        print(f"  {name:<30} {r['tested']:>6} {r['avg_score']:>6.2f}/5 {r['avg_latency']:>7.0f}ms {str(round(sugg_p) if sugg_p!='?' else '?')+('%' if sugg_p!='?' else ''):>7} [{src}]")

    print("\n  ── RECOMMENDATION ──────────────────────────────────────────────────")
    # Pick best by avg_score
    best_c1 = max(all_c1.items(), key=lambda x: x[1].get("avg_score", 0))
    best_c2 = max(all_c2.items(), key=lambda x: (x[1].get("avg_score", 0), -x[1].get("avg_latency", 9999)))
    print(f"  Best Call 1: {best_c1[0]} (score={best_c1[1]['avg_score']:.2f}/4, latency={best_c1[1]['avg_latency']:.0f}ms)")
    print(f"  Best Call 2: {best_c2[0]} (score={best_c2[1]['avg_score']:.2f}/5, latency={best_c2[1]['avg_latency']:.0f}ms)")

async def main():
    print("=" * 76)
    print("  OPENROUTER MULTI-KEY RETEST")
    print("  4 OR keys in round-robin rotation | ~1s delay between queries")
    print(f"  Keys (last 8 chars): {' | '.join(k[-8:] for k in OR_KEYS)}")
    print("=" * 76)

    async with httpx.AsyncClient() as client:
        call1_results = await run_call1_models(client)
        print("\n\n⏳ 5s pause before Call 2...")
        await asyncio.sleep(5)
        call2_results = await run_call2_models(client)

    print_final_comparison(call1_results, call2_results)

    # Save new results
    out = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "call1_new": {k: {mk: mv for mk, mv in v.items() if mk != "scores"} for k, v in call1_results.items()},
        "call2_new": {k: {mk: mv for mk, mv in v.items() if mk != "per_query"} for k, v in call2_results.items()},
        "call2_per_query": {k: v.get("per_query", []) for k, v in call2_results.items()},
    }
    with open("openrouter_retest_results.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False, default=str)
    print("\n  Results saved to openrouter_retest_results.json")
    print("  Done!")

if __name__ == "__main__":
    asyncio.run(main())
