#!/usr/bin/env python3
"""
V5 Comprehensive Chatbot Test Runner
=====================================
Sends test queries from v5_queries_*.json files to the chatbot API endpoint
via SSE streaming.  Stops when ALL provider keys (4 OpenRouter + 6 Groq) are
rate-limited (detected by consecutive rate-limit responses).

Results are saved to v5_test_results.json and a markdown report is generated.
"""

import json, time, uuid, sys, os, re, httpx, asyncio
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
API_BASE = "http://localhost:8000/api/v1"
QUERY_FILES = [
    "v5_queries_tentree.json",
    "v5_queries_zevaramaze.json",
    "v5_queries_kriyanta.json",
]
RESULTS_FILE = "v5_test_results.json"
REPORT_FILE  = "V5_TEST_REPORT.md"

# Rate-limit detection
RATE_LIMIT_PHRASES = [
    "a lot of requests",
    "try again in a few minutes",
    "rate limit",
    "too many requests",
    "429",
    "can't respond right now",
]
# After this many *consecutive* rate-limit responses (across ALL bots), we stop
CONSECUTIVE_RL_THRESHOLD = 8
# Delay between requests (seconds) — keeps us under 30 req/min/bot comfortably
INTER_REQUEST_DELAY = 2.5

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def is_rate_limit_response(text: str) -> bool:
    lowered = text.lower()
    return any(p in lowered for p in RATE_LIMIT_PHRASES)


def parse_sse_response(raw_text: str):
    """Parse SSE stream into aggregated content, done payload, and error flag."""
    content_parts = []
    done_payload = {}
    session_id = None
    has_error = False

    for line in raw_text.split("\n"):
        line = line.strip()
        if not line.startswith("data: "):
            continue
        try:
            chunk = json.loads(line[6:])
        except json.JSONDecodeError:
            continue

        ctype = chunk.get("type", "")
        if ctype == "session":
            session_id = chunk.get("session_id")
        elif ctype == "content":
            content_parts.append(chunk.get("content", ""))
        elif ctype == "done":
            done_payload = chunk
            if chunk.get("error"):
                has_error = True
        elif ctype == "error":
            has_error = True
            content_parts.append(chunk.get("error", ""))

    full_content = "".join(content_parts)
    return {
        "content": full_content,
        "session_id": session_id,
        "sources": done_payload.get("sources", []),
        "products": done_payload.get("products", []),
        "suggestions": done_payload.get("suggestions", []),
        "has_error": has_error,
        "is_rate_limited": is_rate_limit_response(full_content) or has_error,
    }


async def send_query(client: httpx.AsyncClient, bot_id: str, message: str,
                     session_id: str | None = None, timeout: float = 60) -> dict:
    """Send a single query to the chat streaming endpoint and collect full response."""
    url = f"{API_BASE}/chat/{bot_id}/message/stream"
    form_data = {"message": message, "is_preview": "false"}
    if session_id:
        form_data["session_id"] = session_id

    start = time.time()
    try:
        resp = await client.post(url, data=form_data, timeout=timeout)
        elapsed = round(time.time() - start, 2)

        if resp.status_code == 429:
            return {
                "content": "",
                "session_id": session_id,
                "sources": [],
                "products": [],
                "suggestions": [],
                "has_error": True,
                "is_rate_limited": True,
                "http_status": 429,
                "elapsed_s": elapsed,
            }

        parsed = parse_sse_response(resp.text)
        parsed["http_status"] = resp.status_code
        parsed["elapsed_s"] = elapsed
        return parsed

    except Exception as exc:
        elapsed = round(time.time() - start, 2)
        return {
            "content": str(exc),
            "session_id": session_id,
            "sources": [],
            "products": [],
            "suggestions": [],
            "has_error": True,
            "is_rate_limited": "timeout" not in str(exc).lower(),
            "http_status": 0,
            "elapsed_s": elapsed,
        }


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

