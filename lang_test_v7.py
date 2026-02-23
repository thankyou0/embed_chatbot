"""
Language Test V7 — Non-Product + Product queries across 6 bots with varied language configs.
Pure native Hindi (Devanagari) and Gujarati scripts used.
"""
import httpx, json, time, uuid, asyncio, sys
from typing import Optional

# Force UTF-8 stdout/stderr so Gujarati / Hindi / ✓ symbols don't crash on Windows cp1252
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE = "http://localhost:8000/api/v1"

# ─── Auth ─────────────────────────────────────────────────────────────────────
def login():
    r = httpx.post(f"{BASE}/auth/login",
                   json={"email": "max@gmail.com", "password": "12345678"},
                   timeout=10)
    r.raise_for_status()
    return r.json()["access_token"]

TOKEN = login()
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# ─── Bot definitions ──────────────────────────────────────────────────────────
BOTS = [
    {
        "id": "799637f9-391b-4b9d-84cb-5fdd17cdf109",
        "name": "Crawl-Tentree",
        "domain": "sustainable outdoor/eco clothing (tentree.com)",
        "lang_config": ["en", "hi", "gu"],
    },
    {
        "id": "99fc3604-99e7-4cd0-a2a6-509ac08d9fd0",
        "name": "Crawl-Death Wish Coffee",
        "domain": "strong/specialty coffee brand (deathwishcoffee.com)",
        "lang_config": ["en", "hi"],
    },
    {
        "id": "e23fcc6f-7a02-4b09-8d49-95c00a57d852",
        "name": "Crawl-Beardbrand",
        "domain": "beard grooming & men's care (beardbrand.com)",
        "lang_config": ["en", "gu"],
    },
    {
        "id": "182f88cd-02d8-4c94-824d-b41432847400",
        "name": "ramraj",
        "domain": "Indian cotton traditional wear (ramraj.in)",
        "lang_config": ["hi", "gu"],
    },
    {
        "id": "1cb18dc0-4909-409d-ab03-0436524fcec4",
        "name": "kriyanta",
        "domain": "handmade home décor & gifting (kriyanta.com)",
        "lang_config": ["hi"],
    },
    {
        "id": "e79b3754-006d-45d5-b21d-2391710e08ca",
        "name": "zevaramaze",
        "domain": "handmade silver jewellery (zevaramaze.com)",
        "lang_config": ["gu"],
    },
]

# ─── Queries per bot: (lang_code, query_type, text) ──────────────────────────
# query_type: "non_product" | "product"
# Languages used are within each bot's allowed langs only.

BOT_QUERIES = {
    "799637f9-391b-4b9d-84cb-5fdd17cdf109": [
        # English
        ("en", "non_product", "What is Tentree's environmental mission?"),
        ("en", "product",     "What hoodies or sweatshirts do you sell?"),
        # Pure Devanagari Hindi
        ("hi", "non_product", "टेंट्री का पर्यावरण से क्या संबंध है?"),
        ("hi", "product",     "आपके पास कौन सी जैकेट उपलब्ध हैं?"),
        # Pure Gujarati script
        ("gu", "non_product", "ટેન્ટ્રી પર્યાવરણ માટે શું કરે છે?"),
        ("gu", "product",     "તમારી પાસે ક્યા ટી-શર્ટ ઉપલબ્ધ છે?"),
    ],
    "99fc3604-99e7-4cd0-a2a6-509ac08d9fd0": [
        # English
        ("en", "non_product", "What makes Death Wish Coffee unique compared to other brands?"),
        ("en", "product",     "Show me your ground coffee products and their prices."),
        # Pure Hindi
        ("hi", "non_product", "डेथ विश कॉफी की खासियत क्या है?"),
        ("hi", "product",     "आपके पास कौन सी कॉफी उत्पाद हैं और उनके दाम क्या हैं?"),
    ],
    "e23fcc6f-7a02-4b09-8d49-95c00a57d852": [
        # English
        ("en", "non_product", "How do I grow and maintain a healthy beard?"),
        ("en", "product",     "What beard oils or balms do you carry?"),
        # Pure Gujarati
        ("gu", "non_product", "સ્વસ્થ દાઢી કેવી રીતે ઉગાડવી?"),
        ("gu", "product",     "તમારી પાસે ક્યા દાઢી ઓઈલ ઉપલબ્ધ છે અને ભાવ શું છે?"),
    ],
    "182f88cd-02d8-4c94-824d-b41432847400": [
        # Pure Hindi (no English)
        ("hi", "non_product", "रामराज कॉटन का इतिहास क्या है?"),
        ("hi", "product",     "मुझे पुरुषों के लिए सूती धोती चाहिए, क्या है आपके पास?"),
        # Pure Gujarati
        ("gu", "non_product", "રામરાજ કૉટન વિશે જણાવો."),
        ("gu", "product",     "મહિલaઓ માટe સlvar suit ઉpalbdh che?"),
    ],
    "1cb18dc0-4909-409d-ab03-0436524fcec4": [
        # Pure Hindi only
        ("hi", "non_product", "क्रियान्त ब्रांड के बारे में बताएं।"),
        ("hi", "product",     "मुझे घर की सजावट के लिए कुछ हस्तनिर्मित चीजें चाहिए।"),
    ],
    "e79b3754-006d-45d5-b21d-2391710e08ca": [
        # Pure Gujarati only
        ("gu", "non_product", "ઝેવારામઝ વિશે જણાઓ."),
        ("gu", "product",     "chandIni VINti na bhav shu che?"),
    ],
}

