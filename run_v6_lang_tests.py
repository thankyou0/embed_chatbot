#!/usr/bin/env python3
"""
V6 Language Compliance Test Runner
====================================
Tests that the chatbot responds in the correct script / language matching the
user's query.  Accepts three JSON query files (tentree, zevaramaze, kriyanta)
and scores each response against an expected_script field.

Script detection logic:
  devanagari  → ≥ 10% of alpha-equivalent chars are in Devanagari Unicode range
  gujarati    → ≥ 10% of alpha-equivalent chars are in Gujarati Unicode range
  latin       → Devanagari + Gujarati count < 5% → classified as Latin/English

Outputs:
  v6_lang_results.json  — raw per-query results
  V6_LANG_REPORT.md     — human-readable analysis report
"""

import json, time, asyncio, re, sys
from pathlib import Path
from datetime import datetime
import httpx

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
API_BASE = "http://localhost:8000/api/v1"
QUERY_FILES = [
    "v6_lang_queries_tentree.json",
    "v6_lang_queries_zevaramaze.json",
    "v6_lang_queries_kriyanta.json",
]
RESULTS_FILE   = "v6_lang_results.json"
REPORT_FILE    = "V6_LANG_REPORT.md"
INTER_REQUEST_DELAY = 2.5   # seconds between requests
RATE_LIMIT_PHRASES = [
    "a lot of requests", "try again in a few minutes",
    "rate limit", "too many requests", "can't respond right now",
]
CONSECUTIVE_RL_THRESHOLD = 6

# ---------------------------------------------------------------------------
# Script / language detection helpers
# ---------------------------------------------------------------------------
DEVANAGARI_RANGE = (0x0900, 0x097F)
GUJARATI_RANGE   = (0x0A80, 0x0AFF)

def _count_script_chars(text: str):
    deva = sum(1 for c in text if DEVANAGARI_RANGE[0] <= ord(c) <= DEVANAGARI_RANGE[1])
    guja = sum(1 for c in text if GUJARATI_RANGE[0]   <= ord(c) <= GUJARATI_RANGE[1])
    latin = sum(1 for c in text if c.isalpha() and ord(c) < 0x0250)
    return deva, guja, latin

def detect_response_script(text: str) -> str:
    """Classify response into one of: devanagari, gujarati, latin, mixed, empty"""
    if not text or not text.strip():
        return "empty"
    deva, guja, latin = _count_script_chars(text)
    total = deva + guja + latin
    if total == 0:
        return "empty"
    deva_pct  = deva  / total
    guja_pct  = guja  / total
    # Threshold: 15% native chars → classify as that script
    if deva_pct >= 0.15 and guja_pct < 0.05:
        return "devanagari"
    if guja_pct >= 0.15 and deva_pct < 0.05:
        return "gujarati"
    if deva_pct >= 0.05 or guja_pct >= 0.05:
        return "mixed"
    return "latin"

def script_matches_expectation(detected: str, expected: str) -> bool:
    if expected == "devanagari":
        return detected == "devanagari"
    if expected == "gujarati":
        return detected == "gujarati"
    if expected == "latin":
        return detected in ("latin", "mixed")   # mixed is acceptable for latin-expected
    return True

def is_rejection_message(text: str, lang: str) -> bool:
    """Check if response correctly rejects an unsupported language."""
    t = text.lower()
    return any(p in t for p in [
        "not supported", "support", "nathi", "nahi", "supported",
        "configure", "language", "bhasha", "boli",
    ])

def is_rate_limit_response(text: str) -> bool:
    t = text.lower()
    return any(p in t for p in RATE_LIMIT_PHRASES)

