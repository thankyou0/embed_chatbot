"""
Irrelevant Query Test V9 — Tests all queries from irrelevant_queries.json.
Relies ONLY on the code's built-in algorithm:
  - metadata_json.is_irrelevant  (set by [[IRRELEVANT]] tag detection)
  - metadata_json.response_language
  - product count from done event
  - response text (for human review)
Does NOT use custom keyword heuristics.
"""
import httpx, json, time, uuid, sys, os
from datetime import datetime

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


# ─── Load queries ─────────────────────────────────────────────────────────────
with open("irrelevant_queries.json", "r", encoding="utf-8") as f:
    data = json.load(f)

ALL_QUERIES = []
for bot_entry in data["bots"]:
    for q in bot_entry["queries"]:
        ALL_QUERIES.append({
            "bot_name": bot_entry["bot"],
            "bot_id": bot_entry["bot_id"],
            "domain": bot_entry["domain"],
            "lang": q["lang"],
            "query": q["query"],
        })

print(f"Loaded {len(ALL_QUERIES)} irrelevant queries across {len(data['bots'])} bots\n")


# ─── Stream Collector ────────────────────────────────────────────────────────
def collect_stream(bot_id: str, message: str) -> dict:
    session_id = str(uuid.uuid4())
    full_text = ""
    products = []
    suggestions = []
    error = None

    try:
        with httpx.Client(timeout=httpx.Timeout(180.0, connect=30.0)) as client:
            with client.stream(
                "POST",
                f"{BASE}/chat/{bot_id}/message/stream",
                data={"message": message, "session_id": session_id, "is_preview": "true"},
            ) as resp:
                if resp.status_code != 200:
                    return {"error": f"HTTP {resp.status_code}: {resp.read()[:200].decode()}",
                            "session_id": session_id}
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
                                products = chunk.get("products", [])
                                suggestions = chunk.get("suggestions", [])
                            elif t == "error":
                                error = chunk.get("error", "unknown error")
                        except json.JSONDecodeError:
                            pass
                except Exception as stream_err:
                    if not full_text:
                        error = f"Stream error: {stream_err}"
    except Exception as e:
        error = str(e)

    return {
        "text": full_text.strip(),
        "products": products,
        "suggestions": suggestions,
        "error": error,
        "session_id": session_id,
    }


# ─── Run all queries ─────────────────────────────────────────────────────────
results = []
timestamp_before = datetime.utcnow().isoformat()

for i, q in enumerate(ALL_QUERIES, 1):
    label = f"[{i}/{len(ALL_QUERIES)}] {q['bot_name']} ({q['lang']})"
    print(f"{label}: {q['query'][:60]}...", end=" ", flush=True)
    t0 = time.time()
    resp = collect_stream(q["bot_id"], q["query"])
    elapsed = round(time.time() - t0, 1)

    product_count = len(resp.get("products", []))
    text_preview = resp.get("text", "")[:150].replace("\n", " ")

    status = "OK" if not resp.get("error") else f"ERR: {resp['error'][:60]}"
    print(f"  {elapsed}s | products={product_count} | {status}")

    results.append({
        "bot_name": q["bot_name"],
        "bot_id": q["bot_id"],
        "domain": q["domain"],
        "lang": q["lang"],
        "query": q["query"],
        "response_text": resp.get("text", ""),
        "response_preview": text_preview,
        "product_count": product_count,
        "products": resp.get("products", []),
        "suggestions": resp.get("suggestions", []),
        "session_id": resp.get("session_id", ""),
        "elapsed_s": elapsed,
        "error": resp.get("error"),
    })

    # Small pause to avoid overwhelming the API
    time.sleep(1)

# Save raw results
with open("irrelevant_v9_raw.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n{'='*60}")
print(f"All {len(results)} queries sent. Raw results saved to irrelevant_v9_raw.json")
print(f"Now querying DB for actual metadata flags...\n")

# ─── Query DB for actual flags ──────────────────────────────────────────────
# Get all assistant messages created after we started testing
import subprocess

db_query = f"""
SELECT
    cm.session_id,
    cm.content,
    cm.metadata_json->>'is_irrelevant' as is_irrelevant,
    cm.metadata_json->>'is_missing_info' as is_missing_info,
    cm.metadata_json->>'was_answered' as was_answered,
    cm.metadata_json->>'retrieval_confidence' as confidence,
    cm.metadata_json->>'response_language' as resp_lang,
    cm.metadata_json->>'effective_language' as eff_lang,
    cm.metadata_json->>'is_product_request' as is_product_request,
    cm.created_at
FROM chat_messages cm
WHERE cm.role = 'assistant'
  AND cm.created_at > '{timestamp_before}'
ORDER BY cm.created_at ASC;
"""

print("Running DB query to get metadata flags...")
db_cmd = f'docker exec chatbot_postgres psql -U postgres -d embed_chatbot -t -A -F "|" -c "{db_query}"'
try:
    db_result = subprocess.run(db_cmd, shell=True, capture_output=True, text=True, timeout=30, encoding="utf-8")
    db_lines = [l.strip() for l in db_result.stdout.strip().split("\n") if l.strip()]
