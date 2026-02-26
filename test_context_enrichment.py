#!/usr/bin/env python3
"""
Test: Context Enrichment & Follow-Up Query Handling
====================================================
Tests whether previous messages properly impact current queries across languages.
Each test pair:
  1. Query 1: Simple product-related question
  2. Query 2: Follow-up that REQUIRES context from Query 1 to make sense

Both sent in the SAME session so history is available.
We check if Query 2's response correctly references context from Query 1.
"""

import httpx
import json
import time
import uuid
import re
from datetime import datetime

BASE = "http://localhost:8000/api/v1"
AUTH = {"email": "max@gmail.com", "password": "12345678"}

# Bot IDs (DB UUIDs) and their supported languages
BOTS = {
    "tentree": {
        "id": "799637f9-391b-4b9d-84cb-5fdd17cdf109",
        "langs": ["en", "hi", "gu"],
    },
    "deathwish": {
        "id": "99fc3604-99e7-4cd0-a2a6-509ac08d9fd0",
        "langs": ["en", "hi"],
    },
    "beardbrand": {
        "id": "e23fcc6f-7a02-4b09-8d49-95c00a57d852",
        "langs": ["en", "gu"],
    },
    "ramraj": {
        "id": "182f88cd-02d8-4c94-824d-b41432847400",
        "langs": ["en", "hi"],
    },
    "kriyanta": {
        "id": "1cb18dc0-4909-409d-ab03-0436524fcec4",
        "langs": ["en", "gu"],
    },
    "zevaramaze": {
        "id": "e79b3754-006d-45d5-b21d-2391710e08ca",
        "langs": ["gu"],
    },
}

# Test pairs: (lang, query1, query2, context_keywords)
# context_keywords = words that should appear in query2's response if enrichment worked
TEST_PAIRS = {
    "tentree": [
        {
            "lang": "en",
            "q1": "What materials are your t-shirts made from?",
            "q2": "Are they available in black?",
            "context_keywords": ["t-shirt", "shirt", "tee", "top", "apparel", "black"],
            "description": "Follow-up about color availability for previously discussed product",
        },
        {
            "lang": "hi",
            "q1": "आपके पास कौन से पेड़ लगाने वाले प्रोडक्ट्स हैं?",
            "q2": "इनकी कीमत क्या है?",
            "context_keywords": ["price", "कीमत", "रुपय", "₹", "$", "product", "प्रोडक्ट"],
            "description": "Hindi follow-up asking price of previously discussed products",
        },
        {
            "lang": "gu",
            "q1": "તમારા સસ્ટેનેબલ કપડાં વિશે જણાવો",
            "q2": "તેની ડિલિવરી કેટલા દિવસમાં થાય છે?",
            "context_keywords": ["delivery", "ડિલિવરી", "ship", "day", "દિવસ"],
            "description": "Gujarati follow-up about delivery of previously discussed clothing",
        },
    ],
    "deathwish": [
        {
            "lang": "en",
            "q1": "What is your strongest coffee blend?",
            "q2": "How should I brew it for the best taste?",
            "context_keywords": ["brew", "coffee", "strong", "taste", "cup", "water"],
            "description": "Follow-up about brewing the previously discussed blend",
        },
        {
            "lang": "hi",
            "q1": "आपकी सबसे पॉपुलर कॉफी कौन सी है?",
            "q2": "क्या मैं इसे ऑनलाइन ऑर्डर कर सकता हूँ?",
            "context_keywords": ["order", "ऑर्डर", "online", "ऑनलाइन", "buy", "खरीद"],
            "description": "Hindi follow-up about ordering the previously discussed coffee",
        },
    ],
    "beardbrand": [
        {
            "lang": "en",
            "q1": "What beard oils do you sell?",
            "q2": "Which one is best for sensitive skin?",
            "context_keywords": ["oil", "beard", "sensitive", "skin", "recommend"],
            "description": "Follow-up about specific oil recommendation from previous context",
        },
        {
            "lang": "gu",
            "q1": "તમારા બિયર્ડ પ્રોડક્ટ્સ વિશે જણાવો",
            "q2": "કયું સૌથી વધુ વેચાય છે?",
            "context_keywords": ["beard", "product", "popular", "sell", "best", "પ્રોડક્ટ"],
            "description": "Gujarati follow-up about best-selling beard product",
        },
    ],
    "ramraj": [
        {
            "lang": "en",
            "q1": "What types of dhotis do you have?",
            "q2": "Which fabric is most comfortable in summer?",
            "context_keywords": ["dhoti", "cotton", "fabric", "summer", "comfort"],
            "description": "Follow-up about fabric for previously discussed dhotis",
        },
        {
            "lang": "hi",
            "q1": "क्या आपके पास सिल्क धोती है?",
            "q2": "इसकी कीमत कितनी है?",
            "context_keywords": ["silk", "सिल्क", "धोती", "price", "कीमत", "₹"],
            "description": "Hindi follow-up asking price of silk dhoti",
        },
    ],
    "kriyanta": [
        {
            "lang": "en",
            "q1": "What skincare products do you offer?",
            "q2": "Do any of them contain aloe vera?",
            "context_keywords": ["skincare", "skin", "aloe", "product", "ingredient"],
            "description": "Follow-up about ingredients in previously discussed products",
        },
        {
            "lang": "gu",
            "q1": "તમારા સ્કિનકેર પ્રોડક્ટ્સ વિશે જણાવો",
            "q2": "કયું ડ્રાય સ્કિન માટે સારું છે?",
            "context_keywords": ["skin", "dry", "product", "સ્કિન", "પ્રોડક્ટ"],
            "description": "Gujarati follow-up about dry skin product recommendation",
        },
    ],
    "zevaramaze": [
        {
            "lang": "gu",
            "q1": "તમારા સૌથી લોકપ્રિય પ્રોડક્ટ્સ કયા છે?",
            "q2": "તેની કિંમત શું છે?",
            "context_keywords": ["price", "કિંમત", "₹", "product", "પ્રોડક્ટ"],
            "description": "Gujarati follow-up asking price of previously discussed products",
        },
    ],
}


