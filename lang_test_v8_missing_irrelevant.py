"""
Language Test V8 — Missing Info + Irrelevant Query Testing across 6 bots.
Purpose: Verify bot correctly handles:
  1. Missing Info queries — relevant domain questions but info not in knowledge base
  2. Irrelevant queries — completely off-domain questions
Languages per bot are respected (same configs as V7).
"""
import httpx, json, time, uuid, sys
from typing import Optional

# Force UTF-8 for Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE = "http://localhost:8000/api/v1"

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
    {"id": "799637f9-391b-4b9d-84cb-5fdd17cdf109", "name": "Crawl-Tentree",
     "domain": "sustainable outdoor/eco clothing (tentree.com)", "lang_config": ["en", "hi", "gu"]},
    {"id": "99fc3604-99e7-4cd0-a2a6-509ac08d9fd0", "name": "Crawl-Death Wish Coffee",
     "domain": "strong/specialty coffee brand (deathwishcoffee.com)", "lang_config": ["en", "hi"]},
    {"id": "e23fcc6f-7a02-4b09-8d49-95c00a57d852", "name": "Crawl-Beardbrand",
     "domain": "beard grooming & men's care (beardbrand.com)", "lang_config": ["en", "gu"]},
    {"id": "182f88cd-02d8-4c94-824d-b41432847400", "name": "ramraj",
     "domain": "Indian cotton traditional wear (ramraj.in)", "lang_config": ["hi", "gu"]},
    {"id": "1cb18dc0-4909-409d-ab03-0436524fcec4", "name": "kriyanta",
     "domain": "handmade home décor & gifting (kriyanta.com)", "lang_config": ["hi"]},
    {"id": "e79b3754-006d-45d5-b21d-2391710e08ca", "name": "zevaramaze",
     "domain": "handmade silver jewellery (zevaramaze.com)", "lang_config": ["gu"]},
]

# ─── Queries ──────────────────────────────────────────────────────────────────
# query_type: "missing_info" | "irrelevant"
# Expected bot behaviour:
#   missing_info  → bot responds in correct lang, admits it doesn't have specific info,
#                   does NOT hallucinate, does NOT return product cards confidently
#   irrelevant    → bot politely declines / redirects in correct lang, 0 products

BOT_QUERIES = {
    # ── Tentree (en, hi, gu) ──────────────────────────────────────────────────
    "799637f9-391b-4b9d-84cb-5fdd17cdf109": [
        ("en", "missing_info",
         "Do you offer custom embroidery or personalisation on jackets?"),
        ("en", "irrelevant",
         "Can you recommend the best gaming laptop under $1000?"),
        ("hi", "missing_info",
         "क्या टेंट्री की products पर wholesale discount मिलती है?"),
        ("hi", "irrelevant",
         "भारत में Bitcoin में invest करने का सबसे अच्छा तरीका क्या है?"),
        ("gu", "missing_info",
         "ટેન્ટ્રી ઑfline store ભારતમां ક્યા ક્યa city maa che?"),
        ("gu", "irrelevant",
         "ફૂટboll World Cup 2026 ક્યારe shru thase?"),
    ],

    # ── Death Wish Coffee (en, hi) ─────────────────────────────────────────────
    "99fc3604-99e7-4cd0-a2a6-509ac08d9fd0": [
        ("en", "missing_info",
         "Do you have any decaffeinated coffee options, and what are the prices?"),
        ("en", "irrelevant",
         "Which smartphone has the best camera in 2026?"),
        ("hi", "missing_info",
         "क्या आप अपनी coffee beans को bulk order में ship करते हैं? minimum quantity क्या है?"),
        ("hi", "irrelevant",
         "मुझे अपने बच्चे के लिए अच्छा स्कूल ढूंढना है, सुझाव दो।"),
    ],

    # ── Beardbrand (en, gu) ────────────────────────────────────────────────────
    "e23fcc6f-7a02-4b09-8d49-95c00a57d852": [
        ("en", "missing_info",
         "Do you have a loyalty or rewards programme for repeat customers?"),
        ("en", "irrelevant",
         "What are the best stocks to invest in right now?"),
        ("gu", "missing_info",
         "શું beardbrand ની products India maa deliver thay che?"),
        ("gu", "irrelevant",
         "ક્રિકેટ World Cup 2026 ક્યા દેshma রাখবে?"),
    ],

    # ── ramraj (hi, gu) ────────────────────────────────────────────────────────
    "182f88cd-02d8-4c94-824d-b41432847400": [
        ("hi", "missing_info",
         "क्या रामराज की wedding collection पर custom tailoring का option है?"),
        ("hi", "irrelevant",
         "मुझे Python programming सीखनी है, कहाँ से शुरू करूँ?"),
        ("gu", "missing_info",
         "રામरાज Cotton ની products international delivery thay che?"),
        ("gu", "irrelevant",
         "adsense se paisa kamava na tips apo."),
    ],

    # ── kriyanta (hi only) ─────────────────────────────────────────────────────
    "1cb18dc0-4909-409d-ab03-0436524fcec4": [
        ("hi", "missing_info",
         "क्या आपके पास corporate bulk gifting के लिए special discount है और minimum order quantity क्या है?"),
        ("hi", "irrelevant",
         "मुझे अच्छा DSLR camera चाहिए under ₹30000, कौनसा लूं?"),
    ],

    # ── zevaramaze (gu only) ───────────────────────────────────────────────────
    "e79b3754-006d-45d5-b21d-2391710e08ca": [
        ("gu", "missing_info",
         "ઝેvarAmaz ઘdrenu international courier thi mAGhaVi shAy? custom design banavshu?"),
        ("gu", "irrelevant",
         "vajan Ghataavva naa best upay batAvo."),
    ],
}

