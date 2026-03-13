"""
Comprehensive chatbot test runner — 80 queries across 10 bots.
Runs inside chatbot_api container. Outputs JSON results.
"""
import httpx
import json
import time
import sys

BASE = "http://localhost:8000/api/v1"

# All 10 chatbots with their IDs
BOTS = {
    "zevaramaze": "163f8555-03b7-4d25-aab0-79cbfc757616",
    "BigBasket": "9d88aa90-d351-453f-93e7-4cd13ab5fef1",
    "BoAt": "3bb73cc8-e9ab-4c8e-b87d-73cdd0d2483d",
    "Byjus": "5eb7c096-6edd-4a82-add5-c41bfc8882d3",
    "Mamaearth": "c3c933ca-3ffc-4959-9447-92c7f79b457e",
    "Mokobara": "35dd7e5e-f589-4333-b2b5-8b0f496b43da",
    "Nicobar": "9c34c714-073c-483a-945d-730a102092ab",
    "PlumGoodness": "4ef4ea06-eba5-4319-9b4c-c74ca7f7dc23",
    "SlurrpFarm": "ff936f98-ed66-4a03-b0c4-80b4b8e9c324",
    "TheManCompany": "35fdd3ff-c56c-4877-8452-94b9fa1dd492",
}

# 80 test queries
QUERIES = [
    # === zevaramaze (en, gu) ===
    {"bot": "zevaramaze", "query": "What silver rings do you have for men?", "lang": "en", "type": "product"},
    {"bot": "zevaramaze", "query": "Tell me about Zevar Amaze — what kind of jewelry do you sell?", "lang": "en", "type": "general"},
    {"bot": "zevaramaze", "query": "મોઈસનાઈટ રિંગ્સ વિશે મને જણાવો", "lang": "gu", "type": "gujarati"},
    {"bot": "zevaramaze", "query": "શું તમારી પાસે ગોલ્ડ જ્વેલરી છે?", "lang": "gu", "type": "gujarati"},
    {"bot": "zevaramaze", "query": "What is your return and exchange policy?", "lang": "en", "type": "missing_info"},
    {"bot": "zevaramaze", "query": "Can you help me book a flight to Mumbai?", "lang": "en", "type": "irrelevant"},
    {"bot": "zevaramaze", "query": "What's the difference between moissanite and CZ rings?", "lang": "en", "type": "comparison"},
    {"bot": "zevaramaze", "query": "How do I take care of my silver jewelry?", "lang": "en", "type": "how_to"},

    # === BigBasket (en, hi) ===
    {"bot": "BigBasket", "query": "What ayurveda products are available on BigBasket?", "lang": "en", "type": "product"},
    {"bot": "BigBasket", "query": "What is BigBasket and what do they deliver?", "lang": "en", "type": "general"},
    {"bot": "BigBasket", "query": "क्या बिगबास्केट पर चॉकलेट गिफ्ट बॉक्स मिलते हैं?", "lang": "hi", "type": "hindi"},
    {"bot": "BigBasket", "query": "प्रोटीन सप्लीमेंट्स कौन कौन से हैं?", "lang": "hi", "type": "hindi"},
    {"bot": "BigBasket", "query": "Does BigBasket deliver to the US or Europe?", "lang": "en", "type": "missing_info"},
    {"bot": "BigBasket", "query": "How do I invest in the stock market?", "lang": "en", "type": "irrelevant"},
    {"bot": "BigBasket", "query": "Which is better — buying medicine online vs Ayurveda products on your site?", "lang": "en", "type": "comparison"},
    {"bot": "BigBasket", "query": "How do I order medicines online from BigBasket?", "lang": "en", "type": "how_to"},

    # === BoAt (en) ===
    {"bot": "BoAt", "query": "What are the best boAt ANC earbuds?", "lang": "en", "type": "product"},
    {"bot": "BoAt", "query": "What is boAt Lifestyle and what products do they make?", "lang": "en", "type": "general"},
    {"bot": "BoAt", "query": "Which portable speakers are good for a party under 8000 rupees?", "lang": "en", "type": "product"},
    {"bot": "BoAt", "query": "What smartwatches did boAt launch recently?", "lang": "en", "type": "product"},
    {"bot": "BoAt", "query": "Does boAt offer international warranty?", "lang": "en", "type": "missing_info"},
    {"bot": "BoAt", "query": "Can you recommend a good laptop for programming?", "lang": "en", "type": "irrelevant"},
    {"bot": "BoAt", "query": "What's the difference between TWS earbuds, neckbands, and headphones for ANC?", "lang": "en", "type": "comparison"},
    {"bot": "BoAt", "query": "How do I set up a boAt soundbar for my TV?", "lang": "en", "type": "how_to"},

    # === Byju's (en, hi, gu) ===
    {"bot": "Byjus", "query": "How important are NCERT notes for UPSC preparation?", "lang": "en", "type": "product"},
    {"bot": "Byjus", "query": "What is BYJU'S and what courses do they offer?", "lang": "en", "type": "general"},
    {"bot": "Byjus", "query": "UPSC की तैयारी के लिए BYJU'S कैसे मदद करता है?", "lang": "hi", "type": "hindi"},
    {"bot": "Byjus", "query": "બાયજુસ પર કઈ કઈ પરીક્ષાઓની તૈયારી કરી શકાય?", "lang": "gu", "type": "gujarati"},
    {"bot": "Byjus", "query": "Does Byju's offer courses for MBA entrance exams like CAT?", "lang": "en", "type": "missing_info"},
    {"bot": "Byjus", "query": "What is the best recipe for butter chicken?", "lang": "en", "type": "irrelevant"},
    {"bot": "Byjus", "query": "What's the difference between Byju's Classes and the Learning App?", "lang": "en", "type": "comparison"},
    {"bot": "Byjus", "query": "How do I book a free session on Byju's?", "lang": "en", "type": "how_to"},

    # === Mamaearth (en) ===
    {"bot": "Mamaearth", "query": "What baby care products does Mamaearth have?", "lang": "en", "type": "product"},
    {"bot": "Mamaearth", "query": "Tell me about Mamaearth as a brand — are products really toxin-free?", "lang": "en", "type": "general"},
    {"bot": "Mamaearth", "query": "Which Mamaearth shampoo is best for hair treatment?", "lang": "en", "type": "product"},
    {"bot": "Mamaearth", "query": "Do you have any charcoal-based makeup products?", "lang": "en", "type": "product"},
    {"bot": "Mamaearth", "query": "Does Mamaearth ship to Canada?", "lang": "en", "type": "missing_info"},
    {"bot": "Mamaearth", "query": "Can you help me find a good dentist near me?", "lang": "en", "type": "irrelevant"},
    {"bot": "Mamaearth", "query": "What's the difference between Aqua Glow Face Wash and the regular one?", "lang": "en", "type": "comparison"},
    {"bot": "Mamaearth", "query": "How do I use the Aloe Vera Gel for skin and hair?", "lang": "en", "type": "how_to"},

    # === Mokobara (en, hi) ===
    {"bot": "Mokobara", "query": "What luggage sets are available on Mokobara?", "lang": "en", "type": "product"},
    {"bot": "Mokobara", "query": "What is Mokobara known for?", "lang": "en", "type": "general"},
    {"bot": "Mokobara", "query": "क्या मोकोबारा पर बैकपैक मिलते हैं?", "lang": "hi", "type": "hindi"},
    {"bot": "Mokobara", "query": "कौन सा ब्रीफकेस बिज़नेस ट्रैवल के लिए अच्छा है?", "lang": "hi", "type": "hindi"},
    {"bot": "Mokobara", "query": "Does Mokobara offer a lifetime warranty on luggage?", "lang": "en", "type": "missing_info"},
    {"bot": "Mokobara", "query": "What is the capital of France?", "lang": "en", "type": "irrelevant"},
    {"bot": "Mokobara", "query": "How does the check-in medium compare to the large luggage?", "lang": "en", "type": "comparison"},
    {"bot": "Mokobara", "query": "What's in the Pac Kit and how do I use it?", "lang": "en", "type": "how_to"},

    # === Nicobar (en, hi, gu) ===
    {"bot": "Nicobar", "query": "What kurta sets do you have?", "lang": "en", "type": "product"},
    {"bot": "Nicobar", "query": "What is Nicobar and what kind of products do they sell?", "lang": "en", "type": "general"},
    {"bot": "Nicobar", "query": "क्या निकोबार पर साड़ी मिलती है?", "lang": "hi", "type": "hindi"},
    {"bot": "Nicobar", "query": "ઘર માટે કઈ પ્રોડક્ટ્સ છે?", "lang": "gu", "type": "gujarati"},
    {"bot": "Nicobar", "query": "Does Nicobar have a physical store in Delhi?", "lang": "en", "type": "missing_info"},
    {"bot": "Nicobar", "query": "How do I cook biryani?", "lang": "en", "type": "irrelevant"},
    {"bot": "Nicobar", "query": "What gift sets do you have compared to individual items?", "lang": "en", "type": "comparison"},
    {"bot": "Nicobar", "query": "How do I care for my Nicobar water hyacinth home product?", "lang": "en", "type": "how_to"},

    # === Plum Goodness (en) ===
    {"bot": "PlumGoodness", "query": "What dandruff control products does Plum have?", "lang": "en", "type": "product"},
    {"bot": "PlumGoodness", "query": "Is Plum Goodness really vegan and cruelty-free?", "lang": "en", "type": "general"},
    {"bot": "PlumGoodness", "query": "What's the difference between a hair conditioner and a hair mask?", "lang": "en", "type": "comparison"},
    {"bot": "PlumGoodness", "query": "How do I use the green tea CTMP routine?", "lang": "en", "type": "how_to"},
    {"bot": "PlumGoodness", "query": "Does Plum have anti-aging products for mature skin?", "lang": "en", "type": "missing_info"},
    {"bot": "PlumGoodness", "query": "Can you explain quantum physics?", "lang": "en", "type": "irrelevant"},
    {"bot": "PlumGoodness", "query": "What are some tips for faster hair growth?", "lang": "en", "type": "product"},
    {"bot": "PlumGoodness", "query": "How do I use the 1% Oat and Allantoin Nourishing Cream?", "lang": "en", "type": "how_to"},

    # === SlurrpFarm (en, hi, gu) ===
    {"bot": "SlurrpFarm", "query": "When is my baby ready to start solid foods?", "lang": "en", "type": "product"},
    {"bot": "SlurrpFarm", "query": "What is SlurrpFarm and what kind of food do they make?", "lang": "en", "type": "general"},
    {"bot": "SlurrpFarm", "query": "बच्चों के खाने में कौन से तेल और फैट्स अच्छे हैं?", "lang": "hi", "type": "hindi"},
    {"bot": "SlurrpFarm", "query": "બાળકોને ડેકેરમાં જમવાની આદત કેવી રીતે પાડવી?", "lang": "gu", "type": "gujarati"},
    {"bot": "SlurrpFarm", "query": "Does SlurrpFarm deliver outside India?", "lang": "en", "type": "missing_info"},
    {"bot": "SlurrpFarm", "query": "What is the best smartphone to buy in 2026?", "lang": "en", "type": "irrelevant"},
    {"bot": "SlurrpFarm", "query": "What's the difference between the Week 3 meal plan and Week 4?", "lang": "en", "type": "comparison"},
    {"bot": "SlurrpFarm", "query": "How do I make Sprouted Ragi Pongal for my baby?", "lang": "en", "type": "how_to"},

    # === TheManCompany (en, hi) ===
    {"bot": "TheManCompany", "query": "What grooming products does The Man Company sell?", "lang": "en", "type": "product"},
    {"bot": "TheManCompany", "query": "What is The Man Company all about?", "lang": "en", "type": "general"},
    {"bot": "TheManCompany", "query": "राखी पर भाई के लिए क्या गिफ्ट दे सकते हैं?", "lang": "hi", "type": "hindi"},
    {"bot": "TheManCompany", "query": "2020 में The Man Company ने क्या कहा था?", "lang": "hi", "type": "hindi"},
    {"bot": "TheManCompany", "query": "Does The Man Company offer a subscription box?", "lang": "en", "type": "missing_info"},
    {"bot": "TheManCompany", "query": "How do I fix a leaking kitchen faucet?", "lang": "en", "type": "irrelevant"},
    {"bot": "TheManCompany", "query": "What grooming products are best for summer vs winter?", "lang": "en", "type": "comparison"},
    {"bot": "TheManCompany", "query": "What does The Man Mag blog cover?", "lang": "en", "type": "how_to"},
]


