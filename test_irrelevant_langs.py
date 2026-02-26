"""
Irrelevant Query Test — uses the EXISTING algorithm's detection:
  - [[IRRELEVANT]] tag in response text  (is_irrelevant)
  - _detect_message_language() for input & response language checks
  - Scope gate messages (humanized redirect in correct language)

Tests all queries from irrelevant_test_queries.json across multiple
languages (en, hi, hi-Latn, gu, gu-Latn).

Generates a markdown report.
"""
import httpx
import json
import time
import re
import unicodedata

# ── Config ──
BASE = "http://localhost:8000/api/v1"
AUTH = {"email": "max@gmail.com", "password": "12345678"}

# ── Replicate the existing _detect_message_language algo ──
SUPPORTED_LANGUAGES = {
    "hi": {"unicode_range": (0x0900, 0x097F), "name": "Hindi"},
    "gu": {"unicode_range": (0x0A80, 0x0AFF), "name": "Gujarati"},
}

def detect_language(text: str, default: str = "en") -> str:
    """Mirror of chat_service._detect_message_language"""
    if not text or not text.strip():
        return default
    text = text.strip()
    script_counts = {}
    latin_count = 0
    for char in text:
        cp = ord(char)
        if (0x0041 <= cp <= 0x005A) or (0x0061 <= cp <= 0x007A):
            latin_count += 1
            continue
        for lang_code, lang_info in SUPPORTED_LANGUAGES.items():
            ur = lang_info.get("unicode_range")
            if ur:
                start, end = ur
                if start <= cp <= end:
                    script_counts[lang_code] = script_counts.get(lang_code, 0) + 1
                    break
    script_counts["en"] = latin_count
    total = sum(script_counts.values())
    if total == 0:
        return default
    detected = max(script_counts.items(), key=lambda x: x[1])
    return detected[0] if detected[1] > 0 else default

def infer_response_language(response_text: str, fallback: str) -> str:
    """Mirror of chat_service._infer_response_language"""
    language = (fallback or "en").strip() or "en"
    if language.endswith("-Latn"):
        return language
    base = language.split("-")[0]
    if not response_text:
        return base
    return detect_language(response_text, default=base)


def login():
    r = httpx.post(f"{BASE}/auth/login", json=AUTH, timeout=10)
    r.raise_for_status()
    return r.json()["access_token"]


def stream_chat(token, bot_id, message):
    url = f"{BASE}/chat/{bot_id}/message/stream"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"message": message}
    text = ""
    session_id = None
    with httpx.Client(timeout=60) as client:
        with client.stream("POST", url, data=data, headers=headers) as resp:
            for line in resp.iter_lines():
                if not line.startswith("data: "):
                    continue
                payload = line[6:]
                if payload == "[DONE]":
                    break
                try:
                    evt = json.loads(payload)
                except json.JSONDecodeError:
                    continue
                if evt.get("type") == "content":
                    text += evt.get("content", "")
                elif evt.get("type") == "session":
                    session_id = evt.get("session_id")
    return text.strip(), session_id


def check_is_irrelevant(response_text: str) -> bool:
    """
    Uses same logic as the existing algo:
    - [[IRRELEVANT]] tag in text (LLM-generated rejections)
    - Scope gate messages (humanized redirect — tag stripped before streaming)
    
    The scope gate sets is_irrelevant=True in DB metadata even though 
    [[IRRELEVANT]] is stripped from streamed content. So we must also
    detect the scope gate's humanized messages.
    """
    if "[[IRRELEVANT]]" in response_text:
        return True
    
    # Scope gate humanized messages (tag stripped before streaming)
    scope_gate_markers = [
        "outside my expertise",           # en
        "दायरे से बाहर",                   # hi
        "scope se bahar",                  # hi-Latn
        "scope ની બહાર",                   # gu
        "scope ni bahar",                  # gu-Latn
        "i can only help with",            # old-style en (if any remain)
    ]
    lower = response_text.lower()
    return any(m.lower() in lower for m in scope_gate_markers)


def check_humanized(response_text: str) -> bool:
    """Check if the response is warm/humanized (not robotic)"""
    clean = response_text.replace("[[IRRELEVANT]]", "").replace("[[MISSING_INFO]]", "").strip()
    # Scope gate humanized messages
    humanized_markers = [
        "oops", "😅", "outside my expertise", "outside",
        "अरे", "दायरे से बाहर", "scope se bahar",
        "scope ની બહાર", "scope ni bahar",
        "help you with", "help kar",
        "मदद कर", "મદદ કરી",
    ]
    return any(m in clean.lower() for m in humanized_markers) or len(clean) > 30