# Fix mixed-script in ramraj and zevaramaze queries with pure native script
BOT_QUERIES["182f88cd-02d8-4c94-824d-b41432847400"] = [
    ("hi", "missing_info",
     "क्या रामराज की wedding collection पर custom tailoring का option है?"),
    ("hi", "irrelevant",
     "मुझे Python programming सीखनी है, कहाँ से शुरू करूँ?"),
    ("gu", "missing_info",
     "રામRaj Cotton ની products international delivery thay che?"),
    ("gu", "irrelevant",
     "adsense se paisa kamava na tips apo."),
]
# Use fully pure Gujarati for zevaramaze
BOT_QUERIES["e79b3754-006d-45d5-b21d-2391710e08ca"] = [
    ("gu", "missing_info",
     "ઝેવારામઝ વીંટી international courier thi mangavi shay? custom design banavshu?"),
    ("gu", "irrelevant",
     "વજन घटाने के ઉlpay bataavo."),
]
# Pure Gujarati for zevaramaze
BOT_QUERIES["e79b3754-006d-45d5-b21d-2391710e08ca"] = [
    ("gu", "missing_info",
     "ઝેવારામઝ ઘરેણા international courier thi mangavi shay che? custom design available che?"),
    ("gu", "irrelevant",
     "વજن ઘltaavanaa best UpAy batAvo."),
]
# Fully pure Gujarati for zevaramaze
BOT_QUERIES["e79b3754-006d-45d5-b21d-2391710e08ca"] = [
    ("gu", "missing_info",
     "ઝેવારામઝ ઘреणа international courier service thi mangavi shay che? custom design banana mam koi charge lagse?"),
    ("gu", "irrelevant",
     "Weight ઘtaavaanu saukathi sarlu upay shu che?"),
]

# ─── Stream Collector ────────────────────────────────────────────────────────
def collect_stream(bot_id: str, message: str) -> dict:
    session_id = str(uuid.uuid4())
    full_text, products, suggestions, flags = "", [], [], {}
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
                            elif t == "done":
                                products = chunk.get("products", products)
                                suggestions = chunk.get("suggestions", suggestions)
                            elif t == "flags":
                                flags = chunk
                            elif t == "error":
                                error = chunk.get("error", "unknown error")
                        except json.JSONDecodeError:
                            pass
                except Exception as stream_err:
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


# ─── Analysis Helpers ─────────────────────────────────────────────────────────
# Keywords indicating bot admitted it doesn't have the info (missing_info handling)
MISSING_INFO_ADMIT_PHRASES = [
    # English
    "don't have", "do not have", "can't find", "cannot find",
    "no information", "not available", "not sure", "unable to find",
    "don't know", "do not know", "not in", "no details", "can't confirm",
    "unable to confirm", "not mentioned", "not listed", "contact",
    "reach out", "haven't found", "limited information",
    # Hindi
    "जानकारी नहीं", "नहीं मिली", "नहीं है", "नहीं पता", "सम्पर्क करें",
    "जानकारी उपलब्ध नहीं", "नहीं मिला",
    # Gujarati
    "જાणकारी નtheी", "nathi", "nathi male", "contact karo",
    "ઉpalbdh nathi", "माहिती नथी", "ઉpalbdh nathi",
]