async def main():
    print("=" * 70)
    print("  V5 Chatbot Test Runner")
    print("=" * 70)

    # Load all query files
    all_bots = []
    for qf in QUERY_FILES:
        path = Path(qf)
        if not path.exists():
            print(f"  [SKIP] {qf} not found")
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        all_bots.append(data)
        print(f"  Loaded {len(data['queries'])} queries for {data['bot']}")

    if not all_bots:
        print("No query files found. Exiting.")
        return

    total_queries = sum(len(b["queries"]) for b in all_bots)
    print(f"\n  Total queries to run: {total_queries}")
    print(f"  Rate-limit stop threshold: {CONSECUTIVE_RL_THRESHOLD} consecutive RL responses")
    print(f"  Inter-request delay: {INTER_REQUEST_DELAY}s")
    print()

    # Interleave queries across bots (round-robin)
    interleaved = []
    max_len = max(len(b["queries"]) for b in all_bots)
    for i in range(max_len):
        for bot_data in all_bots:
            if i < len(bot_data["queries"]):
                q = bot_data["queries"][i]
                interleaved.append({
                    "bot": bot_data["bot"],
                    "bot_id": bot_data["bot_id"],
                    "allowed_languages": bot_data["allowed_languages"],
                    "query_type": q["type"],
                    "query_lang": q["lang"],
                    "query_text": q["query"],
                })

    # Session tracking per bot for multi-turn context
    bot_sessions: dict[str, str | None] = {b["bot_id"]: None for b in all_bots}
    # Track which queries need session continuation
    continuation_types = {"continuation", "multi_turn_summary"}

    results = []
    consecutive_rl = 0
    completed = 0
    rate_limited_count = 0
    start_time = time.time()

    async with httpx.AsyncClient() as client:
        for idx, item in enumerate(interleaved, 1):
            bot_id = item["bot_id"]
            query_text = item["query_text"]
            query_type = item["query_type"]
            bot_name = item["bot"]

            # Use session for continuation-like queries
            session_id = None
            if query_type in continuation_types and bot_sessions[bot_id]:
                session_id = bot_sessions[bot_id]

            print(f"  [{idx}/{len(interleaved)}] {bot_name} | {query_type} | {item['query_lang']} | {query_text[:50]}...", end=" ", flush=True)

            resp = await send_query(client, bot_id, query_text, session_id=session_id)

            # Update session if we got one
            if resp.get("session_id"):
                bot_sessions[bot_id] = resp["session_id"]

            # Check rate limit
            if resp["is_rate_limited"]:
                consecutive_rl += 1
                rate_limited_count += 1
                print(f"⚠ RL ({consecutive_rl}/{CONSECUTIVE_RL_THRESHOLD}) [{resp['elapsed_s']}s]")
            else:
                consecutive_rl = 0
                content_preview = resp["content"][:80].replace("\n", " ")
                n_products = len(resp.get("products", []))
                print(f"✓ [{resp['elapsed_s']}s] {n_products}P | {content_preview}...")

            # Store result
            result_entry = {
                "index": idx,
                "bot": bot_name,
                "bot_id": bot_id,
                "allowed_languages": item["allowed_languages"],
                "query_type": query_type,
                "query_lang": item["query_lang"],
                "query": query_text,
                "response": resp["content"],
                "sources": resp.get("sources", []),
                "products": resp.get("products", []),
                "suggestions": resp.get("suggestions", []),
                "session_id": resp.get("session_id"),
                "http_status": resp.get("http_status"),
                "elapsed_s": resp.get("elapsed_s"),
                "is_rate_limited": resp["is_rate_limited"],
                "has_error": resp["has_error"],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            results.append(result_entry)
            completed += 1

            # Stop if too many consecutive rate limits
            if consecutive_rl >= CONSECUTIVE_RL_THRESHOLD:
                print(f"\n  ⛔ {CONSECUTIVE_RL_THRESHOLD} consecutive rate-limit responses detected.")
                print("  All API keys likely exhausted. Stopping tests.")
                break

            # Delay
            await asyncio.sleep(INTER_REQUEST_DELAY)

    elapsed_total = round(time.time() - start_time, 1)
    successful = [r for r in results if not r["is_rate_limited"]]

    print(f"\n{'=' * 70}")
    print(f"  Test Complete!")
    print(f"  Total attempted: {completed} / {len(interleaved)}")
    print(f"  Successful: {len(successful)}")
    print(f"  Rate-limited: {rate_limited_count}")
    print(f"  Total time: {elapsed_total}s")
    print(f"{'=' * 70}")

    # Save raw results
    output = {
        "test_run": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_attempted": completed,
            "total_successful": len(successful),
            "total_rate_limited": rate_limited_count,
            "elapsed_seconds": elapsed_total,
        },
        "results": results,
    }
    Path(RESULTS_FILE).write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n  Results saved to {RESULTS_FILE}")

    # Generate report
    generate_report(output)
    print(f"  Report saved to {REPORT_FILE}")


