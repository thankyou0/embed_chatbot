"""
Post-Humanization-Fix Test V2
Tests:
1. Return policy on Tentree (was wrongly out-of-scope)
2. Missing info responses (should be warm + suggest alternatives)
3. Scope-gate responses (should be humanized)
4. Tricky irrelevant queries designed to fool bots
"""
import httpx
import json
import time
import re

BASE_URL = "http://localhost:8000/api/v1"
AUTH = {"email": "max@gmail.com", "password": "12345678"}

BOTS = {
    "Tentree":       "799637f9-391b-4b9d-84cb-5fdd17cdf109",
    "DeathWish":     "99fc3604-99e7-4cd0-a2a6-509ac08d9fd0",
    "Beardbrand":    "e23fcc6f-7a02-4b09-8d49-95c00a57d852",
    "Ramraj":        "182f88cd-02d8-4c94-824d-b41432847400",
    "Kriyanta":      "1cb18dc0-4909-409d-ab03-0436524fcec4",
    "Zevaramaze":    "e79b3754-006d-45d5-b21d-2391710e08ca",
}

# ─── Tricky irrelevant queries designed to fool bots ───
# These are crafted to sound product-adjacent or use brand-specific keywords
TRICKY_IRRELEVANT = {
    "Tentree": [
        "How many trees are there in the Amazon rainforest?",                  # "trees" sounds related to Tentree
        "What's the carbon footprint of a Tesla Model 3?",                     # sustainability-adjacent but unrelated
        "Can you recommend a good sustainable investing app?",                 # sustainability keyword overlap
        "How do I grow a tree in my backyard?",                                # "tree" keyword overlap
        "What's the environmental impact of Bitcoin mining?",                  # eco topic but irrelevant
    ],
    "DeathWish": [
        "What are the side effects of drinking too much caffeine?",            # coffee-adjacent medical advice
        "How do you roast coffee beans at home?",                              # coffee topic but not about their products
        "Is caffeine good for weight loss?",                                   # caffeine-related health question
        "What's the strongest coffee brand in the world?",                     # competitive question
        "Can coffee cause heart attacks?",                                     # medical + coffee keyword
    ],
    "Beardbrand": [
        "How fast does facial hair grow?",                                     # beard-adjacent biology question
        "What causes patchy beard growth?",                                    # dermatology but beard-related
        "Can minoxidil help grow a beard?",                                    # beard growth medical advice
        "Who has the longest beard in the world?",                             # beard trivia
        "How do I shave without getting razor bumps?",                         # grooming but about shaving, not beard care
    ],
    "Ramraj": [
        "What's the history of cotton farming in Tamil Nadu?",                 # cotton-adjacent history
        "How is silk different from cotton?",                                  # textile question
        "What's the best way to remove stains from white cotton clothes?",     # cotton laundry advice
        "Who invented the dhoti?",                                             # dhoti trivia
        "What is the GST rate on clothing in India?",                          # tangential policy question
    ],
    "Kriyanta": [
        "How do I do home interior design on a budget?",                       # home décor adjacent but generic advice
        "What's the difference between MDF and solid wood?",                   # material knowledge
        "How do I hang a heavy mirror on drywall?",                            # home improvement DIY
        "What are the latest home décor trends for 2025?",                     # home décor but trend advice
        "Can you suggest a good interior designer in Mumbai?",                 # home décor but external recommendation
    ],
    "Zevaramaze": [
        "સોનું અને ચાંદી માં શું ફરક છે?",                                    # "What's the diff between gold and silver?" - jewellery-adjacent
        "ચાંદી ની કિંમત આજે શું છે?",                                         # "What's today's silver price?" - silver keyword
        "હીરા ક્યાંથી આવે છે?",                                               # "Where do diamonds come from?" - jewellery trivia
        "ચાંદી ને કેવી રીતે સાફ કરવી?",                                       # "How to clean silver?" - silver care advice
        "સોના માં રોકાણ કરવું સારું છે?",                                      # "Is it good to invest in gold?" - investment
    ],
}

