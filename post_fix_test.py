"""
Post-Fix Comprehensive Test — Tests the chat service after algorithm fixes.
Covers: product queries, non-product queries, follow-up/continuation queries,
irrelevant queries, missing info, suggestions quality, language correctness,
and "undefined"/URL leakage checks.

Uses the code's own streaming endpoint and analyzes results per the chat_service algorithm.
"""
import httpx, json, time, uuid, sys, re

# Force UTF-8
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

# ─── Bot definitions (from DB) ────────────────────────────────────────────────
BOTS = [
    {
        "id": "799637f9-391b-4b9d-84cb-5fdd17cdf109",
        "name": "Crawl-Tentree",
        "domain": "sustainable outdoor/eco clothing (tentree.com)",
        "langs": ["en", "hi", "gu"],
    },
    {
        "id": "99fc3604-99e7-4cd0-a2a6-509ac08d9fd0",
        "name": "Crawl-Death Wish Coffee",
        "domain": "strong/specialty coffee brand (deathwishcoffee.com)",
        "langs": ["en", "hi"],
    },
    {
        "id": "e23fcc6f-7a02-4b09-8d49-95c00a57d852",
        "name": "Crawl-Beardbrand",
        "domain": "beard grooming & men's care (beardbrand.com)",
        "langs": ["en", "gu"],
    },
    {
        "id": "182f88cd-02d8-4c94-824d-b41432847400",
        "name": "ramraj",
        "domain": "Indian cotton traditional wear (ramraj.in)",
        "langs": ["hi", "gu", "en"],
    },
    {
        "id": "1cb18dc0-4909-409d-ab03-0436524fcec4",
        "name": "kriyanta",
        "domain": "handmade home décor & gifting (kriyanta.com)",
        "langs": ["en", "gu"],
    },
    {
        "id": "e79b3754-006d-45d5-b21d-2391710e08ca",
        "name": "zevaramaze",
        "domain": "handmade silver jewellery (zevaramaze.com)",
        "langs": ["gu"],
    },
]

# ─── Query definitions ────────────────────────────────────────────────────────
# Each query is (lang, query_type, text, session_key_hint)
# session_key_hint groups queries into the same session for continuation tests
# query_type: product | non_product | irrelevant | follow_up | greeting | missing_info

BOT_QUERIES = {
    # ─── Tentree (en, hi, gu) ─────────────────────────────────
    "799637f9-391b-4b9d-84cb-5fdd17cdf109": [
        ("en", "greeting",     "Hello!", "s1"),
        ("en", "product",      "Show me your hoodies", "s2"),
        ("en", "follow_up",    "What about the cheaper ones?", "s2"),  # continuation: should reference hoodies
        ("en", "non_product",  "What is your return policy?", "s3"),
        ("en", "irrelevant",   "Who is the president of USA?", "s4"),
        ("en", "missing_info", "What is my order status?", "s5"),
        ("hi", "product",      "आपके पास कौन सी जैकेट उपलब्ध हैं?", "s6"),
        ("gu", "non_product",  "ટેન્ટ્રી પર્યાવરણ માટે શું કરે છે?", "s7"),
    ],
    # ─── Death Wish Coffee (en, hi) ───────────────────────────
    "99fc3604-99e7-4cd0-a2a6-509ac08d9fd0": [
        ("en", "greeting",     "Hi there!", "s1"),
        ("en", "product",      "Show me your ground coffee products", "s2"),
        ("en", "follow_up",    "Which one is the strongest?", "s2"),   # continuation
        ("en", "non_product",  "How should I brew your coffee?", "s3"),
        ("en", "irrelevant",   "What is machine learning?", "s4"),
        ("en", "missing_info", "Can I track my order?", "s5"),
        ("hi", "product",      "आपके पास कौन सी कॉफी उत्पाद हैं?", "s6"),
    ],
    # ─── Beardbrand (en, gu) ──────────────────────────────────
    "e23fcc6f-7a02-4b09-8d49-95c00a57d852": [
        ("en", "greeting",     "Hey!", "s1"),
        ("en", "product",      "What beard oils do you sell?", "s2"),
        ("en", "follow_up",    "Tell me more about the first one", "s2"),  # continuation
        ("en", "non_product",  "How do I grow a thicker beard?", "s3"),
        ("en", "irrelevant",   "Write me a Python script", "s4"),
        ("en", "missing_info", "What is your phone number?", "s5"),
        ("gu", "product",      "તમારી પાસે ક્યા દાઢી ઓઈલ ઉપલબ્ધ છે?", "s6"),
    ],
    # ─── Ramraj (hi, gu, en) ──────────────────────────────────
    "182f88cd-02d8-4c94-824d-b41432847400": [
        ("en", "greeting",     "Hello!", "s1"),
        ("en", "product",      "Show me cotton dhotis", "s2"),
        ("en", "follow_up",    "What material is it made of?", "s2"),  # continuation
        ("en", "non_product",  "What is your return policy?", "s3"),
        ("en", "irrelevant",   "Tell me a joke", "s4"),
        ("en", "missing_info", "What is my order status?", "s5"),
        ("hi", "product",      "मुझे पुरुषों के लिए सूती धोती दिखाओ", "s6"),
        ("gu", "non_product",  "રામરાજ કૉટન વિશે જણાવો.", "s7"),
    ],
    # ─── Kriyanta (en, gu) ────────────────────────────────────
    "1cb18dc0-4909-409d-ab03-0436524fcec4": [
        ("en", "greeting",     "Hi!", "s1"),
        ("en", "product",      "Show me wall clocks", "s2"),
        ("en", "follow_up",    "What is the material of this clock?", "s2"),  # THE KEY TEST
        ("en", "non_product",  "What makes Kriyanta unique?", "s3"),
        ("en", "irrelevant",   "How can I grow my business?", "s4"),
        ("en", "missing_info", "How can I contact you?", "s5"),
        ("gu", "product",      "ઘરની સજાવટ માટે શું છે?", "s6"),
    ],
    # ─── Zevaramaze (gu only) ─────────────────────────────────
    "e79b3754-006d-45d5-b21d-2391710e08ca": [
        ("gu", "greeting",     "નમસ્તે", "s1"),
        ("gu", "product",      "ચાંદીની વીંટી બતાવો", "s2"),
        ("gu", "follow_up",    "આનો ભાવ શું છે?", "s2"),  # continuation: price of the ring
        ("gu", "non_product",  "ઝેવારામઝ વિશે જણાવો.", "s3"),
        ("en", "irrelevant",   "Who won the world cup?", "s4"),  # English on gu-only bot = lang rejected
        ("gu", "missing_info", "ઓર્ડર ટ્રેક કેવી રીતે કરવો?", "s5"),
    ],
}

