#!/usr/bin/env python3
"""
Test: Missing Info Query Handling
==================================
Tests how the chatbot handles queries that are IN-SCOPE but request information
NOT present in the crawled data (e.g., return policy, size guide, warranty, etc.).

Expected behavior:
- Bot should NOT reject as irrelevant (queries are on-topic)
- Bot should honestly say the info is unavailable
- Bot should be helpful (suggest contacting support, provide related info)
- Response should contain [[MISSING_INFO]] marker (tracked internally)
- Response language should match query language
"""

import httpx
import json
import time
import uuid
import re
import subprocess
from datetime import datetime

BASE = "http://localhost:8000/api/v1"
AUTH = {"email": "max@gmail.com", "password": "12345678"}

# Load test queries from JSON
with open("missing_info_queries.json", "r", encoding="utf-8") as f:
    ALL_TEST_DATA = json.load(f)

# Build flat test list
TEST_CASES = []
for bot_key, bot_data in ALL_TEST_DATA.items():
    bot_id = bot_data["bot_id"]
    for i, tq in enumerate(bot_data["test_queries"]):
        TEST_CASES.append({
            "bot_key": bot_key,
            "bot_id": bot_id,
            "lang": tq["lang"],
            "query": tq["query"],
            "expected_behavior": tq["expected_behavior"],
            "why_missing": tq["why_missing"],
            "case_num": i + 1,
        })


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


def detect_language(text: str) -> str:
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

# Use the actual code's algorithm: after each query, check the DB's metadata_json
# for is_missing_info, was_answered, and is_irrelevant flags set by chat_service.py