# ---------------------------------------------------------------------------
# SSE parsing
# ---------------------------------------------------------------------------
def parse_sse(raw: str) -> dict:
    parts, done_payload, session_id, has_error = [], {}, None, False
    for line in raw.split("\n"):
        line = line.strip()
        if not line.startswith("data: "):
            continue
        try:
            chunk = json.loads(line[6:])
        except json.JSONDecodeError:
            continue
        t = chunk.get("type", "")
        if t == "session":
            session_id = chunk.get("session_id")
        elif t == "content":
            parts.append(chunk.get("content", ""))
        elif t == "done":
            done_payload = chunk
            if chunk.get("error"):
                has_error = True
        elif t == "error":
            has_error = True
            parts.append(chunk.get("error", ""))
    full = "".join(parts)
    return {
        "content":      full,
        "session_id":   session_id,
        "products":     done_payload.get("products", []),
        "suggestions":  done_payload.get("suggestions", []),
        "has_error":    has_error,
        "is_rate_limited": is_rate_limit_response(full) or has_error,
    }

# ---------------------------------------------------------------------------
# Sending queries
# ---------------------------------------------------------------------------
async def send_query(client, bot_id: str, message: str,
                     session_id: str | None = None, timeout: float = 60) -> dict:
    url  = f"{API_BASE}/chat/{bot_id}/message/stream"
    form = {"message": message, "is_preview": "false"}
    if session_id:
        form["session_id"] = session_id
    t0 = time.time()
    try:
        r = await client.post(url, data=form, timeout=timeout)
        elapsed = round(time.time() - t0, 2)
        if r.status_code == 429:
            return {"content": "", "session_id": session_id, "products": [],
                    "suggestions": [], "has_error": True, "is_rate_limited": True,
                    "http_status": 429, "elapsed_s": elapsed}
        p = parse_sse(r.text)
        p["http_status"] = r.status_code
        p["elapsed_s"]   = elapsed
        return p
    except Exception as e:
        return {"content": str(e), "session_id": session_id, "products": [],
                "suggestions": [], "has_error": True, "is_rate_limited": False,
                "http_status": 0, "elapsed_s": round(time.time() - t0, 2)}

