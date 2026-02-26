#!/usr/bin/env python3
"""
Test: Missing Info + Regression (English Only)
================================================
1. Missing info queries (EN only) — tests the 4 fixes (A/B/C/D)
2. Regression queries — irrelevant, greeting, normal product
"""

import httpx
import json
import time
import uuid
import subprocess
import sys
import io
from datetime import datetime

# Fix Windows console encoding for emoji
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE = "http://localhost:8000/api/v1"
AUTH = {"email": "max@gmail.com", "password": "12345678"}

# Load missing_info queries (EN only)
with open("missing_info_queries.json", "r", encoding="utf-8") as f:
    ALL_TEST_DATA = json.load(f)

MISSING_INFO_CASES = []
for bot_key, bot_data in ALL_TEST_DATA.items():
    bot_id = bot_data["bot_id"]
    for i, tq in enumerate(bot_data["test_queries"]):
        if tq["lang"] == "en":
            MISSING_INFO_CASES.append({
                "bot_key": bot_key,
                "bot_id": bot_id,
                "lang": "en",
                "query": tq["query"],
                "expected_behavior": tq["expected_behavior"],
                "why_missing": tq["why_missing"],
                "case_num": i + 1,
                "test_type": "missing_info",
            })

# Regression test queries — 2-3 per type across different bots
REGRESSION_CASES = [
    # Irrelevant queries — must be REJECTED
    {
        "bot_key": "tentree",
        "bot_id": "799637f9-391b-4b9d-84cb-5fdd17cdf109",
        "lang": "en",
        "query": "Who is the president of the United States?",
        "expected_behavior": "Should be rejected as irrelevant with [[IRRELEVANT]]",
        "test_type": "irrelevant",
        "expected_status": "is_irrelevant",
    },
    {
        "bot_key": "deathwish",
        "bot_id": "99fc3604-99e7-4cd0-a2a6-509ac08d9fd0",
        "lang": "en",
        "query": "Write a Python script to sort a list",
        "expected_behavior": "Should be rejected as irrelevant with [[IRRELEVANT]]",
        "test_type": "irrelevant",
        "expected_status": "is_irrelevant",
    },
    {
        "bot_key": "beardbrand",
        "bot_id": "e23fcc6f-7a02-4b09-8d49-95c00a57d852",
        "lang": "en",
        "query": "What is the capital of France?",
        "expected_behavior": "Should be rejected as irrelevant with [[IRRELEVANT]]",
        "test_type": "irrelevant",
        "expected_status": "is_irrelevant",
    },
    # Greeting queries — must respond warmly, NOT missing_info
    {
        "bot_key": "ramraj",
        "bot_id": "182f88cd-02d8-4c94-824d-b41432847400",
        "lang": "en",
        "query": "Hello! How are you?",
        "expected_behavior": "Should respond with a warm greeting, NOT mark as missing_info",
        "test_type": "greeting",
        "expected_status": "was_answered",
    },
    {
        "bot_key": "kriyanta",
        "bot_id": "1cb18dc0-4909-409d-ab03-0436524fcec4",
        "lang": "en",
        "query": "Hi there",
        "expected_behavior": "Should respond with a warm greeting, NOT mark as missing_info",
        "test_type": "greeting",
        "expected_status": "was_answered",
    },
    # Normal product queries — must answer from context, NOT missing_info
    {
        "bot_key": "tentree",
        "bot_id": "799637f9-391b-4b9d-84cb-5fdd17cdf109",
        "lang": "en",
        "query": "Show me your best selling t-shirts",
        "expected_behavior": "Should show products from context, NOT mark as missing_info",
        "test_type": "product",
        "expected_status": "was_answered",
    },
    {
        "bot_key": "deathwish",
        "bot_id": "99fc3604-99e7-4cd0-a2a6-509ac08d9fd0",
        "lang": "en",
        "query": "What coffee blends do you have?",
        "expected_behavior": "Should list coffee products, NOT mark as missing_info",
        "test_type": "product",
        "expected_status": "was_answered",
    },
    {
        "bot_key": "beardbrand",
        "bot_id": "e23fcc6f-7a02-4b09-8d49-95c00a57d852",
        "lang": "en",
        "query": "What beard oils do you sell?",
        "expected_behavior": "Should list beard oil products, NOT mark as missing_info",
        "test_type": "product",
        "expected_status": "was_answered",
    },
]


def get_auth_token():
    with httpx.Client() as c:
        r = c.post(f"{BASE}/auth/login", json=AUTH)
        return r.json()["access_token"]