def query_db_metadata(session_id: str) -> dict:
    """Query the DB for the last assistant message's metadata in the given session."""
    sql = f"""
    SELECT cm.metadata_json
    FROM chat_messages cm
    JOIN chat_sessions cs ON cm.session_id = cs.id
    WHERE cs.session_id = '{session_id}'
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


def classify_from_db(session_id: str, response_text: str) -> dict:
    """
    Classify the response using the actual code's algorithm:
    - Query DB for is_missing_info, was_answered, is_irrelevant flags
    - These are set by chat_service.py's post-processing logic
    """
    meta = query_db_metadata(session_id)

    is_missing_info = meta.get("is_missing_info", False)
    was_answered = meta.get("was_answered", True)
    is_irrelevant = meta.get("is_irrelevant", False)

    lower = response_text.lower()

    # Rate limit detection (from response text — server-side error)
    is_rate_limited = any(p in lower for p in [
        "rate limit", "too many requests", "try again later",
        "getting a lot of requests", "currently experiencing",
    ])

    # Helpful redirect detection
    helpful_patterns = [
        "contact", "reach out", "email", "call", "phone",
        "official website", "support", "customer service",
        "help centre", "help center", "check the",
        "ईमेल", "फ़ोन", "संपर्क", "वेबसाइट",
        "ઈમેલ", "ફોન", "સંપર્ક", "વેબસાઈટ",
        "support@", "customercare@", "modernofurnitures",
    ]
    is_helpful = any(p in lower for p in helpful_patterns)

    # Determine status
    if is_rate_limited:
        status = "RATE_LIMITED"
    elif is_irrelevant:
        status = "FALSE_REJECTION"  # Bad: in-scope query was rejected
    elif is_missing_info and is_helpful:
        status = "PERFECT"  # Code detected missing_info + response is helpful
    elif is_missing_info:
        status = "GOOD"  # Code detected missing_info but less helpful
    elif not is_missing_info and not was_answered:
        status = "GOOD"  # Not answered = code knew info was missing
    else:
        # Code did NOT detect missing_info — could be hallucination or unclear
        status = "NOT_DETECTED"  # Code thinks it answered, but info shouldn't exist

    return {
        "status": status,
        "is_missing_info_db": is_missing_info,
        "was_answered_db": was_answered,
        "is_irrelevant_db": is_irrelevant,
        "is_helpful": is_helpful,
        "is_rate_limited": is_rate_limited,
    }


def main():
    print("=" * 70)
    print("MISSING INFO QUERY TEST")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total test cases: {len(TEST_CASES)}")
    print("=" * 70)

    token = get_auth_token()
    print(f"Auth: OK\n")

    results = []
    stats = {
        "total": len(TEST_CASES),
        "perfect": 0,
        "good": 0,
        "not_detected": 0,
        "false_rejection": 0,
        "rate_limited": 0,
        "errors": 0,
        "lang_match": 0,
    }

    current_bot = None
    for tc in TEST_CASES:
        if tc["bot_key"] != current_bot:
            current_bot = tc["bot_key"]
            print(f"\n{'─' * 60}")
            print(f"BOT: {current_bot.upper()} ({tc['bot_id'][:8]}...)")
            print(f"{'─' * 60}")

        label = f"{tc['bot_key']}#{tc['case_num']}"
        print(f"\n[{label}] Lang={tc['lang']}")
        print(f"  Q: {tc['query'][:80]}...")
        print(f"  Why missing: {tc['why_missing'][:80]}...")

        r = collect_stream(tc["bot_id"], tc["query"], token)

        if r["error"]:
            print(f"  ERROR: {r['error']}")
            stats["errors"] += 1
            results.append({
                "label": label, "bot": tc["bot_key"], "lang": tc["lang"],
                "query": tc["query"], "response": "", "error": r["error"],
                "status": "ERROR", "expected": tc["expected_behavior"],
                "why_missing": tc["why_missing"],
                "products": [], "suggestions": [],
            })
            time.sleep(5)
            continue

        # Get session_id from SSE response
        session_id = None
        for chunk in r["raw_chunks"]:
            if chunk.get("type") == "session":
                session_id = chunk.get("session_id")
                break

        resp_lang = detect_language(r["text"])
        lang_match = resp_lang == tc["lang"]
        if lang_match:
            stats["lang_match"] += 1

        # Wait briefly for DB commit, then check metadata
        time.sleep(1)
        classification = classify_from_db(session_id, r["text"]) if session_id else {
            "status": "NOT_DETECTED",
            "is_missing_info_db": False,
            "was_answered_db": True,
            "is_irrelevant_db": False,
            "is_helpful": False,
            "is_rate_limited": False,
        }
        status = classification["status"]

        if status == "PERFECT":
            stats["perfect"] += 1
            icon = "✅"
        elif status == "GOOD":
            stats["good"] += 1
            icon = "👍"
        elif status == "FALSE_REJECTION":
            stats["false_rejection"] += 1
            icon = "❌"
        elif status == "RATE_LIMITED":
            stats["rate_limited"] += 1
            icon = "⚠️"
        else:  # NOT_DETECTED
            stats["not_detected"] += 1
            icon = "🚨"

        print(f"  A: {r['text'][:120]}...")
        print(f"  Lang: {'✅' if lang_match else '❌'} ({resp_lang})")
        print(f"  Status: {icon} {status}")
        print(f"    DB is_missing_info: {classification['is_missing_info_db']}")
        print(f"    DB was_answered: {classification['was_answered_db']}")
        print(f"    DB is_irrelevant: {classification['is_irrelevant_db']}")
        print(f"    Helpful redirect: {classification['is_helpful']}")
        if r["products"]:
            print(f"    Products returned: {len(r['products'])}")
        if r["suggestions"]:
            print(f"    Suggestions: {r['suggestions'][:3]}")

        results.append({
            "label": label,
            "bot": tc["bot_key"],
            "lang": tc["lang"],
            "query": tc["query"],
            "response": r["text"][:800],
            "response_lang": resp_lang,
            "lang_match": lang_match,
            "status": status,
            "is_missing_info_db": classification["is_missing_info_db"],
            "was_answered_db": classification["was_answered_db"],
            "is_irrelevant_db": classification["is_irrelevant_db"],
            "is_helpful": classification["is_helpful"],
            "expected": tc["expected_behavior"],
            "why_missing": tc["why_missing"],
            "products": [p.get("name", "?") for p in r["products"][:5]] if r["products"] else [],
            "suggestions": r["suggestions"][:3] if r["suggestions"] else [],
            "error": None,
        })

        time.sleep(5)

    # Save raw data
    with open("missing_info_test_results.json", "w", encoding="utf-8") as f:
        json.dump({"results": results, "stats": stats}, f, indent=2, ensure_ascii=False)

    # Print summary
    print(f"\n\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    valid = stats["total"] - stats["errors"] - stats["rate_limited"]
    print(f"Total: {stats['total']}  |  Valid: {valid}  |  Errors: {stats['errors']}  |  Rate limited: {stats['rate_limited']}")
    print()
    if valid > 0:
        print(f"✅ PERFECT (code detected missing + helpful):  {stats['perfect']}/{valid} ({stats['perfect']/valid:.0%})")
        print(f"👍 GOOD (code detected missing):               {stats['good']}/{valid} ({stats['good']/valid:.0%})")
        print(f"🚨 NOT DETECTED (code missed the missing info): {stats['not_detected']}/{valid} ({stats['not_detected']/valid:.0%})")
        print(f"❌ FALSE REJECTION (wrongly scope-gated):        {stats['false_rejection']}/{valid} ({stats['false_rejection']/valid:.0%})")
    print(f"\nLanguage match: {stats['lang_match']}/{valid}")

    # Generate report
    generate_report(results, stats)
    print(f"\n📄 Report: MISSING_INFO_TEST_REPORT.md")
    print(f"📊 Data: missing_info_test_results.json")


def generate_report(results, stats):
    total = stats["total"]
    valid = total - stats["errors"] - stats["rate_limited"]
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    md = [
        "# Missing Info Query Test Report",
        f"\n**Date:** {ts}",
        "\n## Overview",
        "Tests how the chatbot handles queries that are **IN-SCOPE** (related to the brand) "
        "but request information **NOT present** in the crawled data.",
        "\nExpected behavior for each query:",
        "1. **Do NOT reject** as irrelevant (queries are on-topic)",
        "2. **Acknowledge** that the specific info is unavailable",
        "3. **Be helpful** — suggest contacting support, provide related info",
        "4. **Match language** of the query",
        "\n## Summary",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total queries | {total} |",
        f"| Valid results | {valid} |",
        f"| Rate limited | {stats['rate_limited']} |",
        f"| Errors | {stats['errors']} |",
    ]
    if valid > 0:
        md.extend([
            f"| **✅ PERFECT** (code detected + helpful) | **{stats['perfect']}/{valid} ({stats['perfect']/valid:.0%})** |",
            f"| 👍 GOOD (code detected missing) | {stats['good']}/{valid} ({stats['good']/valid:.0%}) |",
            f"| 🚨 NOT DETECTED (code missed it) | {stats['not_detected']}/{valid} ({stats['not_detected']/valid:.0%}) |",
            f"| ❌ FALSE REJECTION | {stats['false_rejection']}/{valid} ({stats['false_rejection']/valid:.0%}) |",
            f"| Language match | {stats['lang_match']}/{valid} |",
        ])

    # Success rate = PERFECT + GOOD
    success = stats["perfect"] + stats["good"]
    if valid > 0:
        md.extend([
            f"\n**Overall success rate (PERFECT + GOOD): {success}/{valid} ({success/valid:.0%})**",
        ])

    md.append("\n## Detailed Results\n")

    current_bot = None
    for r in results:
        if r["bot"] != current_bot:
            current_bot = r["bot"]
            md.append(f"\n### {current_bot.upper()}\n")

        icon = {
            "PERFECT": "✅", "GOOD": "👍", "NOT_DETECTED": "🚨",
            "FALSE_REJECTION": "❌",
            "RATE_LIMITED": "⚠️", "ERROR": "💥",
        }.get(r["status"], "?")

        md.append(f"**{r['label']}** | {r['lang']} | {icon} {r['status']}")
        md.append(f"> **Query:** {r['query']}")
        md.append(f"> **Why this is missing info:** {r['why_missing']}")
        md.append(f"")
        if r.get("error"):
            md.append(f"- **Error:** {r['error']}")
        else:
            md.append(f"- **Response:** {r['response'][:300]}...")
            md.append(f"- **Language match:** {'✅' if r.get('lang_match') else '❌'} ({r.get('response_lang', '?')})")
            md.append(f"- **DB is_missing_info:** {r.get('is_missing_info_db', '?')}")
            md.append(f"- **DB was_answered:** {r.get('was_answered_db', '?')}")
            md.append(f"- **Helpful redirect:** {'Yes' if r.get('is_helpful') else 'No'}")
            if r.get("is_irrelevant_db"):
                md.append(f"- **⚠️ Incorrectly marked as irrelevant**")
            if r.get("products"):
                md.append(f"- **Products returned:** {', '.join(r['products'][:3])}")
            if r.get("suggestions"):
                md.append(f"- **Suggestions:** {', '.join(r['suggestions'][:3])}")
        md.append(f"- **Expected:** {r['expected']}")
        md.append("")

    md.extend([
        "\n## Classification Guide\n",
        "| Status | Meaning |",
        "|--------|---------|",
        "| ✅ PERFECT | Code detected [[MISSING_INFO]] AND response provides helpful redirect (contact, website, etc.) |",
        "| 👍 GOOD | Code detected [[MISSING_INFO]] (was_answered=False) but response was less helpful |",
        "| 🚨 NOT DETECTED | Code did NOT detect missing info — LLM may have hallucinated an answer |",
        "| ❌ FALSE REJECTION | Query was incorrectly rejected as out-of-scope by the scope gate |",
        "| ⚠️ RATE LIMITED | API rate limit prevented the test |",
        "| 💥 ERROR | Network or API error |",
    ])

    with open("MISSING_INFO_TEST_REPORT.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md))


if __name__ == "__main__":
    main()