def get_auth_token():
    with httpx.Client() as c:
        r = c.post(f"{BASE}/auth/login", json=AUTH)
        return r.json()["access_token"]


def collect_stream(bot_id: str, message: str, session_id: str = None, token: str = None) -> dict:
    """Send a streaming chat message and collect from SSE."""
    if not session_id:
        session_id = str(uuid.uuid4())

    full_text = ""
    products = []
    suggestions = []
    error = None
    returned_session_id = session_id

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        with httpx.Client(timeout=90.0) as client:
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
                        "session_id": session_id,
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


def check_context_awareness(response_text: str, keywords: list, q1_text: str) -> dict:
    """Check if the follow-up response shows awareness of the first query's context."""
    resp_lower = response_text.lower()
    
    # Check keyword matches
    matched_keywords = [kw for kw in keywords if kw.lower() in resp_lower]
    keyword_score = len(matched_keywords) / max(len(keywords), 1)
    
    # Check if response is NOT a generic "I don't understand" / "could you clarify"
    confusion_patterns = [
        "what do you mean",
        "could you clarify",
        "i'm not sure what",
        "please specify",
        "which product",
        "can you be more specific",
        "what are you referring to",
        "i don't understand",
    ]
    shows_confusion = any(p in resp_lower for p in confusion_patterns)
    
    # Check if response is a rate limit message
    is_rate_limited = (
        "rate limit" in resp_lower
        or "too many requests" in resp_lower
        or "try again" in resp_lower
        or "getting a lot of requests" in resp_lower
    )
    
    # Check if response is a scope gate rejection
    is_scope_gated = (
        "outside my expertise" in resp_lower
        or "mere scope se bahar" in resp_lower
        or "mara scope ni bahar" in resp_lower
        or "दायरे से बाहर" in resp_lower
        or "દાયરાની બહાર" in resp_lower
    )

    # Determine enrichment status
    if is_rate_limited:
        status = "RATE_LIMITED"
    elif is_scope_gated:
        status = "SCOPE_GATED"
    elif shows_confusion:
        status = "NO_CONTEXT"  # Follow-up was not understood
    elif keyword_score >= 0.15:
        status = "CONTEXT_AWARE"  # Response references previous context
    else:
        status = "UNCLEAR"  # Can't determine - may still work but keywords didn't match

    return {
        "status": status,
        "keyword_score": round(keyword_score, 2),
        "matched_keywords": matched_keywords,
        "shows_confusion": shows_confusion,
        "is_rate_limited": is_rate_limited,
        "is_scope_gated": is_scope_gated,
    }