def send_query(client, chatbot_id, message):
    """Send a query via the SSE streaming endpoint and collect the full response."""
    url = f"{BASE}/chat/{chatbot_id}/message/stream"
    
    try:
        with client.stream(
            "POST", url,
            data={"message": message, "is_preview": "true"},
            timeout=120.0,
        ) as response:
            if response.status_code != 200:
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}",
                    "content": "",
                    "sources": [],
                    "suggestions": [],
                    "products": [],
                }

            content_parts = []
            sources = []
            suggestions = []
            products = []
            session_id = None
            error = None

            for line in response.iter_lines():
                if not line.startswith("data: "):
                    continue
                data_str = line[6:]
                if data_str == "[DONE]":
                    break
                try:
                    d = json.loads(data_str)
                except json.JSONDecodeError:
                    continue

                msg_type = d.get("type", "")
                if msg_type == "content":
                    content_parts.append(d.get("content", ""))
                elif msg_type == "done":
                    sources = d.get("sources", [])
                    suggestions = d.get("suggestions", [])
                    products = d.get("products", [])
                elif msg_type == "session":
                    session_id = d.get("session_id", "")
                elif msg_type == "error":
                    error = d.get("error", "Unknown error")

            full_content = "".join(content_parts)
            if error:
                return {"status": "error", "error": error, "content": full_content, "sources": sources, "suggestions": suggestions, "products": products}
            return {"status": "success", "content": full_content, "sources": sources, "suggestions": suggestions, "products": products, "session_id": session_id}

    except Exception as e:
        return {"status": "error", "error": str(e), "content": "", "sources": [], "suggestions": [], "products": []}