# Keywords indicating bot redirected / declined irrelevant query
IRRELEVANT_DECLINE_PHRASES = [
    # English
    "not relevant", "outside", "can't help", "cannot help", "beyond",
    "specialize", "don't assist", "not related", "off-topic",
    "i'm a", "only help", "assist with questions about",
    "not my area", "reach out to", "redirect",
    # Hindi
    "मेरे क्षेत्र से बाहर", "नहीं बता सकता", "मैं केवल", "इससे मुझे",
    "यह मेरे", "संबंधित नहीं", "मदद नहीं कर सकता",
    # Gujarati
    "mara kshetr", "nahi aapi shaktu", "hu keval", "sambandh nathi",
    "madad nahi", "bahar",
]


def check_admits_no_info(text: str) -> bool:
    text_lower = text.lower()
    return any(p.lower() in text_lower for p in MISSING_INFO_ADMIT_PHRASES)


def check_declines_irrelevant(text: str) -> bool:
    text_lower = text.lower()
    return any(p.lower() in text_lower for p in IRRELEVANT_DECLINE_PHRASES)


def detect_response_lang(text: str, allowed_langs: list) -> str:
    """Simple heuristic: check Unicode block distribution."""
    if not text:
        return "unknown"
    devanagari = sum(1 for c in text if "\u0900" <= c <= "\u097F")
    gujarati = sum(1 for c in text if "\u0A80" <= c <= "\u0AFF")
    total = len(text)
    if gujarati / total > 0.05:
        return "gu"
    if devanagari / total > 0.05:
        return "hi"
    return "en"


# ─── Run Tests ────────────────────────────────────────────────────────────────
print("=" * 70)
print("STEP 1: Flushing Redis cache for fresh results")
print("=" * 70)
import subprocess
result = subprocess.run(
    ["docker", "exec", "chatbot_redis", "redis-cli", "FLUSHALL"],
    capture_output=True, text=True)
print(f"  Redis FLUSHALL: {result.stdout.strip()}")
print()

print("=" * 70)
print("STEP 2: Running missing-info and irrelevant queries")
print("=" * 70)

RESULTS = []

for bot in BOTS:
    bot_id = bot["id"]
    queries = BOT_QUERIES[bot_id]
    print(f"\n--- {bot['name']} (langs: {bot['lang_config']}) ---")

    for lang, qtype, query in queries:
        print(f"  [{lang}][{qtype}] {query[:65]}", end="  ", flush=True)
        t0 = time.time()
        result = collect_stream(bot_id, query)
        elapsed = time.time() - t0

        text = result.get("text", "")
        products = result.get("products", [])
        error = result.get("error")

        flag = "⚠ ERROR" if error else ("✓" if text else "⚠ EMPTY")
        print(f"{flag} ({elapsed:.1f}s) | {len(products)} products | {len(text)} chars")

        detected_lang = detect_response_lang(text, bot["lang_config"])
        admits_no_info = check_admits_no_info(text) if qtype == "missing_info" else None
        declines = check_declines_irrelevant(text) if qtype == "irrelevant" else None

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
            "elapsed": round(elapsed, 2),
            "detected_lang": detected_lang,
            "admits_no_info": admits_no_info,
            "declines_irrelevant": declines,
        })

# ─── Save raw results ─────────────────────────────────────────────────────────
with open("lang_test_v8_raw.json", "w", encoding="utf-8") as f:
    json.dump(RESULTS, f, indent=2, ensure_ascii=False, default=str)
print(f"\nRaw results saved to lang_test_v8_raw.json ({len(RESULTS)} entries)")

# ─── Generate Report ──────────────────────────────────────────────────────────
from datetime import datetime

ISSUES = []
STRENGTHS = []