def collect_stream(bot_id: str, message: str, token: str) -> dict:
    """Send a streaming chat message and collect full response from SSE."""
    session_id = str(uuid.uuid4())
    full_text = ""
    products = []
    suggestions = []
    error = None
    raw_chunks = []

    headers = {"Authorization": f"Bearer {token}"} if token else {}

    try:
        with httpx.Client(timeout=httpx.Timeout(120.0, read=120.0)) as client:
            with client.stream(
                "POST",
                f"{BASE}/chat/{bot_id}/message/stream",
                headers=headers,
                data={"message": message, "session_id": session_id},
            ) as resp:
                if resp.status_code != 200:
                    return {
                        "text": "",
                        "products": [],
                        "suggestions": [],
                        "error": f"HTTP {resp.status_code}",
                        "raw_chunks": [],
                    }
                for line in resp.iter_lines():
                    line = line.strip()
                    if not line or not line.startswith("data: "):
                        continue
                    raw = line[6:]
                    if raw == "[DONE]":
                        break
                    try:
                        chunk = json.loads(raw)
                        raw_chunks.append(chunk)
                        t = chunk.get("type", "")
                        if t == "content":
                            full_text += chunk.get("content", "")
                        elif t == "done":
                            products = chunk.get("products", [])
                            suggestions = chunk.get("suggestions", [])
                    except json.JSONDecodeError:
                        pass
    except BaseException as e:
        error = f"{type(e).__name__}: {e}"

    return {
        "text": full_text.strip(),
        "products": products,
        "suggestions": suggestions,
        "error": error,
        "raw_chunks": raw_chunks,
    }


def query_db_metadata(session_id: str) -> dict:
    """Query the DB for the last assistant message's metadata in the given session."""
    sql = f"""
    SELECT cm.metadata_json
    FROM chat_messages cm
    JOIN chat_sessions cs ON cm.session_id = cs.id
    WHERE cs.id = '{session_id}'
      AND cm.role = 'assistant'
    ORDER BY cm.created_at DESC
    LIMIT 1;
    """
    try:
        result = subprocess.run(
            ["docker", "exec", "chatbot_postgres", "psql", "-U", "postgres",
             "-d", "embed_chatbot", "-t", "-A", "-c", sql],
            capture_output=True, text=True, timeout=10
        )
        raw = result.stdout.strip()
        if raw:
            return json.loads(raw)
    except Exception as e:
        print(f"    DB query error: {e}")
    return {}


def run_test(test_case, token, test_num, total):
    """Run a single test case and return result dict."""
    tc = test_case
    label = f"{tc['test_type'].upper()}:{tc['bot_key']}#{tc.get('case_num', 1)}"
    print(f"\n[{test_num}/{total}] {label}")
    print(f"  Q: {tc['query'][:80]}")

    r = collect_stream(tc["bot_id"], tc["query"], token)

    if r["error"]:
        print(f"  ERROR: {r['error']}")
        return {"label": label, "status": "ERROR", "error": r["error"], **tc}

    # Get session_id
    session_id = None
    for chunk in r["raw_chunks"]:
        if chunk.get("type") == "session":
            session_id = chunk.get("session_id")
            break

    # Wait for DB write
    time.sleep(1.5)
    meta = query_db_metadata(session_id) if session_id else {}

    is_missing_info = meta.get("is_missing_info", False)
    was_answered = meta.get("was_answered", True)
    is_irrelevant = meta.get("is_irrelevant", False)

    lower = r["text"].lower()
    is_rate_limited = any(p in lower for p in [
        "rate limit", "too many requests", "try again later",
        "getting a lot of requests", "currently experiencing",
    ])

    # Determine result based on test type
    if is_rate_limited:
        status = "RATE_LIMITED"
        icon = "⚠️"
    elif tc["test_type"] == "missing_info":
        helpful_patterns = [
            "contact", "reach out", "email", "call", "phone",
            "official website", "support", "customer service",
            "help centre", "help center", "check the",
            "support@", "customercare@",
        ]
        is_helpful = any(p in lower for p in helpful_patterns)

        if is_irrelevant:
            status = "FALSE_REJECTION"
            icon = "❌"
        elif is_missing_info and is_helpful:
            status = "PERFECT"
            icon = "✅"
        elif is_missing_info:
            status = "GOOD"
            icon = "👍"
        else:
            status = "NOT_DETECTED"
            icon = "🚨"
    elif tc["test_type"] == "irrelevant":
        if is_irrelevant:
            status = "PASS"
            icon = "✅"
        else:
            status = "FAIL_NOT_REJECTED"
            icon = "❌"
    elif tc["test_type"] == "greeting":
        if is_missing_info:
            status = "FAIL_FALSE_MISSING"
            icon = "❌"
        elif is_irrelevant:
            status = "FAIL_REJECTED"
            icon = "❌"
        else:
            status = "PASS"
            icon = "✅"
    elif tc["test_type"] == "product":
        if is_missing_info:
            status = "FAIL_FALSE_MISSING"
            icon = "❌"
        elif is_irrelevant:
            status = "FAIL_REJECTED"
            icon = "❌"
        else:
            status = "PASS"
            icon = "✅"
    else:
        status = "UNKNOWN"
        icon = "?"

    print(f"  A: {r['text'][:120]}...")
    print(f"  {icon} {status} | DB: missing={is_missing_info}, answered={was_answered}, irrelevant={is_irrelevant}")
    if r["products"]:
        print(f"    Products: {len(r['products'])}")

    return {
        "label": label,
        "bot": tc["bot_key"],
        "query": tc["query"],
        "response": r["text"][:500],
        "status": status,
        "test_type": tc["test_type"],
        "is_missing_info_db": is_missing_info,
        "was_answered_db": was_answered,
        "is_irrelevant_db": is_irrelevant,
        "expected": tc["expected_behavior"],
        "products_count": len(r["products"]),
        "error": None,
    }