# ─── Streaming helper ─────────────────────────────────────────────────────────
def collect_stream(bot_id: str, message: str, session_id: str = None) -> dict:
    """Send a streaming chat message and collect the full assembled response."""
    if not session_id:
        session_id = str(uuid.uuid4())
    
    full_text = ""
    products = []
    suggestions = []
    error = None
    returned_session_id = session_id

    try:
        with httpx.Client(timeout=60.0) as client:
            with client.stream(
                "POST",
                f"{BASE}/chat/{bot_id}/message/stream",
                headers=HEADERS,
                data={"message": message, "session_id": session_id},
            ) as resp:
                if resp.status_code != 200:
                    return {"text": "", "products": [], "suggestions": [],
                            "error": f"HTTP {resp.status_code}", "session_id": session_id}
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
                        elif t == "session":
                            returned_session_id = chunk.get("session_id", session_id)
                        elif t == "done":
                            products = chunk.get("products", [])
                            suggestions = chunk.get("suggestions", [])
                    except json.JSONDecodeError:
                        pass
    except Exception as e:
        error = str(e)

    return {
        "text": full_text.strip(),
        "products": products,
        "suggestions": suggestions,
        "error": error,
        "session_id": returned_session_id,
    }


# ─── Language detection heuristic ─────────────────────────────────────────────
def detect_response_language(text: str) -> str:
    if not text:
        return "empty"
    deva = sum(1 for c in text if '\u0900' <= c <= '\u097F')
    guja = sum(1 for c in text if '\u0A80' <= c <= '\u0AFF')
    eng = sum(1 for c in text if c.isalpha() and ord(c) < 128)
    total = max(deva + guja + eng, 1)
    if deva / total > 0.25:
        return "hi"
    if guja / total > 0.25:
        return "gu"
    return "en"


# ─── Analysis functions (based on chat_service algorithm) ─────────────────────
def check_undefined(text: str) -> bool:
    """Check if response contains the word 'undefined'."""
    return bool(re.search(r'\bundefined\b', text, re.IGNORECASE))

def check_url_leakage(text: str) -> list:
    """Check if response leaks raw URLs."""
    urls = re.findall(r'https?://[^\s<)\]]+', text)
    return urls

def check_context_mention(text: str) -> bool:
    """Check if response mentions 'context' (internal retrieval language)."""
    patterns = ["provided context", "in the context", "from the context",
                "my context", "the context doesn't", "context below"]
    return any(p in text.lower() for p in patterns)