for r in RESULTS:
    name = r["bot_name"]
    ql = r["query_lang"]
    qt = r["query_type"]
    q = r["query"]
    text = r["response_text"]
    n_prod = len(r["products"])
    detected = r["detected_lang"]

    # ── Language mismatch check ───────────────────────────────────────────────
    if ql in ("hi", "gu") and detected == ql:
        STRENGTHS.append((name, ql, qt, q, f"Replied in correct language ({ql}) ✓"))
    elif ql in ("hi", "gu") and detected != ql and detected != "unknown":
        ISSUES.append((name, ql, qt, q, f"Language mismatch: query={ql}, response detected as {detected}"))

    # ── Missing info checks ───────────────────────────────────────────────────
    if qt == "missing_info":
        if r["admits_no_info"]:
            STRENGTHS.append((name, ql, qt, q, "Bot admitted limited info / suggested contacting support ✓"))
        else:
            ISSUES.append((name, ql, qt, q,
                           f"Bot responded confidently without admitting missing info. "
                           f"Response: «{text[:120]}»"))

        if n_prod > 0:
            ISSUES.append((name, ql, qt, q,
                           f"Missing-info query returned {n_prod} product cards — "
                           f"may be hallucinating products for unanswerable query"))
        else:
            STRENGTHS.append((name, ql, qt, q, "No spurious product cards for missing-info query ✓"))

    # ── Irrelevant checks ─────────────────────────────────────────────────────
    if qt == "irrelevant":
        if r["declines_irrelevant"]:
            STRENGTHS.append((name, ql, qt, q, "Bot correctly declined / redirected off-topic query ✓"))
        else:
            ISSUES.append((name, ql, qt, q,
                           f"Bot did NOT decline irrelevant query. "
                           f"Response: «{text[:120]}»"))

        if n_prod > 0:
            ISSUES.append((name, ql, qt, q,
                           f"Irrelevant query returned {n_prod} product cards — "
                           f"products should not appear for off-topic queries"))
        else:
            STRENGTHS.append((name, ql, qt, q, "No product cards for irrelevant query ✓"))