except Exception as e:
    print(f"DB query error: {e}")
    db_lines = []

# Parse DB results into a dict keyed by session_id
db_flags = {}
for line in db_lines:
    parts = line.split("|")
    if len(parts) >= 10:
        session_id = parts[0].strip()
        db_flags[session_id] = {
            "is_irrelevant": parts[2].strip(),
            "is_missing_info": parts[3].strip(),
            "was_answered": parts[4].strip(),
            "confidence": parts[5].strip(),
            "resp_lang": parts[6].strip(),
            "eff_lang": parts[7].strip(),
            "is_product_request": parts[8].strip(),
        }

print(f"Found {len(db_flags)} DB records matching test sessions\n")

# ─── Merge DB flags into results ────────────────────────────────────────────
for r in results:
    sid = r.get("session_id", "")
    if sid in db_flags:
        r["db_flags"] = db_flags[sid]
    else:
        r["db_flags"] = None

# Save merged results
with open("irrelevant_v9_raw.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)


# ─── Analysis ────────────────────────────────────────────────────────────────
print("=" * 70)
print("IRRELEVANT QUERY TEST V9 — ANALYSIS")
print("=" * 70)
print(f"Total queries: {len(results)}")
print(f"All queries are type=irrelevant (bot should NOT answer these)\n")

pass_count = 0
fail_count = 0
issues = []

for r in results:
    flags = r.get("db_flags")
    query_short = r["query"][:50]
    bot = r["bot_name"]
    lang = r["lang"]

    row_issues = []

    if r.get("error"):
        row_issues.append(f"API error: {r['error'][:80]}")
    elif flags is None:
        row_issues.append("No DB flags found (session not recorded)")
    else:
        # CHECK 1: is_irrelevant should be True
        irr = flags.get("is_irrelevant", "")
        if irr.lower() != "true":
            row_issues.append(f"is_irrelevant={irr} (expected true)")

        # CHECK 2: products should be 0
        if r["product_count"] > 0:
            row_issues.append(f"products={r['product_count']} (expected 0)")

        # CHECK 3: response language should match query language
        resp_lang = flags.get("resp_lang", "")
        eff_lang = flags.get("eff_lang", "")
        # Accept if resp_lang starts with expected lang code
        if lang != "en":
            if not resp_lang.startswith(lang):
                row_issues.append(f"resp_lang={resp_lang} (expected {lang}*)")

        # CHECK 4: was_answered should be False (bot should decline)
        was_ans = flags.get("was_answered", "")
        if was_ans.lower() == "true":
            row_issues.append(f"was_answered=true (bot answered an irrelevant query)")

        # CHECK 5: confidence (informational)
        conf = flags.get("confidence", "?")

    if row_issues:
        fail_count += 1
        issues.append({
            "bot": bot,
            "lang": lang,
            "query": r["query"],
            "issues": row_issues,
            "flags": flags,
            "product_count": r["product_count"],
            "response_preview": r["response_preview"],
        })
    else:
        pass_count += 1

    status_mark = "PASS" if not row_issues else "FAIL"
    flags_summary = ""
    if flags:
        flags_summary = (f" | irr={flags.get('is_irrelevant','?')}"
                        f" conf={flags.get('confidence','?')}"
                        f" resp_lang={flags.get('resp_lang','?')}"
                        f" answered={flags.get('was_answered','?')}"
                        f" prods={r['product_count']}")
    print(f"  [{status_mark}] {bot:12s} {lang:3s} | {query_short:50s}{flags_summary}")

# ─── Summary ─────────────────────────────────────────────────────────────────
print(f"\n{'='*70}")
print(f"RESULTS: {pass_count} PASS / {fail_count} FAIL out of {len(results)} queries")
print(f"Pass rate: {pass_count/len(results)*100:.0f}%")
print(f"{'='*70}")

if issues:
    print(f"\n{'─'*70}")
    print("FAILURES DETAIL:")
    print(f"{'─'*70}")
    for idx, iss in enumerate(issues, 1):
        print(f"\n  #{idx} [{iss['bot']}] [{iss['lang']}]")
        print(f"     Query: {iss['query']}")
        print(f"     Issues: {'; '.join(iss['issues'])}")
        if iss.get('flags'):
            print(f"     DB Flags: {json.dumps(iss['flags'], ensure_ascii=False)}")
        print(f"     Products: {iss['product_count']}")
        print(f"     Response: {iss['response_preview'][:120]}")

# ─── Save full report ────────────────────────────────────────────────────────
report = {
    "test": "Irrelevant Query Test V9",
    "timestamp": datetime.utcnow().isoformat(),
    "total": len(results),
    "pass": pass_count,
    "fail": fail_count,
    "pass_rate": f"{pass_count/len(results)*100:.0f}%",
    "issues": issues,
    "results": results,
}
with open("irrelevant_v9_report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print(f"\nFull report saved to irrelevant_v9_report.json")
print("Done.")
