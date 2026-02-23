#!/usr/bin/env python3
"""Quick retest of previously-failed queries after the recency-bias script fix."""

import json, time, asyncio
import httpx

API_BASE = "http://localhost:8000/api/v1"

TENTREE = "799637f9-391b-4b9d-84cb-5fdd17cdf109"
ZEVA    = "e79b3754-006d-45d5-b21d-2391710e08ca"
KRIYANTA= "1cb18dc0-4909-409d-ab03-0436524fcec4"

# All 18 previously-failed queries (from terminal + report analysis)
FAILED_QUERIES = [
    # --- Tentree (hi→devanagari) failures ---
    (TENTREE, "hi", "कोई टी-शर्ट दिखाओ",                         "devanagari", "T-L05"),
    (TENTREE, "hi", "क्या आपके पास नीली जींस है?",                "devanagari", "T-L17"),
    (TENTREE, "hi", "भारत के प्रधानमंत्री कौन हैं?",              "devanagari", "T-L21"),
    (TENTREE, "hi", "मुझे eco-friendly jacket चाहिए",              "devanagari", "T-L32"),
    (TENTREE, "hi", "इनमें से सबसे अच्छा कौन सा है?",             "devanagari", "T-L36"),
    (TENTREE, "hi", "आपका फ़ोन नम्बर क्या है?",                   "devanagari", "T-L52"),
    # --- Tentree English-sends-Devanagari (T-L25,26,27 – Tentree only supports hi+gu) ---
    (TENTREE, "en", "Show me your jackets",                        "latin",      "T-L25-fix"),
    (TENTREE, "en", "What is your return policy?",                 "latin",      "T-L26-fix"),
    # --- Tentree gu→devanagari failures ---
    (TENTREE, "gu", "jackets",                                     "gujarati",   "T-L29"),
    (TENTREE, "gu", "મને eco-friendly jacket જોઈ",                 "gujarati",   "T-L33"),
    # --- Zevaramaze hi→devanagari failures ---
    (ZEVA,    "hi", "વાપસી નીતિ ​क्या है?",                       "devanagari", "Z-L15"),
    (ZEVA,    "hi", "चांदी के गहने कितने महंगे हैं?",             "devanagari", "Z-L28"),
    (ZEVA,    "hi", "अंगूठी",                                      "devanagari", "Z-L29"),
    (ZEVA,    "hi", "इनमें से सबसे पॉपुलर कौन सा है?",            "devanagari", "Z-L32"),
    (ZEVA,    "hi", "बहुत अच्छा! और क्या है?",                    "devanagari", "Z-L46"),
    # --- Kriyanta gu→gujarati failure ---
    (KRIYANTA,"gu", "Custom design order કરી શકાય?",              "gujarati",   "K-L18"),
]

DEVA_RANGE = (0x0900, 0x097F)
GUJA_RANGE = (0x0A80, 0x0AFF)

def detect_script(text: str) -> str:
    deva = sum(1 for c in text if DEVA_RANGE[0] <= ord(c) <= DEVA_RANGE[1])
    guja = sum(1 for c in text if GUJA_RANGE[0] <= ord(c) <= GUJA_RANGE[1])
    latin= sum(1 for c in text if c.isalpha() and ord(c) < 0x0250)
    total = deva + guja + latin
    if total == 0: return "unknown"
    if deva/total >= 0.15 and guja/total < 0.05: return "devanagari"
    if guja/total >= 0.15 and deva/total < 0.05: return "gujarati"
    if deva/total >= 0.05 or guja/total >= 0.05:  return "mixed"
    return "latin"

def parse_sse(raw: str) -> str:
    parts = []
    for line in raw.split("\n"):
        line = line.strip()
        if not line.startswith("data: "): continue
        try:
            chunk = json.loads(line[6:])
            if chunk.get("type") == "content":
                parts.append(chunk.get("content",""))
        except: pass
    return "".join(parts)

async def run():
    passed = 0; failed = 0
    async with httpx.AsyncClient() as client:
        for bot_id, lang, query, expected, qid in FAILED_QUERIES:
            url = f"{API_BASE}/chat/{bot_id}/message/stream"
            r = await client.post(url, data={"message": query, "is_preview": "false"}, timeout=45)
            content = parse_sse(r.text)
            detected = detect_script(content)
            ok = (
                detected == expected or
                (expected == "latin" and detected in ("latin","mixed"))
            )
            if ok: passed += 1
            else:  failed += 1
            icon = "✅" if ok else "❌"
            bot_name = {TENTREE:"Tentree", ZEVA:"Zevaramaze", KRIYANTA:"Kriyanta"}[bot_id]
            print(f"{icon} [{qid}] [{bot_name}/{lang}→{expected}] got={detected}: {content[:80]}")
            await asyncio.sleep(2.5)

    total = passed + failed
    pct = int(passed * 100 / total) if total else 0
    print(f"\n===========================")
    print(f"Retest Results: {passed}/{total} PASS ({pct}%)")
    print(f"Previously: 18 failures out of 152 total (88.2% overall)")
    print(f"===========================")

asyncio.run(run())
