"""
Quick targeted Gemini Call 2 test with 5 queries and long delays.
Purpose: Fill the data gap for Gemini response generation quality.
"""
import asyncio, httpx, json, time

GEMINI_KEY_1 = "AIzaSyBQbvzhHyhuqY9sT-b5jSqs9L5GT08se34"  # gemini-2.5-flash
GEMINI_KEY_3 = "AIzaSyDqlz2bCrcVEtZpAkXRM4NAWI78BHG7cFA"  # gemini-2.0-flash
GEMINI_API = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"

# 5 diverse queries covering the key test categories
QUERIES = [
    {"type": "product_browse", "lang": "en", "query": "Show me your best sellers", "bot": "deathwish", "expected_lang": "english"},
    {"type": "product_browse", "lang": "hi", "query": "मुझे ground coffee दिखाओ", "bot": "deathwish", "expected_lang": "hindi"},
    {"type": "irrelevant", "lang": "en", "query": "Who is the Prime Minister of India?", "bot": "deathwish", "expected_lang": "english"},
    {"type": "greeting", "lang": "gu", "query": "નમસ્તે! કેમ છો?", "bot": "zevaramaze", "expected_lang": "gujarati"},
    {"type": "price_filter", "lang": "en", "query": "Show me coffee under $50", "bot": "deathwish", "expected_lang": "english"},
]

BOT_CONFIG = {
    "deathwish": {
        "name": "Death Wish Coffee",
        "products": "Premium coffee: Death Wish Coffee Ground ($19.99), Espresso Roast ($21.99), Pumpkin Chai Latte ($15.99), Cold Brew ($14.99). Categories: Ground, Whole Bean, K-Cups, Cold Brew, Merchandise.",
        "languages": ["english", "hindi"],
    },
    "zevaramaze": {
        "name": "Zevaramaze Jewelry",
        "products": "Handmade jewelry: Silver Bangle Bracelet (₹1,499), Gold Plated Charm Bracelet (₹2,999), Pearl String Bracelet (₹899), Beaded Anklet (₹599). Categories: Bracelets, Necklaces, Earrings, Anklets.",
        "languages": ["english", "hindi", "gujarati"],
    },
}

def build_call2_prompt(query, bot_key, expected_lang):
    bot = BOT_CONFIG[bot_key]
    system_prompt = f"""You are an AI shopping assistant chatbot for "{bot.get('name', 'our store')}".

PRODUCT CONTEXT:
{bot.get('products', 'Various products available.')}

CRITICAL RULES:
1. LANGUAGE: You MUST respond in {expected_lang}. The user's detected language is {expected_lang}.
2. IRRELEVANT QUERIES: If the query is NOT about products/shopping/store, respond ONLY with:
   "[IRRELEVANT_QUERY] I can only help with questions about {bot.get('name', 'our store')} products and services."
   (Translate this to {expected_lang} if needed)
3. MISSING INFO: If you don't have the specific information asked about, say so politely and suggest what you CAN help with.
4. SUGGESTIONS: At the END of EVERY response, add suggestions in this EXACT format:
   ---SUGGESTIONS---
   suggestion 1
   suggestion 2
   suggestion 3
   ---END---
5. NO JSON: Never include raw JSON, code blocks, or technical formatting in your response.
6. Be helpful, concise, and friendly."""

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query},
    ]

def evaluate(response_text, query_info):
    score = 0
    details = {}
    
    if response_text and len(response_text) > 5:
        score += 1
        details["has_response"] = True
    else:
        details["has_response"] = False
        return score, details
    
    # Language check
    lang = query_info["expected_lang"]
    if lang == "english":
        details["lang_ok"] = True
        score += 1
    elif lang == "hindi":
        hindi_chars = sum(1 for c in response_text if '\u0900' <= c <= '\u097F')
        details["lang_ok"] = hindi_chars > 5
        score += 1 if details["lang_ok"] else 0
    elif lang == "gujarati":
        guj_chars = sum(1 for c in response_text if '\u0A80' <= c <= '\u0AFF')
        details["lang_ok"] = guj_chars > 5
        score += 1 if details["lang_ok"] else 0
    
    # Irrelevant marker
    if query_info["type"] == "irrelevant":
        details["irrel_ok"] = "[IRRELEVANT_QUERY]" in response_text or "irrelevant" in response_text.lower()
    else:
        details["irrel_ok"] = "[IRRELEVANT_QUERY]" not in response_text
    score += 1 if details["irrel_ok"] else 0
    
    # Suggestions
    details["sugg_ok"] = "---SUGGESTIONS---" in response_text and "---END---" in response_text
    score += 1 if details["sugg_ok"] else 0
    
    # No JSON leak
    details["no_leak"] = '{"' not in response_text and '"language"' not in response_text
    score += 1 if details["no_leak"] else 0
    
    return score, details