# ---------------------------------------------------------------------------
# Report generator
# ---------------------------------------------------------------------------

def generate_report(data: dict):
    """Analyze results and generate a markdown report with fixes/weakpoints."""
    results = data["results"]
    meta = data["test_run"]

    # Filter to successful (non rate-limited) results only for analysis
    success = [r for r in results if not r["is_rate_limited"]]

    if not success:
        Path(REPORT_FILE).write_text(
            "# V5 Test Report\n\nNo successful responses collected (all rate-limited).\n",
            encoding="utf-8",
        )
        return

    # ---- Per-bot stats ----
    bots = sorted(set(r["bot"] for r in success))
    bot_results = {b: [r for r in success if r["bot"] == b] for b in bots}

    # ---- Scoring functions ----
    def score_response(r: dict) -> dict:
        """Score a single response on multiple dimensions."""
        resp = r["response"].strip()
        qtype = r["query_type"]
        qlang = r["query_lang"]
        allowed = r["allowed_languages"]
        products = r.get("products", [])
        sources = r.get("sources", [])

        scores = {}

        # 1. Relevance — did it answer at all? (non-empty, non-error)
        scores["has_response"] = len(resp) > 10

        # 2. Language compliance
        base_lang = qlang.split("-")[0]
        # Check if response has some script-appropriate characters
        if base_lang == "hi":
            # Hindi Devanagari range or romanized Hindi
            has_lang = bool(re.search(r'[\u0900-\u097F]', resp)) or qlang.endswith("-Latn")
        elif base_lang == "gu":
            has_lang = bool(re.search(r'[\u0A80-\u0AFF]', resp)) or qlang.endswith("-Latn")
        elif base_lang == "en":
            has_lang = bool(re.search(r'[a-zA-Z]', resp))
        else:
            has_lang = True  # can't check
        scores["language_ok"] = has_lang

        # 3. Blocked language test (should NOT respond in disallowed lang)
        if qtype.startswith("blocked_lang"):
            # Extract the blocked lang from the type (e.g., "blocked_lang_en" -> "en")
            blocked_lang = qtype.replace("blocked_lang_", "")
            # Bot should refuse or redirect, not answer substantively
            refusal_phrases = ["sorry", "apologize", "cannot", "can't", "don't support",
                             "not support", "available in", "please use", "supported language",
                             "माफ", "क्षमा", "માફ", "supported", "i can only"]
            scores["blocked_handled"] = any(p in resp.lower() for p in refusal_phrases) or len(resp) < 100
        else:
            scores["blocked_handled"] = None  # not applicable

        # 4. Product returned when expected
        product_types = {"product_browse", "product_specific", "product_comparison",
                        "price_query", "category_browse"}
        if qtype in product_types:
            scores["has_products"] = len(products) > 0
        else:
            scores["has_products"] = None

        # 5. Greeting response quality
        if qtype == "greeting":
            greeting_words = ["hello", "hi", "welcome", "help", "assist",
                            "नमस्ते", "स्वागत", "नमस्કાર", "સ્વાગત",
                            "namaste", "kem chho", "kaise"]
            scores["greeting_ok"] = any(w in resp.lower() for w in greeting_words) or len(resp) > 20
        else:
            scores["greeting_ok"] = None

        # 6. Irrelevant query handling
        if qtype == "irrelevant_intelligent":
            # Should acknowledge but redirect to products/store
            redirect_signs = ["sorry", "can't help", "cannot help", "not related",
                            "can help you with", "product", "store", "shop",
                            "assist you with", "माफ", "मदद", "માફ", "મદદ",
                            "madad", "shopping", "catalog"]
            scores["irrelevant_handled"] = any(s in resp.lower() for s in redirect_signs)
        else:
            scores["irrelevant_handled"] = None

        # 7. Missing info handling (should NOT hallucinate)
        if qtype.startswith("missing_info"):
            # Bot should admit it doesn't have this info
            honesty_phrases = ["sorry", "don't have", "cannot", "can't", "not available",
                             "unable to", "no information", "don't know", "not able",
                             "i cannot track", "cannot process", "not something i can",
                             "माफ", "नहीं", "जानकारी नहीं", "માફ", "નથી",
                             "unavailable", "beyond", "outside", "don't offer"]
            scores["missing_info_honest"] = any(p in resp.lower() for p in honesty_phrases)
            # Check for potential hallucination (making up specific data)
            hallucination_signs = ["order #", "tracking number", "shipped on",
                                  "delivered on", "your order", "policy states",
                                  "our policy is", "warranty covers", "emi available"]
            scores["no_hallucination"] = not any(h in resp.lower() for h in hallucination_signs)
        else:
            scores["missing_info_honest"] = None
            scores["no_hallucination"] = None

        # 8. Edge case handling
        if qtype == "edge_case":
            scores["edge_handled"] = len(resp) > 10 and not r["has_error"]
        else:
            scores["edge_handled"] = None

        # 9. Response time
        scores["fast_response"] = r.get("elapsed_s", 999) < 15

        # 10. Sources provided for product queries
        if qtype in product_types:
            scores["has_sources"] = len(sources) > 0
        else:
            scores["has_sources"] = None

        return scores

    # Score all successful responses
    scored_results = []
    for r in success:
        s = score_response(r)
        scored_results.append({**r, "scores": s})

    # ---- Aggregate stats ----
    def pct(count, total):
        return f"{round(100 * count / total)}%" if total > 0 else "N/A"

    def count_true(items, key):
        applicable = [i for i in items if i["scores"].get(key) is not None]
        yes = sum(1 for i in applicable if i["scores"][key])
        return yes, len(applicable)

    # Per-bot breakdown
    bot_analyses = {}
    for bot_name in bots:
        items = [r for r in scored_results if r["bot"] == bot_name]
        analysis = {
            "total": len(items),
            "has_response": count_true(items, "has_response"),
            "language_ok": count_true(items, "language_ok"),
            "has_products": count_true(items, "has_products"),
            "greeting_ok": count_true(items, "greeting_ok"),
            "blocked_handled": count_true(items, "blocked_handled"),
            "irrelevant_handled": count_true(items, "irrelevant_handled"),
            "missing_info_honest": count_true(items, "missing_info_honest"),
            "no_hallucination": count_true(items, "no_hallucination"),
            "edge_handled": count_true(items, "edge_handled"),
            "fast_response": count_true(items, "fast_response"),
            "has_sources": count_true(items, "has_sources"),
            "avg_time": round(sum(i["elapsed_s"] for i in items) / len(items), 1) if items else 0,
        }
        bot_analyses[bot_name] = analysis

    # Per-type breakdown
    types = sorted(set(r["query_type"] for r in scored_results))
    type_analyses = {}
    for qtype in types:
        items = [r for r in scored_results if r["query_type"] == qtype]
        type_analyses[qtype] = {
            "total": len(items),
            "has_response": count_true(items, "has_response"),
            "avg_time": round(sum(i["elapsed_s"] for i in items) / len(items), 1) if items else 0,
        }

    # ---- Identify weakpoints & fixes ----
    weakpoints = []
    fixes = []

    for bot_name, a in bot_analyses.items():
        # Language compliance issues
        yes, total = a["language_ok"]
        if total > 0 and yes < total:
            fail_items = [r for r in scored_results if r["bot"] == bot_name and not r["scores"].get("language_ok", True)]
            weakpoints.append(f"**{bot_name}**: Language compliance {pct(yes, total)} ({total - yes}/{total} failed) — bot sometimes responds in wrong language/script")
            for fi in fail_items[:3]:
                weakpoints.append(f"  - Query ({fi['query_lang']}): \"{fi['query'][:60]}\" → Response snippet: \"{fi['response'][:80]}...\"")
            bot_langs = next((x["allowed_languages"] for x in results if x["bot"] == bot_name), [])
            fixes.append(f"[{bot_name}] Strengthen language detection in Call1 prompt — enforce script matching for {', '.join(bot_langs)} languages")

        # Product retrieval issues
        yes, total = a["has_products"]
        if total > 0 and yes < total:
            fail_items = [r for r in scored_results if r["bot"] == bot_name and r["scores"].get("has_products") == False]
            weakpoints.append(f"**{bot_name}**: Product retrieval {pct(yes, total)} ({total - yes}/{total} queries returned no products)")
            for fi in fail_items[:3]:
                weakpoints.append(f"  - Query: \"{fi['query'][:60]}\" → No products returned")
            fixes.append(f"[{bot_name}] Improve embedding search to handle non-English product queries — transliterate queries before vector search")

        # Blocked language handling
        yes, total = a["blocked_handled"]
        if total > 0 and yes < total:
            fail_items = [r for r in scored_results if r["bot"] == bot_name and r["scores"].get("blocked_handled") == False]
            weakpoints.append(f"**{bot_name}**: Blocked language rejection {pct(yes, total)} — bot answers in disallowed languages instead of refusing")
            for fi in fail_items[:3]:
                weakpoints.append(f"  - Query ({fi['query_lang']}): \"{fi['query'][:60]}\" → \"{fi['response'][:80]}...\"")
            fixes.append(f"[{bot_name}] Add stricter language gate in system prompt — refuse with redirect when query language is not in allowed list")

        # Irrelevant query handling
        yes, total = a["irrelevant_handled"]
        if total > 0 and yes < total:
            fail_items = [r for r in scored_results if r["bot"] == bot_name and r["scores"].get("irrelevant_handled") == False]
            weakpoints.append(f"**{bot_name}**: Irrelevant query deflection {pct(yes, total)} — bot engages with off-topic queries instead of redirecting")
            for fi in fail_items[:3]:
                weakpoints.append(f"  - Query: \"{fi['query'][:60]}\" → \"{fi['response'][:80]}...\"")
            fixes.append(f"[{bot_name}] Tighten Call1 is_product=false handling — always redirect off-topic queries to store catalog")

        # Missing info honesty
        yes, total = a["missing_info_honest"]
        if total > 0 and yes < total:
            fail_items = [r for r in scored_results if r["bot"] == bot_name and r["scores"].get("missing_info_honest") == False]
            weakpoints.append(f"**{bot_name}**: Missing info honesty {pct(yes, total)} — bot may fabricate answers for info it doesn't have")
            for fi in fail_items[:3]:
                weakpoints.append(f"  - Query: \"{fi['query'][:60]}\" → \"{fi['response'][:100]}...\"")
            fixes.append(f"[{bot_name}] Add explicit guardrail: if no matching embeddings found for order/policy/out-of-catalog queries, respond with 'I don't have that information'")

        # Hallucination
        yes, total = a["no_hallucination"]
        if total > 0 and yes < total:
            fail_items = [r for r in scored_results if r["bot"] == bot_name and r["scores"].get("no_hallucination") == False]
            weakpoints.append(f"**{bot_name}**: Hallucination detected {total - yes}/{total} — bot invents specific data (order numbers, policies)")
            for fi in fail_items[:3]:
                weakpoints.append(f"  - Query: \"{fi['query'][:60]}\" → \"{fi['response'][:100]}...\"")
            fixes.append(f"[{bot_name}] CRITICAL: Add hallucination guard — when retrieval returns no context, bot must NOT invent policy details, order statuses, or product specs")

        # Slow responses
        yes, total = a["fast_response"]
        if total > 0 and yes < total:
            slow_items = [r for r in scored_results if r["bot"] == bot_name and not r["scores"].get("fast_response", True)]
            avg_slow = round(sum(s["elapsed_s"] for s in slow_items) / len(slow_items), 1) if slow_items else 0
            weakpoints.append(f"**{bot_name}**: {total - yes}/{total} responses slower than 15s (avg slow: {avg_slow}s)")
            fixes.append(f"[{bot_name}] Optimize Call1+Call2 pipeline — consider caching common query patterns or reducing max_tokens")

        # Greeting quality
        yes, total = a["greeting_ok"]
        if total > 0 and yes < total:
            weakpoints.append(f"**{bot_name}**: Greeting response quality {pct(yes, total)}")
            fixes.append(f"[{bot_name}] Review welcome message and greeting system prompt")

    # ---- Build report ----
    lines = []
    lines.append("# V5 Chatbot Test Report")
    lines.append(f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"\n## Test Summary\n")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total Attempted | {meta['total_attempted']} |")
    lines.append(f"| Successful | {meta['total_successful']} |")
    lines.append(f"| Rate-Limited | {meta['total_rate_limited']} |")
    lines.append(f"| Duration | {meta['elapsed_seconds']}s |")

    lines.append(f"\n## Per-Bot Results\n")
    for bot_name, a in bot_analyses.items():
        lines.append(f"### {bot_name}\n")
        lines.append(f"| Dimension | Pass | Total | Rate |")
        lines.append(f"|-----------|------|-------|------|")

        dims = [
            ("Response Received", "has_response"),
            ("Language Compliance", "language_ok"),
            ("Product Retrieval", "has_products"),
            ("Greeting Quality", "greeting_ok"),
            ("Blocked Lang Handled", "blocked_handled"),
            ("Irrelevant Deflection", "irrelevant_handled"),
            ("Missing Info Honesty", "missing_info_honest"),
            ("No Hallucination", "no_hallucination"),
            ("Edge Case Handled", "edge_handled"),
            ("Fast Response (<15s)", "fast_response"),
            ("Sources Provided", "has_sources"),
        ]
        for label, key in dims:
            yes, total = a[key]
            if total > 0:
                lines.append(f"| {label} | {yes} | {total} | {pct(yes, total)} |")

        lines.append(f"| **Avg Response Time** | | | **{a['avg_time']}s** |")
        lines.append("")

    lines.append(f"\n## Per Query-Type Results\n")
    lines.append(f"| Type | Count | Avg Time |")
    lines.append(f"|------|-------|----------|")
    for qtype, a in type_analyses.items():
        yes, total = a["has_response"]
        lines.append(f"| {qtype} | {total} ({pct(yes, total)} ok) | {a['avg_time']}s |")

    lines.append(f"\n## Weakpoints & Issues\n")
    if weakpoints:
        for w in weakpoints:
            lines.append(f"- {w}")
    else:
        lines.append("No significant weakpoints detected! 🎉")

    lines.append(f"\n## Recommended Fixes\n")
    if fixes:
        for i, f in enumerate(fixes, 1):
            lines.append(f"{i}. {f}")
    else:
        lines.append("No fixes needed.")

    # ---- Sample responses for each type ----
    lines.append(f"\n## Sample Responses (by type)\n")
    for qtype in types:
        items = [r for r in scored_results if r["query_type"] == qtype]
        if not items:
            continue
        sample = items[0]
        lines.append(f"### {qtype}\n")
        lines.append(f"**Query** ({sample['query_lang']}): {sample['query']}\n")
        resp_preview = sample['response'][:300].replace("\n", " \\n ")
        lines.append(f"**Response**: {resp_preview}\n")
        n_products = len(sample.get("products", []))
        n_sources = len(sample.get("sources", []))
        lines.append(f"Products: {n_products} | Sources: {n_sources} | Time: {sample['elapsed_s']}s\n")

    # ---- Detailed failures ----
    lines.append(f"\n## Detailed Failures\n")
    failures = [r for r in scored_results if r["scores"] and (
        r["scores"].get("language_ok") == False or
        r["scores"].get("blocked_handled") == False or
        r["scores"].get("missing_info_honest") == False or
        r["scores"].get("no_hallucination") == False or
        r["scores"].get("has_products") == False or
        r["scores"].get("irrelevant_handled") == False
    )]
    if failures:
        for f in failures:
            failed_dims = [k for k, v in f["scores"].items() if v == False]
            lines.append(f"**[{f['bot']}]** `{f['query_type']}` ({f['query_lang']})")
            lines.append(f"- Query: {f['query']}")
            lines.append(f"- Failed: {', '.join(failed_dims)}")
            resp_snip = f['response'][:200].replace("\n", " ")
            lines.append(f"- Response: {resp_snip}")
            lines.append("")
    else:
        lines.append("No failures detected!")

    report_text = "\n".join(lines)
    Path(REPORT_FILE).write_text(report_text, encoding="utf-8")


if __name__ == "__main__":
    asyncio.run(main())