def check_language_match(query_lang: str, response_text: str) -> dict:
    """
    Check if response matches expected language using existing algo.
    Returns dict with detected language, match status, and details.
    """
    clean = response_text.replace("[[IRRELEVANT]]", "").replace("[[MISSING_INFO]]", "").strip()

    # Use exact same algo as the service
    input_lang = detect_language(response_text.replace("[[IRRELEVANT]]", "").replace("[[MISSING_INFO]]", ""), default="en")
    response_lang = infer_response_language(clean, query_lang)

    # For Latn variants, check script is Latin
    expected_base = query_lang.split("-")[0]
    is_latn = query_lang.endswith("-Latn")

    if is_latn:
        # Response should be in Latin script (romanized)
        # Check that there are no native script chars
        native_chars = sum(1 for c in clean if ord(c) > 0x007F and not unicodedata.category(c).startswith('S'))  # exclude symbols/emoji
        total_alpha = sum(1 for c in clean if c.isalpha())
        native_ratio = native_chars / max(total_alpha, 1)
        script_match = native_ratio < 0.1  # less than 10% native = good romanized
    elif expected_base == "hi":
        # Response should contain Devanagari
        devanagari = sum(1 for c in clean if 0x0900 <= ord(c) <= 0x097F)
        total_alpha = sum(1 for c in clean if c.isalpha() or 0x0900 <= ord(c) <= 0x097F)
        script_match = devanagari / max(total_alpha, 1) > 0.3
    elif expected_base == "gu":
        # Response should contain Gujarati
        gujarati = sum(1 for c in clean if 0x0A80 <= ord(c) <= 0x0AFF)
        total_alpha = sum(1 for c in clean if c.isalpha() or 0x0A80 <= ord(c) <= 0x0AFF)
        script_match = gujarati / max(total_alpha, 1) > 0.3
    else:
        # English
        script_match = True  # Default OK for English

    return {
        "detected_response_lang": response_lang,
        "expected_lang": query_lang,
        "script_match": script_match,
    }