# ─── Write Markdown Report ────────────────────────────────────────────────────
with open("LANG_TEST_V8_REPORT.md", "w", encoding="utf-8") as f:
    f.write("# Language Test V8 — Missing Info & Irrelevant Query Report\n\n")
    f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
    f.write("## Purpose\n")
    f.write("Test how the chatbot handles:\n")
    f.write("1. **Missing Info** — domain-relevant questions but info not in the knowledge base\n")
    f.write("2. **Irrelevant** — completely off-topic queries\n\n")
    f.write("Expected behaviour:\n")
    f.write("- **Missing info**: Bot admits it doesn't have the specific info, does NOT hallucinate, "
            "suggests contacting support/checking official site.\n")
    f.write("- **Irrelevant**: Bot politely declines or redirects to its domain, returns 0 products.\n\n")

    f.write("## Detailed Results\n\n")
    for bot in BOTS:
        bot_id = bot["id"]
        bot_results = [r for r in RESULTS if r["bot_id"] == bot_id]
        f.write(f"### {bot['name']}\n")
        f.write(f"**Domain:** {bot['domain']}  \n")
        f.write(f"**Allowed Languages:** {', '.join(bot['lang_config'])}\n\n")

        f.write("| Lang | Type | Query | Response (first 200 chars) | Products | Admits/Declines | Time |\n")
        f.write("|------|------|-------|----------------------------|----------|--------------------|------|\n")

        for r in bot_results:
            resp_preview = r["response_text"][:200].replace("|", "｜").replace("\n", " ")
            admits_col = ""
            if r["query_type"] == "missing_info":
                admits_col = "✓ admits no info" if r["admits_no_info"] else "✗ no admission"
            elif r["query_type"] == "irrelevant":
                admits_col = "✓ declines" if r["declines_irrelevant"] else "✗ did not decline"
            f.write(f"| {r['query_lang']} | {r['query_type']} | {r['query'][:50]} | "
                    f"{resp_preview} | {len(r['products'])} | {admits_col} | {r['elapsed']}s |\n")
        f.write("\n")

        # Suggestions
        f.write("**Follow-up Suggestions:**\n\n")
        has_suggestions = False
        for r in bot_results:
            if r.get("suggestions"):
                has_suggestions = True
                f.write(f"- [{r['query_lang']}] *{r['query'][:50]}* → {r['suggestions']}\n")
        if not has_suggestions:
            f.write("- No follow-up suggestions returned for any query.\n")
        f.write("\n")

    # ── Issues ────────────────────────────────────────────────────────────────
    f.write("## Issues Found\n\n")
    if not ISSUES:
        f.write("No issues found.\n\n")
    else:
        f.write(f"**Total: {len(ISSUES)} issues**\n\n")
        for i, (bot, lang, qtype, query, issue) in enumerate(ISSUES, 1):
            f.write(f"{i}. **[{bot}][{lang}][{qtype}]** `{query[:60]}` — {issue}\n")
        f.write("\n")

    # ── Strengths ─────────────────────────────────────────────────────────────
    f.write("## Strengths\n\n")
    if not STRENGTHS:
        f.write("No strengths recorded.\n\n")
    else:
        f.write(f"**Total: {len(STRENGTHS)} strengths**\n\n")
        f.write("| Bot | Lang | Type | Query | Strength |\n")
        f.write("|-----|------|------|-------|----------|\n")
        for bot, lang, qtype, query, strength in STRENGTHS:
            f.write(f"| {bot} | {lang} | {qtype} | {query[:40]} | {strength} |\n")
        f.write("\n")

    # ── Improvement Suggestions ────────────────────────────────────────────────
    f.write("## Improvement Suggestions\n\n")

    missing_info_issue_bots = sorted(set(
        b for (b, l, qt, q, _) in ISSUES if qt == "missing_info" and "no admission" in _
    ))
    irrelevant_issue_bots = sorted(set(
        b for (b, l, qt, q, _) in ISSUES if qt == "irrelevant" and "did not decline" in _
    ))
    prod_leakage_bots = sorted(set(
        b for (b, l, qt, q, _) in ISSUES if "product cards" in _
    ))

    if missing_info_issue_bots:
        f.write(f"### 1. Missing-Info Confidence Problem (affects: {', '.join(missing_info_issue_bots)})\n")
        f.write("- **Problem:** Bot answers confidently even when the specific info is not in knowledge base.\n")
        f.write("- **Root Cause:** The system prompt doesn't explicitly instruct the bot to admit knowledge gaps.\n")
        f.write("- **Fix:** Add to system prompt: \"If the question asks about something very specific (custom services, "
                "international shipping, corporate programmes, etc.) and the knowledge base doesn't have clear details, "
                "politely admit you don't have that specific info and suggest the user check the official website or "
                "contact support directly.\"\n\n")

    if irrelevant_issue_bots:
        f.write(f"### 2. Irrelevant Query Not Declined (affects: {', '.join(irrelevant_issue_bots)})\n")
        f.write("- **Problem:** Bot attempts to answer completely off-topic queries.\n")
        f.write("- **Root Cause:** Retrieval confidence threshold (0.35) may not trigger for all off-domain queries, "
                "especially when the query has any semantic overlap with product terms.\n")
        f.write("- **Fix:** Lower irrelevance threshold OR add a domain-description check in the system prompt: "
                "\"If the question is completely unrelated to [brand domain], politely say you can only help with "
                "questions about [brand].\"\n\n")

    if prod_leakage_bots:
        f.write(f"### 3. Product Cards Returned for Non-Product Queries (affects: {', '.join(prod_leakage_bots)})\n")
        f.write("- **Problem:** Product cards appear for queries that should return no products.\n")
        f.write("- **Fix:** Tighter Call1 product classification (recently improved), "
                "and ensure blog/info pages are excluded from product extraction (recently fixed with `/blogs?/` pattern).\n\n")

    f.write("### 4. General Recommendations\n")
    f.write("- Add a section in the system prompt: \"When you don't have the exact information, "
            "say so clearly and direct the user to the official website or customer support.\"\n")
    f.write("- For irrelevant queries, consider adding a hard-coded domain description check in the "
            "out-of-scope detection logic so it triggers for clearly unrelated topics even at higher confidence.\n")
    f.write("- Consider logging which queries triggered missing-info vs out-of-scope paths for analytics.\n\n")

    f.write("## Raw Results\nSee `lang_test_v8_raw.json` for complete response data.\n")

print(f"\nReport written to LANG_TEST_V8_REPORT.md")
print(f"Issues found: {len(ISSUES)}")
print(f"Strengths found: {len(STRENGTHS)}")