# ─── Previously-failing queries that should now work ───
SHOULD_WORK = {
    "Tentree": [
        ("What is your return policy?", "return_policy"),
        ("Do you ship internationally?", "shipping"),
        ("What makes Tentree different from other brands?", "brand_info"),
    ],
    "DeathWish": [
        ("What is your return policy?", "return_policy"),
        ("How should I store my coffee?", "product_care"),
    ],
    "Ramraj": [
        ("क्या return policy है?", "return_policy_hi"),
    ],
    "Zevaramaze": [
        ("રિટર્ન પોલિસી શું છે?", "return_policy_gu"),
    ],
}

# ─── Missing info queries (should get warm, helpful response) ───
MISSING_INFO = {
    "Tentree": [
        "What is your CEO's phone number?",
        "Where is your warehouse located?",
    ],
    "DeathWish": [
        "What certifications do your products have?",
    ],
    "Kriyanta": [
        "Do you offer a lifetime warranty?",
    ],
}


def login():
    r = httpx.post(f"{BASE_URL}/auth/login", json=AUTH, timeout=10)
    r.raise_for_status()
    return r.json()["access_token"]


def stream_chat(token, bot_id, message, session_id=None):
    url = f"{BASE_URL}/chat/{bot_id}/message/stream"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"message": message}
    if session_id:
        data["session_id"] = session_id

    text = ""
    new_session_id = None
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
                    new_session_id = evt.get("session_id")
    return text.strip(), new_session_id