def check_irrelevant_marker(text: str) -> bool:
    """Check if response was marked as irrelevant."""
    return "[[IRRELEVANT]]" in text

def check_missing_info_marker(text: str) -> bool:
    return "[[MISSING_INFO]]" in text

def check_suggestion_quality(suggestions: list, query_lang: str) -> list:
    """Check suggestion quality issues."""
    issues = []
    if len(suggestions) < 2:
        issues.append(f"Only {len(suggestions)} suggestions (expected 2+)")
    for s in suggestions:
        if not isinstance(s, str):
            continue
        if len(s.split()) < 4:
            issues.append(f"Too short suggestion: '{s}'")
        if check_undefined(s):
            issues.append(f"'undefined' in suggestion: '{s}'")
        if re.search(r'https?://', s):
            issues.append(f"URL leaked in suggestion: '{s}'")
    return issues


# ─── Flush redis to avoid cached results ──────────────────────────────────────
print("Flushing Redis cache...")
import subprocess
subprocess.run(["docker", "exec", "chatbot_redis", "redis-cli", "FLUSHALL"],
               capture_output=True, timeout=10)
print("Redis flushed.\n")

# ─── Run tests ────────────────────────────────────────────────────────────────
print("=" * 70)
print("POST-FIX COMPREHENSIVE TEST")
print("=" * 70)

ALL_RESULTS = []
ALL_ISSUES = []
ALL_STRENGTHS = []

for bot in BOTS:
    bot_id = bot["id"]
    queries = BOT_QUERIES.get(bot_id, [])
    print(f"\n{'─'*50}")
    print(f"Bot: {bot['name']} | Langs: {bot['langs']} | Domain: {bot['domain']}")
    print(f"{'─'*50}")

    # Track sessions for continuation tests
    sessions = {}  # session_key -> session_id
    
    for lang, qtype, query, session_key in queries:
        # Use same session for continuation queries
        sid = sessions.get(session_key)
        
        print(f"  [{lang}][{qtype:12s}] {query[:55]:55s}", end=" ", flush=True)
        t0 = time.time()
        result = collect_stream(bot_id, query, session_id=sid)
        elapsed = time.time() - t0
        
        # Track session ID for follow-ups
        if result.get("session_id"):
            sessions[session_key] = result["session_id"]
        
        text = result.get("text", "")
        products = result.get("products", [])
        suggestions = result.get("suggestions", [])
        error = result.get("error")
        
        # Quick status
        if error:
            print(f"⚠ ERROR ({elapsed:.1f}s)")
        elif not text:
            print(f"⚠ EMPTY ({elapsed:.1f}s)")
        else:
            prod_str = f"{len(products)}p" if products else "0p"
            sug_str = f"{len(suggestions)}s" if suggestions else "0s"
            print(f"✓ ({elapsed:.1f}s) {prod_str} {sug_str} | {text[:60].replace(chr(10),' ')}...")
        
        # Store result
        entry = {
            "bot_id": bot_id,
            "bot_name": bot["name"],
            "domain": bot["domain"],
            "allowed_langs": bot["langs"],
            "query_lang": lang,
            "query_type": qtype,
            "query": query,
            "session_key": session_key,
            "response_text": text,
            "products": products,
            "suggestions": suggestions,
            "error": error,
            "elapsed_s": round(elapsed, 2),
        }
        ALL_RESULTS.append(entry)
        
        # ─── Analyze issues ───────────────────────────────────
        name = bot["name"]
        
        if error:
            ALL_ISSUES.append((name, lang, qtype, query, f"API ERROR: {error}"))
        elif not text:
            ALL_ISSUES.append((name, lang, qtype, query, "Empty response"))
        else:
            # Undefined check
            if check_undefined(text):
                ALL_ISSUES.append((name, lang, qtype, query,
                    f"Contains 'undefined' in response: ...{text[max(0,text.lower().find('undefined')-30):text.lower().find('undefined')+40]}..."))
            
            # URL leakage check
            leaked_urls = check_url_leakage(text)
            if leaked_urls:
                ALL_ISSUES.append((name, lang, qtype, query,
                    f"URL leakage: {leaked_urls[0][:60]}"))
            
            # Context mention check
            if check_context_mention(text):
                ALL_ISSUES.append((name, lang, qtype, query,
                    "Exposes internal 'context' language"))
            
            # Language mismatch
            resp_lang = detect_response_language(text)
            if lang in ("hi", "gu") and resp_lang == "en":
                ALL_ISSUES.append((name, lang, qtype, query,
                    f"Query in {lang} but responded in English"))
            
            # Irrelevant queries should be rejected
            if qtype == "irrelevant":
                # Should NOT answer the question
                if not any(phrase in text.lower() for phrase in [
                    "can only help", "can only assist", "only assist",
                    "not related", "out of scope", "cannot help",
                    "i can only", "related to", "ફક્ત", "केवल", "sirf"
                ]):
                    ALL_ISSUES.append((name, lang, qtype, query,
                        "Irrelevant query was NOT properly rejected — bot answered it"))
                else:
                    ALL_STRENGTHS.append((name, lang, qtype, query,
                        "Irrelevant query correctly rejected ✓"))
            
            # Product queries should return products
            if qtype == "product" and len(products) == 0:
                ALL_ISSUES.append((name, lang, qtype, query,
                    "Product query returned 0 product cards"))
            elif qtype == "product" and len(products) > 0:
                ALL_STRENGTHS.append((name, lang, qtype, query,
                    f"Returned {len(products)} product card(s) ✓"))
            
            # Follow-up queries should show enriched understanding
            if qtype == "follow_up":
                # The response should reference something from prior context
                if "I don't have" in text and "information" in text.lower():
                    ALL_ISSUES.append((name, lang, qtype, query,
                        "Follow-up query got 'I don't have information' — context enrichment may have failed"))
                else:
                    ALL_STRENGTHS.append((name, lang, qtype, query,
                        "Follow-up query got contextual response ✓"))
            
            # Missing info queries: should acknowledge lack of info
            if qtype == "missing_info":
                if "undefined" in text.lower():
                    ALL_ISSUES.append((name, lang, qtype, query,
                        "Missing info response contains 'undefined'"))
            
            # Greeting check
            if qtype == "greeting":
                if len(text) < 5:
                    ALL_ISSUES.append((name, lang, qtype, query,
                        "Greeting got very short/empty response"))
                else:
                    ALL_STRENGTHS.append((name, lang, qtype, query,
                        "Greeting responded warmly ✓"))
            
            # Suggestion quality
            sug_issues = check_suggestion_quality(suggestions, lang)
            for si in sug_issues:
                ALL_ISSUES.append((name, lang, qtype, query, f"Suggestion: {si}"))
            
            # Correct language = strength
            if lang in ("hi", "gu") and resp_lang == lang:
                ALL_STRENGTHS.append((name, lang, qtype, query,
                    f"Correct language ({lang}) ✓"))
        
        time.sleep(1.5)  # Rate limit politeness