def main():
    print("=" * 70)
    print("MISSING INFO + REGRESSION TEST (English Only)")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    all_cases = MISSING_INFO_CASES + REGRESSION_CASES
    print(f"Missing info queries (EN): {len(MISSING_INFO_CASES)}")
    print(f"Regression queries: {len(REGRESSION_CASES)}")
    print(f"Total: {len(all_cases)}")
    print("=" * 70)

    token = get_auth_token()
    print(f"Auth: OK")

    results = []
    for i, tc in enumerate(all_cases):
        result = run_test(tc, token, i + 1, len(all_cases))
        results.append(result)
        time.sleep(5)

    # Compute stats
    mi_results = [r for r in results if r["test_type"] == "missing_info" and r["status"] not in ("ERROR", "RATE_LIMITED")]
    irr_results = [r for r in results if r["test_type"] == "irrelevant" and r["status"] not in ("ERROR", "RATE_LIMITED")]
    greet_results = [r for r in results if r["test_type"] == "greeting" and r["status"] not in ("ERROR", "RATE_LIMITED")]
    prod_results = [r for r in results if r["test_type"] == "product" and r["status"] not in ("ERROR", "RATE_LIMITED")]

    mi_perfect = sum(1 for r in mi_results if r["status"] == "PERFECT")
    mi_good = sum(1 for r in mi_results if r["status"] == "GOOD")
    mi_detected = mi_perfect + mi_good
    mi_not = sum(1 for r in mi_results if r["status"] == "NOT_DETECTED")
    mi_false_rej = sum(1 for r in mi_results if r["status"] == "FALSE_REJECTION")

    irr_pass = sum(1 for r in irr_results if r["status"] == "PASS")
    greet_pass = sum(1 for r in greet_results if r["status"] == "PASS")
    prod_pass = sum(1 for r in prod_results if r["status"] == "PASS")

    rate_limited = sum(1 for r in results if r.get("status") == "RATE_LIMITED")
    errors = sum(1 for r in results if r.get("status") == "ERROR")

    print(f"\n\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")

    print(f"\n--- MISSING INFO (EN) ---")
    print(f"Valid: {len(mi_results)}")
    if mi_results:
        print(f"✅ PERFECT: {mi_perfect}/{len(mi_results)} ({mi_perfect/len(mi_results):.0%})")
        print(f"👍 GOOD:    {mi_good}/{len(mi_results)} ({mi_good/len(mi_results):.0%})")
        print(f"🚨 NOT_DETECTED: {mi_not}/{len(mi_results)} ({mi_not/len(mi_results):.0%})")
        print(f"❌ FALSE_REJECTION: {mi_false_rej}/{len(mi_results)}")
        print(f"Detection rate (PERFECT+GOOD): {mi_detected}/{len(mi_results)} ({mi_detected/len(mi_results):.0%})")

    print(f"\n--- REGRESSION: IRRELEVANT ---")
    print(f"✅ Correctly rejected: {irr_pass}/{len(irr_results)}")

    print(f"\n--- REGRESSION: GREETING ---")
    print(f"✅ Correctly answered: {greet_pass}/{len(greet_results)}")

    print(f"\n--- REGRESSION: PRODUCT ---")
    print(f"✅ Correctly answered: {prod_pass}/{len(prod_results)}")

    print(f"\n--- OTHER ---")
    print(f"⚠️ Rate limited: {rate_limited}")
    print(f"💥 Errors: {errors}")

    # Save raw data
    with open("missing_info_v2_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "results": results,
            "stats": {
                "missing_info": {"total": len(mi_results), "perfect": mi_perfect, "good": mi_good, "not_detected": mi_not, "false_rejection": mi_false_rej},
                "irrelevant": {"total": len(irr_results), "pass": irr_pass},
                "greeting": {"total": len(greet_results), "pass": greet_pass},
                "product": {"total": len(prod_results), "pass": prod_pass},
                "rate_limited": rate_limited,
                "errors": errors,
            },
        }, f, indent=2, ensure_ascii=False)

    # Generate report
    generate_report(results, mi_results, irr_results, greet_results, prod_results,
                    mi_perfect, mi_good, mi_not, mi_false_rej,
                    irr_pass, greet_pass, prod_pass, rate_limited, errors)
    print(f"\n📄 Report: MISSING_INFO_V2_REPORT.md")