def main():
    token = login()
    print("=" * 80)
    print("POST-HUMANIZATION FIX TEST V2")
    print("=" * 80)

    results = {
        "tricky_irrelevant": {"total": 0, "correctly_rejected": 0, "failures": []},
        "should_work": {"total": 0, "passed": 0, "failures": []},
        "missing_info": {"total": 0, "humanized": 0, "bare": []},
    }

    # ─── PART 1: Tricky irrelevant queries ───
    print("\n" + "=" * 60)
    print("PART 1: TRICKY IRRELEVANT QUERIES")
    print("=" * 60)
    for bot_name, queries in TRICKY_IRRELEVANT.items():
        bot_id = BOTS[bot_name]
        print(f"\n--- {bot_name} ---")
        for q in queries:
            results["tricky_irrelevant"]["total"] += 1
            try:
                resp, _ = stream_chat(token, bot_id, q)
                # Detection: scope gate strips [[IRRELEVANT]] before streaming,
                # so also check for the humanized rejection message patterns
                is_rejected = (
                    "[[IRRELEVANT]]" in resp
                    or "outside my expertise" in resp.lower()
                    or "scope" in resp.lower() and ("bahar" in resp.lower() or "બહાર" in resp.lower() or "बाहर" in resp.lower())
                    or "only help with" in resp.lower()
                    or "I can only" in resp.lower()
                    or "fakat" in resp.lower() and "madad" in resp.lower()
                    or "केवल" in resp and "मदद" in resp
                    or "ફક્ત" in resp and "મદદ" in resp
                )
                is_humanized = any(w in resp.lower() for w in ["oops", "😅", "expertise", "outside", "अरे", "scope", "bahar", "બહાર"])
                marker = "✅" if is_rejected else "❌"
                human = " 😊" if is_humanized else ""

                clean = resp.replace("[[IRRELEVANT]]", "").replace("[[MISSING_INFO]]", "").strip()
                print(f"  {marker}{human} Q: {q[:60]}")
                print(f"       A: {clean[:120]}")

                if is_rejected:
                    results["tricky_irrelevant"]["correctly_rejected"] += 1
                else:
                    results["tricky_irrelevant"]["failures"].append({
                        "bot": bot_name, "query": q, "response": clean[:200]
                    })
            except Exception as e:
                print(f"  ⚠️ ERROR: {e}")
            time.sleep(0.3)

    # ─── PART 2: Previously-failing queries (return policy etc) ───
    print("\n" + "=" * 60)
    print("PART 2: SHOULD-WORK QUERIES (return policy, shipping, brand)")
    print("=" * 60)
    for bot_name, queries in SHOULD_WORK.items():
        bot_id = BOTS[bot_name]
        print(f"\n--- {bot_name} ---")
        for q, qtype in queries:
            results["should_work"]["total"] += 1
            try:
                resp, _ = stream_chat(token, bot_id, q)
                is_rejected = "[[IRRELEVANT]]" in resp
                is_scope_gated = "scope" in resp.lower() or "only help with" in resp.lower()
                passed = not is_rejected and not is_scope_gated
                marker = "✅" if passed else "❌"
                clean = resp.replace("[[IRRELEVANT]]", "").replace("[[MISSING_INFO]]", "").strip()
                print(f"  {marker} [{qtype}] Q: {q}")
                print(f"       A: {clean[:150]}")

                if passed:
                    results["should_work"]["passed"] += 1
                else:
                    results["should_work"]["failures"].append({
                        "bot": bot_name, "query": q, "type": qtype, "response": clean[:200]
                    })
            except Exception as e:
                print(f"  ⚠️ ERROR: {e}")
            time.sleep(0.3)

    # ─── PART 3: Missing info queries (humanization check) ───
    print("\n" + "=" * 60)
    print("PART 3: MISSING INFO RESPONSES (humanization check)")
    print("=" * 60)
    for bot_name, queries in MISSING_INFO.items():
        bot_id = BOTS[bot_name]
        print(f"\n--- {bot_name} ---")
        for q in queries:
            results["missing_info"]["total"] += 1
            try:
                resp, _ = stream_chat(token, bot_id, q)
                clean = resp.replace("[[MISSING_INFO]]", "").replace("[[IRRELEVANT]]", "").strip()
                # Check if response is bare (just "I don't have that information") vs helpful
                is_bare = len(clean) < 60 and ("don't have" in clean.lower() or "not available" in clean.lower())
                has_suggestion = any(w in clean.lower() for w in [
                    "website", "support", "reach out", "contact", "check", "help you with",
                    "can tell you", "instead", "but", "however", "alternatively"
                ])
                is_humanized = not is_bare or has_suggestion
                marker = "😊" if is_humanized else "🤖"
                print(f"  {marker} Q: {q}")
                print(f"       A: {clean[:200]}")

                if is_humanized:
                    results["missing_info"]["humanized"] += 1
                else:
                    results["missing_info"]["bare"].append({
                        "bot": bot_name, "query": q, "response": clean[:200]
                    })
            except Exception as e:
                print(f"  ⚠️ ERROR: {e}")
            time.sleep(0.3)

    # ─── SUMMARY ───
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    tr = results["tricky_irrelevant"]
    sw = results["should_work"]
    mi = results["missing_info"]

    print(f"\n🎯 Tricky Irrelevant: {tr['correctly_rejected']}/{tr['total']} correctly rejected "
          f"({100 * tr['correctly_rejected'] / max(tr['total'], 1):.0f}%)")
    if tr["failures"]:
        print(f"   ❌ Failures ({len(tr['failures'])}):")
        for f in tr["failures"]:
            print(f"      - [{f['bot']}] {f['query'][:70]}")

    print(f"\n✅ Should-Work: {sw['passed']}/{sw['total']} passed")
    if sw["failures"]:
        print(f"   ❌ Failures ({len(sw['failures'])}):")
        for f in sw["failures"]:
            print(f"      - [{f['bot']}] {f['query'][:70]} → {f['response'][:80]}")

    print(f"\n😊 Missing Info Humanization: {mi['humanized']}/{mi['total']} humanized")
    if mi["bare"]:
        print(f"   🤖 Bare responses ({len(mi['bare'])}):")
        for f in mi["bare"]:
            print(f"      - [{f['bot']}] {f['query'][:70]} → {f['response'][:80]}")

    total_score = tr["correctly_rejected"] + sw["passed"] + mi["humanized"]
    total_max = tr["total"] + sw["total"] + mi["total"]
    print(f"\n{'='*60}")
    print(f"OVERALL: {total_score}/{total_max} ({100 * total_score / max(total_max, 1):.0f}%)")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