# Fix typos in ramraj and zevaramaze queries (these should remain pure script but I inadvertently mixed)
BOT_QUERIES["182f88cd-02d8-4c94-824d-b41432847400"] = [
    ("hi", "non_product", "रामराज कॉटन का इतिहास क्या है?"),
    ("hi", "product",     "मुझे पुरुषों के लिए सूती धोती चाहिए, क्या है आपके पास?"),
    ("gu", "non_product", "રામરાજ કૉટન વિશે જણાવો."),
    ("gu", "product",     "સ્ત્રીઓ માટે સલ્વાર સૂટ ઉપલ્બ્ધ છે?"),
]
BOT_QUERIES["e79b3754-006d-45d5-b21d-2391710e08ca"] = [
    ("gu", "non_product", "ઝેવારામઝ ઘરેણા વિશે જણાઓ."),
    ("gu", "product",     "ચાંદીની વીંટી ઉpalbdh che ane bhav su che?"),
]
# Final correction of zevaramaze query to pure Gujarati
BOT_QUERIES["e79b3754-006d-45d5-b21d-2391710e08ca"] = [
    ("gu", "non_product", "ઝેવારામઝ ઘરેણા વિશે જણાઓ."),
    ("gu", "product",     "ચાંદીની વીંટી ઉપલ્બ્ધ છે? ભાવ શું છે?"),
]

# ─── Step 1: Update language configs ─────────────────────────────────────────
print("=" * 70)
print("STEP 1: Setting language configurations")
print("=" * 70)

for bot in BOTS:
    r = httpx.patch(
        f"{BASE}/chatbots/{bot['id']}/appearance",
        headers=HEADERS,
        json={"languages": bot["lang_config"]},
        timeout=10,
    )
    status = "OK" if r.status_code in (200, 204) else f"FAIL {r.status_code} {r.text[:80]}"
    print(f"  {bot['name']}: langs={bot['lang_config']} -> {status}")

print()