def analyze_response(query_info, result):
    """Analyze a single response for quality."""
    checks = {
        "responded": False,
        "has_content": False,
        "content_length": 0,
        "has_sources": False,
        "has_suggestions": False,
        "has_products": False,
        "deflected_irrelevant": None,  # only checked for irrelevant type
        "admitted_limitation": None,   # only checked for missing_info type
        "used_correct_language": None, # only checked for hindi/gujarati
        "response_relevant": None,     # heuristic check
    }

    if result["status"] == "success" and result["content"]:
        checks["responded"] = True
        checks["has_content"] = True
        checks["content_length"] = len(result["content"])
        checks["has_sources"] = len(result.get("sources", [])) > 0
        checks["has_suggestions"] = len(result.get("suggestions", [])) > 0
        checks["has_products"] = len(result.get("products", [])) > 0

        content_lower = result["content"].lower()

        # Check irrelevant deflection
        if query_info["type"] == "irrelevant":
            deflection_signals = [
                "i can't help", "i cannot help", "outside my scope",
                "not related", "i'm not able", "i don't have information",
                "beyond my scope", "i'm here to help with",
                "i specialize in", "i can assist you with",
                "not something i can", "i'm designed to",
                "that's outside", "beyond what i", "out of scope",
                "don't have expertise", "not within my",
            ]
            checks["deflected_irrelevant"] = any(s in content_lower for s in deflection_signals)

        # Check missing info admission
        if query_info["type"] == "missing_info":
            limitation_signals = [
                "i don't have", "i'm not sure", "don't have specific",
                "not available", "couldn't find", "no information",
                "contact", "reach out", "check with",
                "don't have details", "unable to find",
                "not in my knowledge", "apologize",
                "sorry", "i couldn't locate",
            ]
            checks["admitted_limitation"] = any(s in content_lower for s in limitation_signals)

        # Check language for Hindi/Gujarati queries
        if query_info["type"] in ("hindi",):
            # Check for Devanagari characters
            has_devanagari = any("\u0900" <= ch <= "\u097F" for ch in result["content"])
            checks["used_correct_language"] = has_devanagari
        elif query_info["type"] in ("gujarati",):
            # Check for Gujarati characters
            has_gujarati = any("\u0A80" <= ch <= "\u0AFF" for ch in result["content"])
            checks["used_correct_language"] = has_gujarati

    elif result["status"] == "error":
        checks["responded"] = False

    return checks