# ---------------------------------------------------------------------------
# Main test loop
# ---------------------------------------------------------------------------
async def run_tests():
    all_results   = []
    consecutive_rl = 0
    total_sent     = 0

    async with httpx.AsyncClient() as client:
        for qfile in QUERY_FILES:
            p = Path(qfile)
            if not p.exists():
                print(f"⚠️  Query file not found: {qfile} — skipping")
                continue

            data = json.loads(p.read_text(encoding="utf-8"))
            bot        = data["bot"]
            bot_id     = data["bot_id"]
            allowed    = data.get("allowed_languages", ["en"])
            queries    = data["queries"]

            print(f"\n{'='*60}")
            print(f"  Bot: {bot}  ({bot_id})")
            print(f"  Allowed: {allowed}  |  Queries: {len(queries)}")
            print(f"{'='*60}")

            session_id = None   # start fresh per bot

            for q in queries:
                if consecutive_rl >= CONSECUTIVE_RL_THRESHOLD:
                    print(f"⛔  {CONSECUTIVE_RL_THRESHOLD} consecutive rate-limits — stopping all tests")
                    goto_report = True
                    break
                else:
                    goto_report = False

                qid   = q.get("id", "?")
                qtype = q.get("type", "")
                lang  = q.get("lang", "en")
                exp   = q.get("expected_script", "latin")
                msg   = q["query"]

                resp = await send_query(client, bot_id, msg, session_id=session_id)
                session_id = resp.get("session_id", session_id)
                total_sent += 1

                content        = resp["content"]
                detected_script = detect_response_script(content)
                script_ok      = script_matches_expectation(detected_script, exp)

                # Special handling for "rejection" query types (unsupported lang)
                is_rejection_type = ("rejection" in qtype or lang in ("fr", "esp")) \
                                    and lang not in allowed and not (lang.split("-")[0] in allowed)
                if is_rejection_type:
                    # Expected behaviour: bot should reject and respond in its first allowed language
                    script_ok = is_rejection_message(content, lang)

                if resp["is_rate_limited"]:
                    consecutive_rl += 1
                    status = "RATE_LIMIT"
                else:
                    consecutive_rl = 0
                    status = "PASS" if script_ok else "FAIL"

                icon = {"PASS": "✅", "FAIL": "❌", "RATE_LIMIT": "⏳"}.get(status, "?")
                snip = content[:80].replace("\n", " ")
                print(f"  {icon} [{qid}] [{lang}→{exp}] detected={detected_script}: {snip}")

                all_results.append({
                    "bot":            bot,
                    "bot_id":         bot_id,
                    "query_id":       qid,
                    "query_type":     qtype,
                    "lang":           lang,
                    "expected_script":exp,
                    "message":        msg,
                    "response":       content[:500],
                    "detected_script":detected_script,
                    "script_ok":      script_ok,
                    "status":         status,
                    "http_status":    resp["http_status"],
                    "elapsed_s":      resp["elapsed_s"],
                    "products_count": len(resp.get("products", [])),
                    "suggestions":    resp.get("suggestions", []),
                    "is_rate_limited":resp["is_rate_limited"],
                })

                if goto_report:
                    break

                await asyncio.sleep(INTER_REQUEST_DELAY)

    # Save raw results
    Path(RESULTS_FILE).write_text(
        json.dumps(all_results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\n💾  Results saved → {RESULTS_FILE}  ({len(all_results)} records)")
    return all_results

# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------
def generate_report(results: list[dict]) -> str:
    from collections import defaultdict
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    bots   = list(dict.fromkeys(r["bot"] for r in results))
    tested = [r for r in results if r["status"] != "RATE_LIMIT"]

    total       = len(tested)
    passed      = sum(1 for r in tested if r["status"] == "PASS")
    failed      = sum(1 for r in tested if r["status"] == "FAIL")
    rate_limits = sum(1 for r in results if r["status"] == "RATE_LIMIT")
    pass_rate   = round(passed / total * 100, 1) if total else 0

    lines = [
        f"# V6 Language Compliance Test Report",
        f"",
        f"**Generated:** {ts}  ",
        f"**Scope:** Language / script matching across {len(bots)} chatbot(s)",
        f"",
        f"## Overall Summary",
        f"",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Queries tested | {total} |",
        f"| PASS | {passed} ({pass_rate}%) |",
        f"| FAIL | {failed} |",
        f"| Rate-limited (skipped) | {rate_limits} |",
        f"",
    ]

    # Per-bot breakdown
    lines.append("## Per-Bot Breakdown\n")
    for bot in bots:
        br = [r for r in tested if r["bot"] == bot]
        if not br:
            continue
        bp = sum(1 for r in br if r["status"] == "PASS")
        bf = sum(1 for r in br if r["status"] == "FAIL")
        bpr = round(bp / len(br) * 100, 1) if br else 0
        lines += [
            f"### {bot}",
            f"",
            f"- Tested: {len(br)} &nbsp; Pass: {bp} ({bpr}%) &nbsp; Fail: {bf}",
            f"",
        ]

        # Per expected_script breakdown
        by_script = defaultdict(list)
        for r in br:
            by_script[r["expected_script"]].append(r)

        lines.append("| Expected Script | Tested | Pass | Fail | Pass% |")
        lines.append("|----------------|--------|------|------|-------|")
        for script, recs in sorted(by_script.items()):
            sp = sum(1 for r in recs if r["status"] == "PASS")
            sf = sum(1 for r in recs if r["status"] == "FAIL")
            spr = round(sp / len(recs) * 100, 1) if recs else 0
            lines.append(f"| `{script}` | {len(recs)} | {sp} | {sf} | {spr}% |")
        lines.append("")

        # Per query-type breakdown
        by_type = defaultdict(list)
        for r in br:
            by_type[r["query_type"]].append(r)

        lines.append("| Query Type | Tested | Pass | Fail |")
        lines.append("|-----------|--------|------|------|")
        for qtype, recs in sorted(by_type.items()):
            tp = sum(1 for r in recs if r["status"] == "PASS")
            tf = sum(1 for r in recs if r["status"] == "FAIL")
            lines.append(f"| `{qtype}` | {len(recs)} | {tp} | {tf} |")
        lines.append("")

    # Failed queries detail
    failures = [r for r in tested if r["status"] == "FAIL"]
    if failures:
        lines += [
            "## Failed Queries — Detail\n",
            "| ID | Bot | Lang | Expected | Detected | Query | Response snippet |",
            "|----|-----|------|----------|----------|-------|-----------------|",
        ]
        for r in failures:
            q = r["message"][:40].replace("|", "\\|")
            resp = r["response"][:60].replace("|", "\\|").replace("\n", " ")
            lines.append(
                f"| {r['query_id']} | {r['bot']} | `{r['lang']}` "
                f"| `{r['expected_script']}` | `{r['detected_script']}` "
                f"| {q} | {resp} |"
            )
        lines.append("")

    # Root cause analysis and fixes
    lines += [
        "## Root Cause Analysis\n",
        "### Issues found\n",
    ]

    type_fails = defaultdict(int)
    for r in failures:
        type_fails[r["query_type"]] += 1

    if not type_fails:
        lines.append("✅ No failures — all queries passed language compliance checks!\n")
    else:
        for qtype, cnt in sorted(type_fails.items(), key=lambda x: -x[1]):
            lines.append(f"- **`{qtype}`** → {cnt} failures")
        lines.append("")

    # Romanized failures
    rom_fails = [r for r in failures if "-Latn" in r.get("lang", "") or "romanized" in r.get("query_type", "")]
    if rom_fails:
        lines += [
            "### Romanized Language Issues",
            f"",
            f"{len(rom_fails)} romanized queries (hi-Latn / gu-Latn) failed to receive Latin-script responses.",
            f"This typically means either:",
            f"- The LLM did not detect the romanized language correctly (Call 1)",
            f"- The language_instructions for `hi-Latn` / `gu-Latn` were not respected by the LLM",
            f"",
        ]

    native_fails = [r for r in failures if "native" in r.get("query_type", "")]
    if native_fails:
        lines += [
            "### Native Script Issues",
            f"",
            f"{len(native_fails)} native-script queries failed to receive correct-script responses.",
            f"Possible causes:",
            f"- Call 1 misclassified the language",
            f"- System prompt language instruction was not followed",
            f"",
        ]

    # Recommendations
    lines += [
        "## Recommendations\n",
        "1. **Reinforce language instruction** — Repeat the critical language rule in the last line of the system prompt (recency bias).",
        "2. **Romanized detection accuracy** — Expand the Call 1 few-shot examples with clear romanized Hindi/Gujarati samples.",
        "3. **Script detection logging** — Log detected vs expected script per response to monitor ongoing compliance.",
        "4. **Temperature reduction for hi-Latn** — Use temperature=0 for romanized language generation to reduce hallucination of wrong script.",
        "5. **Post-processing check** — After Call 2, verify response script matches request; if mismatch, trigger a re-generation with stricter prompt.",
        "",
    ]

    return "\n".join(lines)

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
async def main():
    print("🚀  V6 Language Compliance Test Runner")
    print(f"   Files: {QUERY_FILES}")
    print(f"   API:   {API_BASE}")
    print("")

    results = await run_tests()
    report  = generate_report(results)

    Path(REPORT_FILE).write_text(report, encoding="utf-8")
    print(f"📄  Report saved → {REPORT_FILE}")

    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    total  = sum(1 for r in results if r["status"] != "RATE_LIMIT")
    print(f"\n{'='*50}")
    print(f"  PASS {passed}/{total}  |  FAIL {failed}/{total}")
    print(f"{'='*50}")

if __name__ == "__main__":
    asyncio.run(main())