# ─── Step 2: Run queries via streaming endpoint ───────────────────────────────
def collect_stream(bot_id: str, message: str) -> dict:
    """Send a streaming chat message and collect the full assembled response."""
    session_id = str(uuid.uuid4())
    full_text = ""
    products = []
    suggestions = []
    flags = {}
    error = None

    try:
        with httpx.Client(timeout=60.0) as client:
            with client.stream(
                "POST",
                f"{BASE}/chat/{bot_id}/message/stream",
                data={"message": message, "session_id": session_id, "is_preview": "true"},
            ) as resp:
                if resp.status_code != 200:
                    return {"error": f"HTTP {resp.status_code}: {resp.read()[:200].decode()}"}
                try:
                    for line in resp.iter_lines():
                        line = line.strip()
                        if not line or not line.startswith("data: "):
                            continue
                        raw = line[6:]
                        if raw == "[DONE]":
                            break
                        try:
                            chunk = json.loads(raw)
                            t = chunk.get("type", "")
                            if t == "content":
                                full_text += chunk.get("content", "")
                            elif t == "products":
                                products = chunk.get("products", [])
                            elif t == "suggestions":
                                suggestions = chunk.get("suggestions", [])
                            elif t == "done":
                                # products & suggestions only arrive in the done event
                                products = chunk.get("products", products)
                                suggestions = chunk.get("suggestions", suggestions)
                            elif t == "flags":
                                flags = chunk
                            elif t == "error":
                                error = chunk.get("error", "unknown error")
                        except json.JSONDecodeError:
                            pass
                except Exception as stream_err:
                    # Partial content is OK — still return what we got
                    if not full_text:
                        error = f"Stream error: {stream_err}"
    except KeyboardInterrupt:
        raise
    except Exception as e:
        error = str(e)

    return {
        "text": full_text.strip(),
        "products": products,
        "suggestions": suggestions,
        "flags": flags,
        "error": error,
    }


print("=" * 70)
print("STEP 2: Running queries")
print("=" * 70)

RESULTS = []

for bot in BOTS:
    bot_id = bot["id"]
    queries = BOT_QUERIES[bot_id]
    print(f"\n--- {bot['name']} (langs: {bot['lang_config']}) ---")
    for lang, qtype, query in queries:
        print(f"  [{lang}][{qtype}] {query[:60]}", end="  ", flush=True)
        t0 = time.time()
        result = collect_stream(bot_id, query)
        elapsed = time.time() - t0
        
        text = result.get("text", "")
        products = result.get("products", [])
        error = result.get("error")
        
        flag = "⚠ ERROR" if error else ("✓" if text else "⚠ EMPTY")
        print(f"{flag} ({elapsed:.1f}s) | {len(products)} products | {len(text)} chars")

        RESULTS.append({
            "bot_id": bot_id,
            "bot_name": bot["name"],
            "allowed_langs": bot["lang_config"],
            "domain": bot["domain"],
            "query_lang": lang,
            "query_type": qtype,
            "query": query,
            "response_text": text,
            "products": products,
            "suggestions": result.get("suggestions", []),
            "error": error,
            "elapsed_s": round(elapsed, 2),
        })
        time.sleep(1)  # be polite

print()

# ─── Step 3: Analyse and score ────────────────────────────────────────────────
def detect_response_language(text: str) -> str:
    """Rough heuristic: determine if response is in EN / HI / GU / other."""
    if not text:
        return "empty"
    # Check for Devanagari chars (Hindi)
    deva = sum(1 for c in text if '\u0900' <= c <= '\u097F')
    # Check for Gujarati chars
    guja = sum(1 for c in text if '\u0A80' <= c <= '\u0AFF')
    # Check for English alpha
    eng = sum(1 for c in text if c.isalpha() and ord(c) < 128)

    total = max(deva + guja + eng, 1)
    if deva / total > 0.3:
        return "hi"
    if guja / total > 0.3:
        return "gu"
    return "en"

def has_context_mention(text: str) -> bool:
    return "context" in text.lower() or "the provided context" in text.lower()

ISSUES = []
STRENGTHS = []