def generate_report(results, mi_results, irr_results, greet_results, prod_results,
                    mi_perfect, mi_good, mi_not, mi_false_rej,
                    irr_pass, greet_pass, prod_pass, rate_limited, errors):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mi_detected = mi_perfect + mi_good

    md = [
        "# Missing Info V2 Test Report (Post-Fix)",
        f"\n**Date:** {ts}",
        f"\n**Fixes applied:** Fix A (products guard), Fix B (contact verify), Fix C (server-side detect + prompt), Fix D (product count injection)",
        "\n## Summary\n",
        "### Missing Info Detection (EN only)\n",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Valid queries | {len(mi_results)} |",
        f"| ✅ PERFECT (detected + helpful) | {mi_perfect}/{len(mi_results)} ({mi_perfect/len(mi_results):.0%} if mi_results else 'n/a') |" if mi_results else "| ✅ PERFECT | n/a |",
        f"| 👍 GOOD (detected) | {mi_good}/{len(mi_results)} |" if mi_results else "",
        f"| 🚨 NOT DETECTED | {mi_not}/{len(mi_results)} |" if mi_results else "",
        f"| ❌ FALSE REJECTION | {mi_false_rej}/{len(mi_results)} |" if mi_results else "",
        f"| **Detection rate** | **{mi_detected}/{len(mi_results)} ({mi_detected/len(mi_results):.0%})**|" if mi_results else "",
        "\n### Regression Tests\n",
        "| Test Type | Result |",
        "|-----------|--------|",
        f"| Irrelevant rejection | {irr_pass}/{len(irr_results)} ({'✅' if irr_pass == len(irr_results) else '❌'}) |",
        f"| Greeting response | {greet_pass}/{len(greet_results)} ({'✅' if greet_pass == len(greet_results) else '❌'}) |",
        f"| Product query answer | {prod_pass}/{len(prod_results)} ({'✅' if prod_pass == len(prod_results) else '❌'}) |",
        f"| Rate limited | {rate_limited} |",
        f"| Errors | {errors} |",
    ]

    # Detailed results
    md.append("\n## Detailed Results\n")

    for test_type, label in [("missing_info", "Missing Info"), ("irrelevant", "Irrelevant"), ("greeting", "Greeting"), ("product", "Product")]:
        type_results = [r for r in results if r["test_type"] == test_type]
        if not type_results:
            continue
        md.append(f"\n### {label} Queries\n")
        for r in type_results:
            icon = {"PERFECT": "✅", "GOOD": "👍", "NOT_DETECTED": "🚨", "PASS": "✅",
                    "FAIL_NOT_REJECTED": "❌", "FAIL_FALSE_MISSING": "❌", "FAIL_REJECTED": "❌",
                    "FALSE_REJECTION": "❌", "RATE_LIMITED": "⚠️", "ERROR": "💥"}.get(r["status"], "?")
            md.append(f"**{r['label']}** | {icon} {r['status']}")
            md.append(f"> **Q:** {r['query']}")
            if r.get("error"):
                md.append(f"- Error: {r['error']}")
            else:
                md.append(f"- **A:** {r.get('response', '')[:300]}...")
                md.append(f"- DB: missing_info={r.get('is_missing_info_db')}, answered={r.get('was_answered_db')}, irrelevant={r.get('is_irrelevant_db')}")
                if r.get("products_count"):
                    md.append(f"- Products: {r['products_count']}")
            md.append(f"- Expected: {r['expected']}")
            md.append("")

    with open("MISSING_INFO_V2_REPORT.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md))


if __name__ == "__main__":
    main()