async def test_model(model_name, api_key, delay_s=15):
    print(f"\n{'='*60}")
    print(f"  Testing {model_name} for Call 2 (5 queries, {delay_s}s delay)")
    print(f"{'='*60}")
    
    results = []
    async with httpx.AsyncClient(timeout=60) as client:
        for i, q in enumerate(QUERIES):
            if i > 0:
                print(f"  Waiting {delay_s}s...", end="", flush=True)
                await asyncio.sleep(delay_s)
                print(" done")
            
            messages = build_call2_prompt(q["query"], q["bot"], q["expected_lang"])
            
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = {"model": model_name, "messages": messages, "temperature": 0.3, "max_tokens": 1024}
            
            start = time.time()
            try:
                resp = await client.post(GEMINI_API, headers=headers, json=payload)
                latency = int((time.time() - start) * 1000)
                
                if resp.status_code == 429:
                    print(f"  Q{i+1} [{q['type']}][{q['lang']}] ⏳ RATE LIMITED")
                    results.append({"query": q, "status": "rate_limited"})
                    continue
                elif resp.status_code != 200:
                    print(f"  Q{i+1} [{q['type']}][{q['lang']}] ❌ HTTP {resp.status_code}")
                    results.append({"query": q, "status": f"error_{resp.status_code}"})
                    continue
                
                data = resp.json()
                text = data["choices"][0]["message"]["content"]
                score, details = evaluate(text, q)
                
                marks = f"Resp:{'✓' if details.get('has_response') else '✗'} " \
                        f"Lang:{'✓' if details.get('lang_ok') else '✗'} " \
                        f"Irrel:{'✓' if details.get('irrel_ok') else '✗'} " \
                        f"Sugg:{'✓' if details.get('sugg_ok') else '✗'} " \
                        f"NoLeak:{'✓' if details.get('no_leak') else '✗'}"
                print(f"  Q{i+1} [{q['type']}][{q['lang']}] {latency}ms | {marks} | {score}/5")
                results.append({"query": q, "status": "ok", "score": score, "details": details, "latency": latency, "response_preview": text[:200]})
                
            except Exception as e:
                print(f"  Q{i+1} [{q['type']}][{q['lang']}] ❌ {str(e)[:60]}")
                results.append({"query": q, "status": "error", "error": str(e)[:100]})
    
    ok = [r for r in results if r.get("status") == "ok"]
    rl = [r for r in results if r.get("status") == "rate_limited"]
    print(f"\n  Summary: {len(ok)}/5 success, {len(rl)} rate limited")
    if ok:
        avg = sum(r["score"] for r in ok) / len(ok)
        avg_lat = sum(r["latency"] for r in ok) / len(ok)
        print(f"  Avg score: {avg:.2f}/5, Avg latency: {avg_lat:.0f}ms")
    
    return model_name, results

async def main():
    print("=" * 60)
    print("  GEMINI MINI-TEST: CALL 2 (Response Generation)")
    print("  5 queries per model, 15s delay between queries")
    print("=" * 60)
    
    all_results = {}
    
    # Test gemini-2.5-flash
    name, res = await test_model("gemini-2.5-flash", GEMINI_KEY_1, delay_s=15)
    all_results[name] = res
    
    print("\n\nWaiting 20s before next model...\n")
    await asyncio.sleep(20)
    
    # Test gemini-2.0-flash
    name, res = await test_model("gemini-2.0-flash", GEMINI_KEY_3, delay_s=15)
    all_results[name] = res
    
    # Save results
    with open("gemini_mini_results.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    
    print("\n\nResults saved to gemini_mini_results.json")

if __name__ == "__main__":
    asyncio.run(main())