for r in RESULTS:
    name = r["bot_name"]
    ql = r["query_lang"]
    qt = r["query_type"]
    text = r["response_text"]
    products = r["products"]
    allowed = r["allowed_langs"]

    # Error check
    if r["error"]:
        ISSUES.append((name, ql, qt, r["query"], f"API ERROR: {r['error']}"))
        continue

    # Empty response
    if not text:
        ISSUES.append((name, ql, qt, r["query"], "Empty response (no text returned)"))
        continue

    # "context" mention check
    if has_context_mention(text):
        ISSUES.append((name, ql, qt, r["query"],
                       "Mentions 'context' — should rephrase to avoid exposing internal retrieval language"))

    # Response language check (should roughly match query lang OR be English for EN queries)
    resp_lang = detect_response_language(text)
    if ql == "hi" and resp_lang not in ("hi", "en"):
        ISSUES.append((name, ql, qt, r["query"],
                       f"Query in Hindi but response detected as: {resp_lang}"))
    elif ql == "gu" and resp_lang not in ("gu", "en"):
        ISSUES.append((name, ql, qt, r["query"],
                       f"Query in Gujarati but response detected as: {resp_lang}"))

    # For Hindi/Gujarati queries, response should be in that language (not pure English)
    if ql in ("hi", "gu") and resp_lang == "en":
        ISSUES.append((name, ql, qt, r["query"],
                       f"Query in {ql} but bot responded in English instead"))

    # Product query but no products returned
    if qt == "product" and len(products) == 0:
        # Not necessarily wrong if bot says no products available; but note it
        ISSUES.append((name, ql, qt, r["query"],
                       "Product query returned 0 product cards — check if products exist in knowledge base"))

    # Suggestions quality
    if not r["suggestions"] or len(r["suggestions"]) < 2:
        ISSUES.append((name, ql, qt, r["query"], "Fewer than 2 follow-up suggestions returned"))

    # Strength: good product listings
    if qt == "product" and len(products) > 0:
        STRENGTHS.append((name, ql, qt, r["query"], f"Returned {len(products)} product card(s) ✓"))

    # Strength: correct language reply
    if (ql == "hi" and resp_lang == "hi") or (ql == "gu" and resp_lang == "gu"):
        STRENGTHS.append((name, ql, qt, r["query"], f"Replied in correct language ({ql}) ✓"))

# ─── Step 4: Write report ─────────────────────────────────────────────────────
REPORT_PATH = "LANG_TEST_V7_REPORT.md"