def main():
    results = []
    client = httpx.Client(timeout=120.0)

    total = len(QUERIES)
    for i, q in enumerate(QUERIES):
        bot_name = q["bot"]
        bot_id = BOTS[bot_name]
        qtype = q["type"]
        lang = q["lang"]
        query_text = q["query"]

        print(f"[{i+1}/{total}] {bot_name} ({qtype}/{lang}): {query_text[:50]}...", flush=True)

        start = time.time()
        result = send_query(client, bot_id, query_text)
        elapsed = round(time.time() - start, 2)

        analysis = analyze_response(q, result)

        results.append({
            "index": i + 1,
            "bot": bot_name,
            "query": query_text,
            "type": qtype,
            "lang": lang,
            "status": result["status"],
            "error": result.get("error"),
            "content_preview": result["content"][:300] if result["content"] else "",
            "content_length": len(result["content"]) if result["content"] else 0,
            "num_sources": len(result.get("sources", [])),
            "num_suggestions": len(result.get("suggestions", [])),
            "num_products": len(result.get("products", [])),
            "elapsed_seconds": elapsed,
            "analysis": analysis,
        })

        # Small delay to avoid overloading
        time.sleep(0.5)

    client.close()

    # Write results
    with open("/tmp/test_results.json", "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nDone! {len(results)} queries completed. Results saved to /tmp/test_results.json")

    # Quick summary
    successes = sum(1 for r in results if r["status"] == "success")
    errors = sum(1 for r in results if r["status"] == "error")
    avg_time = sum(r["elapsed_seconds"] for r in results) / len(results) if results else 0
    print(f"  Success: {successes}/{total}")
    print(f"  Errors: {errors}/{total}")
    print(f"  Avg response time: {avg_time:.1f}s")

    # Type-level summary
    from collections import defaultdict
    by_type = defaultdict(list)
    for r in results:
        by_type[r["type"]].append(r)

    for qtype, items in sorted(by_type.items()):
        ok = sum(1 for i in items if i["analysis"]["responded"])
        total_t = len(items)
        
        extra = ""
        if qtype == "irrelevant":
            deflected = sum(1 for i in items if i["analysis"].get("deflected_irrelevant"))
            extra = f" | deflected: {deflected}/{total_t}"
        elif qtype == "missing_info":
            admitted = sum(1 for i in items if i["analysis"].get("admitted_limitation"))
            extra = f" | admitted: {admitted}/{total_t}"
        elif qtype in ("hindi", "gujarati"):
            correct_lang = sum(1 for i in items if i["analysis"].get("used_correct_language"))
            extra = f" | correct_lang: {correct_lang}/{total_t}"
        
        print(f"  {qtype:15} → {ok}/{total_t} responded{extra}")


if __name__ == "__main__":
    main()