def main():
    token = login()

    # Load queries
    with open("irrelevant_test_queries.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    queries = data["queries"]
    results = []

    print("=" * 80)
    print("IRRELEVANT QUERY TEST — Using Existing Algorithm Tags")
    print(f"Total queries: {len(queries)}")
    print("=" * 80)

    for i, q in enumerate(queries):
        bot = q["bot"]
        bot_id = q["bot_id"]
        query = q["query"]
        lang = q["language"]
        category = q["category"]

        print(f"\n[{i+1}/{len(queries)}] {bot} | {lang} | {category}")
        print(f"  Q: {query[:80]}")

        try:
            resp, sid = stream_chat(token, bot_id, query)

            # 1. Check irrelevant tag (existing algo)
            is_irrelevant = check_is_irrelevant(resp)

            # 2. Check humanization
            is_humanized = check_humanized(resp)

            # 3. Check language match (existing algo)
            lang_check = check_language_match(lang, resp)

            # 4. Check for rate limit errors
            is_rate_limited = "try again" in resp.lower() and "minutes" in resp.lower()

            clean = resp.replace("[[IRRELEVANT]]", "").replace("[[MISSING_INFO]]", "").strip()

            result = {
                "bot": bot,
                "query": query,
                "language": lang,
                "category": category,
                "response": clean[:300],
                "full_response": clean,
                "is_irrelevant_tagged": is_irrelevant,
                "is_humanized": is_humanized,
                "is_rate_limited": is_rate_limited,
                "lang_check": lang_check,
                "passed": is_irrelevant and not is_rate_limited,
            }
            results.append(result)

            tag = "✅ REJECTED" if is_irrelevant else ("⚠️ RATE_LIMITED" if is_rate_limited else "❌ FOOLED")
            lang_mark = "✅" if lang_check["script_match"] else "❌"
            human_mark = "😊" if is_humanized else "🤖"
            print(f"  {tag} | Lang: {lang_mark} ({lang_check['detected_response_lang']}) | {human_mark}")
            print(f"  A: {clean[:120]}")

        except Exception as e:
            print(f"  ⚠️ ERROR: {e}")
            results.append({
                "bot": bot, "query": query, "language": lang, "category": category,
                "response": str(e), "full_response": str(e),
                "is_irrelevant_tagged": False, "is_humanized": False,
                "is_rate_limited": False, "lang_check": {"script_match": False},
                "passed": False, "error": str(e),
            })

        time.sleep(0.5)  # avoid rate limits

    # ── Generate Report ──
    generate_report(results, queries)

    # Save raw results
    with open("irrelevant_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nRaw results saved to irrelevant_test_results.json")


def generate_report(results, queries):
    total = len(results)
    rejected = sum(1 for r in results if r["is_irrelevant_tagged"])
    humanized = sum(1 for r in results if r["is_humanized"] and r["is_irrelevant_tagged"])
    lang_match = sum(1 for r in results if r["lang_check"]["script_match"] and not r["is_rate_limited"])
    rate_limited = sum(1 for r in results if r["is_rate_limited"])
    fooled = sum(1 for r in results if not r["is_irrelevant_tagged"] and not r["is_rate_limited"])
    valid = total - rate_limited

    report = []
    report.append("# IRRELEVANT QUERY TEST REPORT")
    report.append("")
    report.append(f"**Date:** {time.strftime('%Y-%m-%d %H:%M')}")
    report.append(f"**Total Queries:** {total}")
    report.append(f"**Valid (non rate-limited):** {valid}")
    report.append("")
    report.append("## Summary")
    report.append("")
    report.append(f"| Metric | Count | Rate |")
    report.append(f"|--------|-------|------|")
    report.append(f"| Correctly Rejected ([[IRRELEVANT]] tag) | {rejected} | {100*rejected/max(valid,1):.0f}% |")
    report.append(f"| Humanized Rejections | {humanized} | {100*humanized/max(rejected,1):.0f}% of rejections |")
    report.append(f"| Language Match (correct script) | {lang_match} | {100*lang_match/max(valid,1):.0f}% |")
    report.append(f"| Fooled (answered irrelevant) | {fooled} | {100*fooled/max(valid,1):.0f}% |")
    report.append(f"| Rate Limited | {rate_limited} | {100*rate_limited/max(total,1):.0f}% |")
    report.append("")

    # Per-bot breakdown
    report.append("## Per-Bot Results")
    report.append("")
    bots = sorted(set(r["bot"] for r in results))
    for bot in bots:
        bot_results = [r for r in results if r["bot"] == bot]
        bot_rejected = sum(1 for r in bot_results if r["is_irrelevant_tagged"])
        bot_rl = sum(1 for r in bot_results if r["is_rate_limited"])
        bot_valid = len(bot_results) - bot_rl
        bot_lang = sum(1 for r in bot_results if r["lang_check"]["script_match"] and not r["is_rate_limited"])
        report.append(f"### {bot}")
        report.append(f"- Queries: {len(bot_results)} ({bot_valid} valid)")
        report.append(f"- Rejected: {bot_rejected}/{bot_valid} ({100*bot_rejected/max(bot_valid,1):.0f}%)")
        report.append(f"- Language Match: {bot_lang}/{bot_valid} ({100*bot_lang/max(bot_valid,1):.0f}%)")
        report.append("")

    # Per-language breakdown
    report.append("## Per-Language Results")
    report.append("")
    report.append("| Language | Total | Valid | Rejected | Lang Match | Rejection Rate |")
    report.append("|----------|-------|-------|----------|------------|---------------|")
    langs = sorted(set(r["language"] for r in results))
    for lang in langs:
        lr = [r for r in results if r["language"] == lang]
        l_total = len(lr)
        l_rl = sum(1 for r in lr if r["is_rate_limited"])
        l_valid = l_total - l_rl
        l_rej = sum(1 for r in lr if r["is_irrelevant_tagged"])
        l_lm = sum(1 for r in lr if r["lang_check"]["script_match"] and not r["is_rate_limited"])
        report.append(f"| {lang} | {l_total} | {l_valid} | {l_rej} | {l_lm} | {100*l_rej/max(l_valid,1):.0f}% |")
    report.append("")

    # Detailed results table
    report.append("## Detailed Results")
    report.append("")
    report.append("| # | Bot | Language | Category | Query | Rejected | Humanized | Lang Match | Response (preview) |")
    report.append("|---|-----|----------|----------|-------|----------|-----------|------------|-------------------|")
    for i, r in enumerate(results):
        rej = "✅" if r["is_irrelevant_tagged"] else ("⚠️ RL" if r["is_rate_limited"] else "❌")
        hum = "😊" if r["is_humanized"] else "🤖"
        lang = "✅" if r["lang_check"]["script_match"] else "❌"
        resp_preview = r["response"][:80].replace("|", "\\|").replace("\n", " ")
        query_preview = r["query"][:50].replace("|", "\\|")
        report.append(f"| {i+1} | {r['bot']} | {r['language']} | {r['category']} | {query_preview} | {rej} | {hum} | {lang} | {resp_preview} |")
    report.append("")

    # Failures detail
    failures = [r for r in results if not r["is_irrelevant_tagged"] and not r["is_rate_limited"]]
    if failures:
        report.append("## Failures (bot answered irrelevant query)")
        report.append("")
        for r in failures:
            report.append(f"### {r['bot']} | {r['language']} | {r['category']}")
            report.append(f"- **Query:** {r['query']}")
            report.append(f"- **Response:** {r['response'][:200]}")
            report.append(f"- **Language Match:** {'✅' if r['lang_check']['script_match'] else '❌'} (detected: {r['lang_check']['detected_response_lang']})")
            report.append("")

    md = "\n".join(report)
    with open("IRRELEVANT_TEST_REPORT.md", "w", encoding="utf-8") as f:
        f.write(md)
    print(f"\n{'='*60}")
    print(f"Report saved to IRRELEVANT_TEST_REPORT.md")
    print(f"{'='*60}")

    # Print summary
    print(f"\nRejection: {rejected}/{valid} ({100*rejected/max(valid,1):.0f}%)")
    print(f"Humanized: {humanized}/{rejected} ({100*humanized/max(rejected,1):.0f}%)")
    print(f"Lang Match: {lang_match}/{valid} ({100*lang_match/max(valid,1):.0f}%)")
    print(f"Fooled: {fooled}/{valid}")
    print(f"Rate Limited: {rate_limited}/{total}")


if __name__ == "__main__":
    main()