with open(REPORT_PATH, "w", encoding="utf-8") as f:
    f.write("# Language Test V7 — Non-Product & Product Query Report\n\n")
    f.write(f"**Date:** {time.strftime('%Y-%m-%d %H:%M')}\n\n")
    f.write("## Language Configuration\n\n")
    f.write("| Bot | Domain | Languages Set |\n")
    f.write("|-----|--------|---------------|\n")
    for bot in BOTS:
        f.write(f"| {bot['name']} | {bot['domain']} | {', '.join(bot['lang_config'])} |\n")
    f.write("\n")

    f.write("## Detailed Results\n\n")
    for bot in BOTS:
        bot_results = [r for r in RESULTS if r["bot_id"] == bot["id"]]
        f.write(f"### {bot['name']}\n")
        f.write(f"**Domain:** {bot['domain']}  \n")
        f.write(f"**Allowed Languages:** {', '.join(bot['lang_config'])}\n\n")
        f.write("| Lang | Type | Query | Response (first 200 chars) | Products | Resp Lang | Time |\n")
        f.write("|------|------|-------|----------------------------|----------|-----------|------|\n")
        for r in bot_results:
            resp_lang = detect_response_language(r["response_text"])
            snippet = (r["response_text"][:200].replace("\n", " ").replace("|", "\\|")
                       if r["response_text"] else f"ERROR: {r['error']}")
            f.write(f"| {r['query_lang']} | {r['query_type']} | {r['query'][:50]} | {snippet} | {len(r['products'])} | {resp_lang} | {r['elapsed_s']}s |\n")
        f.write("\n")
        
        # Suggestions per query
        f.write("**Follow-up Suggestions:**\n\n")
        for r in bot_results:
            if r.get("suggestions"):
                f.write(f"- [{r['query_lang']}] *{r['query'][:50]}* → {r['suggestions']}\n")
        f.write("\n")

    f.write("## Issues Found\n\n")
    if ISSUES:
        f.write("| Bot | Lang | Type | Query | Issue |\n")
        f.write("|-----|------|------|-------|-------|\n")
        for (name, ql, qt, q, issue) in ISSUES:
            q_safe = q[:50].replace("|", "\\|")
            issue_safe = issue.replace("|", "\\|")
            f.write(f"| {name} | {ql} | {qt} | {q_safe} | {issue_safe} |\n")
    else:
        f.write("No issues found.\n")
    f.write("\n")

    f.write("## Strengths\n\n")
    if STRENGTHS:
        f.write("| Bot | Lang | Type | Query | Strength |\n")
        f.write("|-----|------|------|-------|----------|\n")
        for (name, ql, qt, q, s) in STRENGTHS:
            q_safe = q[:50].replace("|", "\\|")
            f.write(f"| {name} | {ql} | {qt} | {q_safe} | {s} |\n")
    else:
        f.write("No notable strengths recorded.\n")
    f.write("\n")

    f.write("## Improvement Suggestions\n\n")
    
    # Analyse common patterns and write targeted suggestions
    lang_mismatch_bots = set(name for (name, ql, qt, q, issue) in ISSUES
                             if "responded in English" in issue or "response detected as" in issue)
    no_product_bots = set(name for (name, ql, qt, q, issue) in ISSUES
                          if "0 product cards" in issue)
    context_bots = set(name for (name, ql, qt, q, issue) in ISSUES
                       if "'context'" in issue or "context" in issue.lower())
    no_suggestion_bots = set(name for (name, ql, qt, q, issue) in ISSUES
                              if "suggestion" in issue)
    
    if lang_mismatch_bots:
        f.write(f"### 1. Language Mismatch (affects: {', '.join(sorted(lang_mismatch_bots))})\n")
        f.write("- **Root cause:** The bot responds in English even when the query is in Hindi/Gujarati.\n")
        f.write("- **Fix:** Ensure Call2 system prompt explicitly instructs the model to respond in the detected query language (`effective_language`). Verify `_translate_response` is being triggered correctly.\n\n")
    
    if context_bots:
        f.write(f"### 2. 'Context' Exposed in Response (affects: {', '.join(sorted(context_bots))})\n")
        f.write("- **Root cause:** The LLM leaks retrieval/system language like 'not mentioned in the provided context'.\n")
        f.write("- **Fix:** Add an explicit instruction in the system prompt: `Never say 'context', 'provided context', 'my knowledge base', or similar phrases. Instead say 'I don't have information about that' or similar.`\n\n")
    
    if no_product_bots:
        f.write(f"### 3. Product Cards Not Returned (affects: {', '.join(sorted(no_product_bots))})\n")
        f.write("- **Root cause:** Product embeddings may not have been indexed, OR the translated Hindi/Gujarati query is not matching product embeddings (which are in English).\n")
        f.write("- **Fix:** \n")
        f.write("  - Verify crawled product data has price+name in embedding.\n")
        f.write("  - Improve Call1 english_query translation quality so the embedding search finds products.\n")
        f.write("  - Consider adding a fallback: if 0 products returned but `is_product_query=True`, re-run with a broader query.\n\n")
    
    if no_suggestion_bots:
        f.write(f"### 4. Insufficient Follow-up Suggestions (affects: {', '.join(sorted(no_suggestion_bots))})\n")
        f.write("- **Fix:** Ensure the suggestions generator in the system prompt always produces at least 2-3 contextually relevant suggestions in the user's language.\n\n")
    
    f.write("### 5. General Recommendations\n")
    f.write("- For product query responses in non-English languages, ensure product card image/price/name rendering is tested in the widget UI — the data may be correct but UI may not render non-ASCII names.\n")
    f.write("- Add a post-response language validator: if detected(response_lang) != effective_language, trigger automatic re-translation of the bot's reply.\n")
    f.write("- Consider pre-indexing transliterated product names to improve Hindi/Gujarati-typed search matches.\n\n")

    # Save raw results JSON
    with open("lang_test_v7_raw.json", "w", encoding="utf-8") as jf:
        json.dump(RESULTS, jf, ensure_ascii=False, indent=2)

    f.write("## Raw Results\nSee `lang_test_v7_raw.json` for complete response data.\n")

print(f"Report written to {REPORT_PATH}")
print(f"Issues found: {len(ISSUES)}")
print(f"Strengths found: {len(STRENGTHS)}")