def main():
    print("=" * 70)
    print("CONTEXT ENRICHMENT & FOLLOW-UP TEST")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    token = get_auth_token()
    print(f"Auth: OK\n")

    results = []
    stats = {
        "total_pairs": 0,
        "context_aware": 0,
        "no_context": 0,
        "unclear": 0,
        "rate_limited": 0,
        "scope_gated": 0,
        "q1_errors": 0,
        "q2_errors": 0,
        "lang_match_q1": 0,
        "lang_match_q2": 0,
    }

    for bot_name, pairs in TEST_PAIRS.items():
        bot_id = BOTS[bot_name]["id"]
        print(f"\n{'─' * 60}")
        print(f"BOT: {bot_name.upper()} ({bot_id[:8]}...)")
        print(f"{'─' * 60}")

        for i, pair in enumerate(pairs):
            stats["total_pairs"] += 1
            pair_num = f"{bot_name}#{i+1}"
            lang = pair["lang"]
            
            print(f"\n[{pair_num}] Lang={lang} | {pair['description']}")
            
            # --- Query 1: Initial product question ---
            print(f"  Q1: {pair['q1'][:60]}...")
            session_id = None  # Let server create new session
            r1 = collect_stream(bot_id, pair["q1"], session_id=session_id, token=token)
            
            if r1["error"]:
                print(f"  Q1 ERROR: {r1['error']}")
                stats["q1_errors"] += 1
                results.append({
                    "pair": pair_num, "bot": bot_name, "lang": lang,
                    "q1": pair["q1"], "q2": pair["q2"],
                    "q1_response": "", "q2_response": "",
                    "q1_error": r1["error"], "q2_error": None,
                    "enrichment_status": "Q1_ERROR",
                    "description": pair["description"],
                })
                continue

            q1_lang = detect_response_language(r1["text"])
            q1_lang_match = q1_lang == lang.split("-")[0]  # Base lang match
            if q1_lang_match:
                stats["lang_match_q1"] += 1
            
            print(f"  A1: {r1['text'][:100]}...")
            print(f"  Q1 Lang: {'✅' if q1_lang_match else '❌'} ({q1_lang})")
            
            # Get session_id from Q1 for Q2
            returned_session = r1["session_id"]
            
            # Brief pause between queries
            time.sleep(5)
            
            # --- Query 2: Follow-up requiring context ---
            print(f"  Q2: {pair['q2'][:60]}...")
            r2 = collect_stream(bot_id, pair["q2"], session_id=returned_session, token=token)
            
            if r2["error"]:
                print(f"  Q2 ERROR: {r2['error']}")
                stats["q2_errors"] += 1
                results.append({
                    "pair": pair_num, "bot": bot_name, "lang": lang,
                    "q1": pair["q1"], "q2": pair["q2"],
                    "q1_response": r1["text"][:300], "q2_response": "",
                    "q1_error": None, "q2_error": r2["error"],
                    "enrichment_status": "Q2_ERROR",
                    "description": pair["description"],
                })
                continue

            q2_lang = detect_response_language(r2["text"])
            q2_lang_match = q2_lang == lang.split("-")[0]
            if q2_lang_match:
                stats["lang_match_q2"] += 1

            # Check context awareness
            ctx = check_context_awareness(r2["text"], pair["context_keywords"], pair["q1"])
            
            if ctx["status"] == "CONTEXT_AWARE":
                stats["context_aware"] += 1
                icon = "✅"
            elif ctx["status"] == "NO_CONTEXT":
                stats["no_context"] += 1
                icon = "❌"
            elif ctx["status"] == "RATE_LIMITED":
                stats["rate_limited"] += 1
                icon = "⚠️"
            elif ctx["status"] == "SCOPE_GATED":
                stats["scope_gated"] += 1
                icon = "🚫"
            else:
                stats["unclear"] += 1
                icon = "❓"
            
            print(f"  A2: {r2['text'][:100]}...")
            print(f"  Q2 Lang: {'✅' if q2_lang_match else '❌'} ({q2_lang})")
            print(f"  Enrichment: {icon} {ctx['status']} "
                  f"(keywords: {ctx['keyword_score']:.0%}, matched: {ctx['matched_keywords'][:3]})")
            
            results.append({
                "pair": pair_num,
                "bot": bot_name,
                "lang": lang,
                "description": pair["description"],
                "q1": pair["q1"],
                "q2": pair["q2"],
                "q1_response": r1["text"][:500],
                "q2_response": r2["text"][:500],
                "q1_lang_detected": q1_lang,
                "q2_lang_detected": q2_lang,
                "q1_lang_match": q1_lang_match,
                "q2_lang_match": q2_lang_match,
                "enrichment_status": ctx["status"],
                "keyword_score": ctx["keyword_score"],
                "matched_keywords": ctx["matched_keywords"],
                "shows_confusion": ctx["shows_confusion"],
                "session_id": returned_session,
            })
            
            # Longer pause between pairs to avoid rate limits
            time.sleep(8)

    # --- Save raw results ---
    with open("context_enrichment_results.json", "w", encoding="utf-8") as f:
        json.dump({"results": results, "stats": stats}, f, indent=2, ensure_ascii=False)

    # --- Print Summary ---
    print(f"\n\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    total = stats["total_pairs"]
    valid = total - stats["q1_errors"] - stats["q2_errors"] - stats["rate_limited"]
    
    print(f"Total pairs tested: {total}")
    print(f"Q1 errors: {stats['q1_errors']}")
    print(f"Q2 errors: {stats['q2_errors']}")
    print(f"Rate limited: {stats['rate_limited']}")
    print(f"Scope gated: {stats['scope_gated']}")
    print(f"Valid results: {valid}")
    print()
    if valid > 0:
        print(f"✅ Context-aware: {stats['context_aware']}/{valid} ({stats['context_aware']/valid:.0%})")
        print(f"❌ No context: {stats['no_context']}/{valid} ({stats['no_context']/valid:.0%})")
        print(f"❓ Unclear: {stats['unclear']}/{valid} ({stats['unclear']/valid:.0%})")
    print()
    print(f"Q1 language match: {stats['lang_match_q1']}/{total}")
    print(f"Q2 language match: {stats['lang_match_q2']}/{total - stats['q1_errors'] - stats['q2_errors']}")

    # --- Generate Report ---
    generate_report(results, stats)
    print(f"\n📄 Report: CONTEXT_ENRICHMENT_REPORT.md")
    print(f"📊 Data: context_enrichment_results.json")


def generate_report(results, stats):
    total = stats["total_pairs"]
    valid = total - stats["q1_errors"] - stats["q2_errors"] - stats["rate_limited"]
    
    md = []
    md.append("# Context Enrichment & Follow-Up Test Report")
    md.append(f"\n**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    md.append(f"\n## Overview")
    md.append(f"Tests whether previous messages properly enrich follow-up queries across languages.")
    md.append(f"Each pair: Query 1 (product) → Query 2 (follow-up needing Q1 context).")
    md.append(f"\n## Summary")
    md.append(f"| Metric | Value |")
    md.append(f"|--------|-------|")
    md.append(f"| Total pairs | {total} |")
    md.append(f"| Valid results | {valid} |")
    md.append(f"| Rate limited | {stats['rate_limited']} |")
    md.append(f"| Q1/Q2 errors | {stats['q1_errors']}/{stats['q2_errors']} |")
    if valid > 0:
        md.append(f"| **Context-aware** | **{stats['context_aware']}/{valid} ({stats['context_aware']/valid:.0%})** |")
        md.append(f"| No context | {stats['no_context']}/{valid} ({stats['no_context']/valid:.0%}) |")
        md.append(f"| Unclear | {stats['unclear']}/{valid} ({stats['unclear']/valid:.0%}) |")
    md.append(f"| Scope gated | {stats['scope_gated']} |")
    md.append(f"| Q1 lang match | {stats['lang_match_q1']}/{total} |")
    md.append(f"| Q2 lang match | {stats['lang_match_q2']}/{total - stats['q1_errors'] - stats['q2_errors']} |")

    md.append(f"\n## Detailed Results\n")
    
    current_bot = None
    for r in results:
        if r["bot"] != current_bot:
            current_bot = r["bot"]
            md.append(f"\n### {current_bot.upper()}\n")
        
        status_icon = {
            "CONTEXT_AWARE": "✅",
            "NO_CONTEXT": "❌",
            "UNCLEAR": "❓",
            "RATE_LIMITED": "⚠️",
            "SCOPE_GATED": "🚫",
            "Q1_ERROR": "💥",
            "Q2_ERROR": "💥",
        }.get(r.get("enrichment_status", ""), "?")
        
        md.append(f"**{r['pair']}** | {r['lang']} | {status_icon} {r['enrichment_status']}")
        md.append(f"> {r['description']}")
        md.append(f"")
        md.append(f"- **Q1:** {r['q1']}")
        md.append(f"- **A1:** {r.get('q1_response', 'N/A')[:200]}...")
        md.append(f"- **Q2:** {r['q2']}")
        md.append(f"- **A2:** {r.get('q2_response', 'N/A')[:200]}...")
        if r.get("matched_keywords"):
            md.append(f"- **Matched keywords:** {', '.join(r['matched_keywords'][:5])}")
        if r.get("keyword_score") is not None:
            md.append(f"- **Keyword score:** {r['keyword_score']:.0%}")
        md.append("")

    md.append(f"\n## Interpretation\n")
    md.append(f"- **CONTEXT_AWARE**: Follow-up response correctly referenced the previous query's context")
    md.append(f"- **NO_CONTEXT**: Response showed confusion or asked for clarification (enrichment failed)")
    md.append(f"- **UNCLEAR**: Could not determine from keywords alone (manual review recommended)")
    md.append(f"- **RATE_LIMITED**: API rate limit prevented the test")
    md.append(f"- **SCOPE_GATED**: Query was incorrectly rejected as out-of-scope")

    with open("CONTEXT_ENRICHMENT_REPORT.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md))


if __name__ == "__main__":
    main()