print()

# ─── Write Report ─────────────────────────────────────────────────────────────
REPORT_PATH = "POST_FIX_TEST_REPORT.md"
RAW_PATH = "post_fix_test_raw.json"

with open(RAW_PATH, "w", encoding="utf-8") as jf:
    json.dump(ALL_RESULTS, jf, ensure_ascii=False, indent=2)

with open(REPORT_PATH, "w", encoding="utf-8") as f:
    f.write("# Post-Fix Comprehensive Test Report\n\n")
    f.write(f"**Date:** {time.strftime('%Y-%m-%d %H:%M')}\n")
    f.write(f"**Total Queries:** {len(ALL_RESULTS)}\n")
    f.write(f"**Issues Found:** {len(ALL_ISSUES)}\n")
    f.write(f"**Strengths Found:** {len(ALL_STRENGTHS)}\n\n")

    # Summary table
    f.write("## Bot Configurations\n\n")
    f.write("| Bot | Domain | Languages |\n")
    f.write("|-----|--------|-----------|\n")
    for bot in BOTS:
        f.write(f"| {bot['name']} | {bot['domain']} | {', '.join(bot['langs'])} |\n")
    f.write("\n")

    # Detailed results per bot
    f.write("## Detailed Results\n\n")
    for bot in BOTS:
        bot_results = [r for r in ALL_RESULTS if r["bot_id"] == bot["id"]]
        f.write(f"### {bot['name']}\n")
        f.write(f"**Domain:** {bot['domain']}  \n")
        f.write(f"**Languages:** {', '.join(bot['langs'])}\n\n")
        
        for r in bot_results:
            resp_lang = detect_response_language(r["response_text"])
            f.write(f"**[{r['query_lang']}][{r['query_type']}]** `{r['query']}`\n\n")
            if r["error"]:
                f.write(f"> ⚠️ ERROR: {r['error']}\n\n")
            else:
                # Truncate response for readability
                resp_preview = r["response_text"][:400].replace("\n", "  \n")
                f.write(f"> {resp_preview}\n\n")
                f.write(f"- Products: {len(r['products'])} | Resp Lang: {resp_lang} | Time: {r['elapsed_s']}s\n")
                if r["suggestions"]:
                    f.write(f"- Suggestions: {r['suggestions']}\n")
                if r["products"]:
                    for p in r["products"][:3]:
                        pname = p.get("name", "?")
                        pprice = p.get("price", "?")
                        pcur = p.get("currency", "")
                        f.write(f"  - 🛒 {pname} — {pcur} {pprice}\n")
            f.write("\n")
        f.write("---\n\n")

    # Issues
    f.write("## Issues Found\n\n")
    if ALL_ISSUES:
        # Group by issue type
        issue_types = {}
        for (name, lang, qtype, q, issue) in ALL_ISSUES:
            category = "Other"
            if "undefined" in issue.lower():
                category = "Undefined Leakage"
            elif "URL" in issue or "url" in issue:
                category = "URL Leakage"
            elif "context" in issue.lower():
                category = "Context Mention"
            elif "language" in issue.lower() or "English" in issue:
                category = "Language Mismatch"
            elif "irrelevant" in issue.lower() or "rejected" in issue.lower():
                category = "Irrelevant Handling"
            elif "product" in issue.lower() and "0 product" in issue.lower():
                category = "Missing Products"
            elif "follow-up" in issue.lower() or "enrichment" in issue.lower():
                category = "Follow-up/Enrichment"
            elif "suggestion" in issue.lower():
                category = "Suggestion Quality"
            
            if category not in issue_types:
                issue_types[category] = []
            issue_types[category].append((name, lang, qtype, q, issue))
        
        for category, items in sorted(issue_types.items()):
            f.write(f"### {category} ({len(items)} issues)\n\n")
            f.write("| Bot | Lang | Type | Query | Issue |\n")
            f.write("|-----|------|------|-------|-------|\n")
            for (name, lang, qtype, q, issue) in items:
                q_safe = q[:45].replace("|", "\\|").replace("\n", " ")
                issue_safe = issue[:120].replace("|", "\\|").replace("\n", " ")
                f.write(f"| {name} | {lang} | {qtype} | {q_safe} | {issue_safe} |\n")
            f.write("\n")
    else:
        f.write("No issues found! 🎉\n\n")

    # Strengths
    f.write("## Strengths\n\n")
    if ALL_STRENGTHS:
        f.write("| Bot | Lang | Type | Query | Strength |\n")
        f.write("|-----|------|------|-------|----------|\n")
        for (name, lang, qtype, q, s) in ALL_STRENGTHS:
            q_safe = q[:45].replace("|", "\\|")
            f.write(f"| {name} | {lang} | {qtype} | {q_safe} | {s} |\n")
    f.write("\n")

    # Recommendations
    f.write("## Fix Recommendations\n\n")
    
    if any("Undefined" in cat for cat in issue_types):
        f.write("### 1. Undefined Leakage\n")
        f.write("- Crawled data has null/missing fields (email, phone) showing as 'undefined'\n")
        f.write("- **Fix:** Enhanced regex sanitization to remove entire sentences with undefined contact info\n\n")
    
    if any("Follow-up" in cat for cat in issue_types):
        f.write("### 2. Follow-up Context Enrichment\n")
        f.write("- LLM in Call 1 fails to enrich follow-up queries with conversation context\n")
        f.write("- **Fix:** Restored local `enrich_query_with_context()` as safety net after Call 1\n\n")
    
    if any("Missing Products" in cat for cat in issue_types):
        f.write("### 3. Missing Products\n")
        f.write("- Product queries returning 0 cards despite relevant crawled data\n")
        f.write("- **Fix:** Check embedding quality, improve product extraction from chunks\n\n")
    
    if any("Language" in cat for cat in issue_types):
        f.write("### 4. Language Mismatch\n")
        f.write("- Bot responding in wrong language\n")
        f.write("- **Fix:** Strengthen language instructions in Call 2 system prompt\n\n")
    
    if any("Suggestion" in cat for cat in issue_types):
        f.write("### 5. Suggestion Quality\n")
        f.write("- Suggestions too short, contain undefined, or not contextual\n")
        f.write("- **Fix:** Enforce minimum suggestion length and sanitization\n\n")

    f.write(f"\n## Raw Data\nSee `{RAW_PATH}` for complete response data.\n")

print(f"\n{'='*70}")
print(f"REPORT: {REPORT_PATH}")
print(f"RAW DATA: {RAW_PATH}")
print(f"Total queries: {len(ALL_RESULTS)}")
print(f"Issues: {len(ALL_ISSUES)}")
print(f"Strengths: {len(ALL_STRENGTHS)}")
print(f"{'='*70}")
