# IRRELEVANT Tag Test Report — V9

**Date:** 2026-02-23  
**Queries tested:** 42 (across 6 bots, 3 languages)  
**Valid tests:** 36 (6 correctly rejected as unsupported language)  
**Detection rate:** 9/36 = **25%**

---

## Current Algorithm: How `[[IRRELEVANT]]` Tag Works

### Step-by-step flow in `chat_service.py`:

```
User query
    │
    ▼
[Call 1] — Unified query analysis (LLM)
    │  Outputs: lang, is_product_request, retrieval_query
    │
    ▼
[Embedding search] — Finds top-N similar chunks
    │  Outputs: sources[], retrieval_confidence (0.0–1.0)
    │
    ▼
[Cross-encoder reranker] — Re-scores & filters chunks
    │
    ▼
[Product extraction] — If is_product_request: extract products from product URLs
    │
    ▼
[Out-of-scope detection] ← FIRST GATE
    │  IF is_product_request AND products > 0:
    │      is_likely_out_of_scope = False  (always treated as in-scope)
    │  ELSE:
    │      is_likely_out_of_scope = (confidence < 0.35) AND (not greeting) AND (sources > 0)
    │
    ▼
[Build system prompt for Call 2] — includes:
    │  - Rule 3: "For completely unrelated topics → DO NOT answer, append [[IRRELEVANT]]"
    │  - Exception: "Only suppress [[IRRELEVANT]] when user genuinely asks about brand's
    │    own products AND matching products exist..."
    │  - If is_likely_out_of_scope: adds hint "[SCOPE WARNING] confidence is very low"
    │  - product_carousel_instruction: conditional on is_product_request
    │      if is_product_request → "DO NOT mark [[IRRELEVANT]]"
    │      else → "products appeared due to keyword/price overlap, STILL mark [[IRRELEVANT]]"
    │
    ▼
[Call 2] — LLM generates response (streaming)
    │  LLM may or may not include [[IRRELEVANT]] in response text
    │
    ▼
[Post-processing]
    │  is_irrelevant = "[[IRRELEVANT]]" in full_content   ← extracted from response text
    │  is_missing_info = "[[MISSING_INFO]]" in full_content
    │
    │  Override: if is_irrelevant AND products AND is_product_request:
    │      is_irrelevant = False  (only for genuine product requests)
    │
    ▼
[Done event]
    │  products = [] if is_irrelevant else products  ← products suppressed when irrelevant
    │  Cache: skipped if is_irrelevant
    │
    ▼
[DB save]
    │  metadata_json: { is_irrelevant, was_answered, retrieval_confidence, ... }
```

### Key decision points:
1. **`is_likely_out_of_scope` gate** — Only triggers when `retrieval_confidence < 0.35`. If embeddings return high similarity (keyword overlap), this gate never fires.
2. **LLM judgment** — The system prompt tells the LLM to mark `[[IRRELEVANT]]`, but the LLM must voluntarily include it in its response text.
3. **Post-processing override** — Only overrides `is_irrelevant=False` when `is_product_request=True` (prevents clearing the flag for price-matched products on non-product queries).

---

## Test Results: Per-Query Analysis

### Legend
- ✅ **PASS** — `is_irrelevant=true` in DB, 0 products, correct language
- ❌ **FAIL** — `is_irrelevant=false` (bot didn't reject the query)
- ⚠️ — Partial (text redirects but tag not set, or products leaked)

---

### Tentree (eco-friendly clothing: t-shirts, hoodies, jackets, joggers)

| # | Lang | Query | is_irrelevant | Confidence | Products | Response Preview | Status |
|---|------|-------|--------------|------------|----------|-----------------|--------|
| 1 | en | What's the best way to invest money in the stock market? | **true** | 0.238 | 0 | "I can only help with Crawl-Tentree products." | ✅ |
| 2 | en | Can you recommend a good laptop for programming? | false | 0.153 | **8** | "Here are some great options from Crawl-Tentree..." + 8 products (backpacks, sweaters) | ❌ |
| 3 | en | How do I treat a migraine headache naturally? | false | 0.423 | 0 | "Hmm, let me check... Unfortunately, I don't have that information" | ❌ |
| 4 | hi | शेयर बाज़ार में पैसे कैसे लगाएं? | false | 0.445 | **10** | "यहाँ कुछ बढ़िया ऑप्शन हैं! शेयर बाज़ार में पैसे लगाने के लिए..." — HALLUCINATED investment advice + 10 products | ❌❌ |
| 5 | hi | घर पर बिरयानी कैसे बनाएं? | false | 0.417 | 0 | "अरे, यहाँ बिरयानी बनाने की जानकारी नहीं है! हमारे पास..." — partial redirect | ⚠️ |
| 6 | hi | क्रिकेट विश्वकप में कौन सी टीम जीतेगी? | **true** | 0.0 | 0 | "अरे, यह तो भविष्यवाणी का मामला है! मैं क्रिकेट विश्वकप के बारे में जानकारी नहीं दे सकता" | ✅ |
| 7 | gu | શેરબજારમાં કેવી રીતે રોકાણ કરવું? | false | 0.45 | 0 | "ઓહ, શેરબજારમાં રોકાણ કરવા માટે ઘણી બાબતો..." — ANSWERED with investment advice | ❌ |
| 8 | gu | ઘર પર બિરિયાની કેવી રીતે બનાવવી? | false | 0.417 | 0 | "અરે, બિરિયાની બનાવવાની રીત ખૂબ જ સરળ છે!" — ANSWERED with full recipe | ❌ |
| 9 | gu | ક્રિકેટ વિશ્વ કપ માટે કઈ ટીમ જીતશે? | false | 0.0 | 0 | "અરે...આ વિષય અમારા Crawl-Tentree પ્રોડક્ટ્સ સાથે સંબંધિત નથી." — redirects but NO tag | ⚠️ |

**Tentree: 2/9 PASS (22%)**

---

### Death Wish Coffee (coffee beans, blends, merchandise)

| # | Lang | Query | is_irrelevant | Confidence | Products | Response Preview | Status |
|---|------|-------|--------------|------------|----------|-----------------|--------|
| 10 | en | What's the best programming language for beginners? | **true** | 0.157 | 0 | "I can only help with Crawl-Death Wish Coffee products." | ✅ |
| 11 | en | Recommend me a good sports car under 50000 dollars | false | 0.258 | **10** | "I can only help with Crawl-Death Wish Coffee products." — text redirects but 10 products leaked | ⚠️ |
| 12 | en | How do I lose weight effectively in 30 days? | false | 0.498 | 0 | "Losing weight in 30 days can be challenging, but..." — ANSWERED with diet advice | ❌ |
| 13 | hi | शुरुआती लोगों के लिए सबसे अच्छी प्रोग्रामिंग भाषा कौन सी है? | false | 0.421 | 0 | "अरे, यह एक अच्छा सवाल है! लेकिन...यह प्रोग्रामिंग से जुड़ा है" — partial redirect, NO tag | ⚠️ |
| 14 | hi | घर पर माइग्रेन का इलाज कैसे करें? | false | 0.721 | 0 | "अरे, माइग्रेन का इलाज करना थोड़ा मुश्किल...लेकिन कॉफी से मदद मिल सकती है!" — CONNECTED coffee to migraine | ❌❌ |
| 15 | hi | भारत में खरीदने के लिए सबसे अच्छी कार कौन सी है? | false | 0.782 | **10** | "यहाँ कुछ बढ़िया ऑप्शन हैं! देखो Crawl-Death Wish Coffee..." + 10 products for a car question | ❌❌ |

**DWC: 1/6 PASS (17%)**

---

### Beardbrand (beard grooming: beard oil, balm, grooming kits)

| # | Lang | Query | is_irrelevant | Confidence | Products | Response Preview | Status |
|---|------|-------|--------------|------------|----------|-----------------|--------|
| 16 | en | Which tech stocks should I invest in right now? | false | 0.651 | **1** | "Here are some great options from Crawl-Beardbrand..." + 1 product for a stock market question | ❌ |
| 17 | en | Suggest a good weight loss diet plan for men | **true** | 0.824 | 0 | "I can only help with Crawl-Beardbrand products." | ✅ |
| 18 | en | Best countries to visit for solo travel? | **true** | 0.602 | 0 | "I can only help with Crawl-Beardbrand products." | ✅ |
| 19 | gu | કયા ટેક્નોલોજી શેરો ખરીદવા જોઈએ? | false | 0.57 | **1** | "અહીં કેટલાક સરસ ઓપ્શન છે! જુઓ Crawl-Beardbrand..." + 1 product | ❌ |
| 20 | gu | વજન ઘટાડવા માટે શ્રેષ્ઠ ડાઇટ કઈ છે? | false | 0.352 | 0 | "ઓહ, તમે વજન ઘટાડવા માટે ડાઇટ...દુર્ભાગ્યે, આ વિષય અમારા ઉત્પાદનો સાથે સંબંધિત નથી." — redirects but NO tag | ⚠️ |
| 21 | gu | એકલા પ્રવાસ માટે સૌથી સારો દેશ કયો છે? | false | 0.0 | 0 | "...દુર્ભાગ્યે, હું ફક્ત Crawl-Beardbrand પ્રોડક્ટ્સ વિશે જ માહિતી આપી શકું" — redirects but NO tag | ⚠️ |

**Beardbrand: 2/6 PASS (33%)**

---

### Ramraj (traditional Indian clothing: dhoti, shirts, kurta)

| # | Lang | Query | is_irrelevant | Confidence | Products | Response Preview | Status |
|---|------|-------|--------------|------------|----------|-----------------|--------|
| 22 | hi | आर्टिफिशियल इंटेलिजेंस के क्या फायदे हैं? | false | 0.337 | 0 | "अरे, यहाँ तो हम ramraj के products की बात कर रहे हैं!" — redirects but NO tag | ⚠️ |
| 23 | hi | अगले चुनाव में कौन सी पार्टी जीतेगी? | false | 0.596 | 0 | "अरे, यह तो भविष्य की बात है! मैं यहाँ ramraj के प्रोडक्ट्स..." — redirects but NO tag | ⚠️ |
| 24 | hi | बच्चों के लिए सबसे अच्छा स्कूल बोर्ड कौन सा है? | false | 0.727 | **10** | "अरे, यहाँ कुछ बढ़िया ऑप्शन हैं! देखो ramraj के पास..." + 10 products for a school question | ❌❌ |
| 25 | gu | આર્ટિફિશિયલ ઇન્ટેલિજન્સના ફાયદા શું છે? | **true** | 0.337 | 0 | "...આ વિષય અહીં નથી" — correctly tagged | ✅ |
| 26 | gu | આગામી ચૂંટણીમાં કઈ પાર્ટી જીતશે? | false | 0.63 | 0 | "ઓહો, આ એક ખૂબ રસપ્રદ પ્રશ્ન છે! પરંતુ...હું ફક્ત Ramraj ના પ્રોડક્ટ્સ..." — redirects but NO tag | ⚠️ |
| 27 | gu | બાળકો માટે કઈ સ્કૂલ બોર્ડ સૌથી સારી છે? | false | 0.516 | 0 | "અરે, એમાં ઘણી વિકલ્પો છે! પણ તમે રમરાજ વિશે..." — starts to answer | ❌ |

**Ramraj: 1/6 PASS (17%)**

---

### Kriyanta (gifts, home decor, accessories, stationery)

| # | Lang | Query | is_irrelevant | Confidence | Products | Response Preview | Status |
|---|------|-------|--------------|------------|----------|-----------------|--------|
| 28 | en | What's the best recipe for dal makhani? | **true** | 0.0 | 0 | "I can only help with kriyanta products." | ✅ |
| 29 | en | How do I lose weight fast in one month? | **true** | 0.0 | 0 | "I can only help with kriyanta products." | ✅ |
| 30 | en | Which mutual funds should I invest in for long term? | false | 0.529 | **4** | "I can only help with kriyanta products." — text redirects but 4 products leaked | ⚠️ |
| 31 | gu | દાળ મખનીની રેસિપી શું છે? | — | — | 0 | "Gujarati is not supported for this chatbot" | N/A |
| 32 | gu | ત્રીસ દિવસમાં વજન કેવી રીતે ઘટાડવું? | — | — | 0 | "Gujarati is not supported for this chatbot" | N/A |
| 33 | gu | સૌથી સારા મ્યુચ્યુઅલ ફંડ કયા છે? | — | — | 0 | "Gujarati is not supported for this chatbot" | N/A |

**Kriyanta: 2/3 valid PASS (67%)** — Gu queries correctly rejected by language filter

---

### Zevaramaze (jewelry: bracelets, necklaces, rings, earrings, pendants)

| # | Lang | Query | is_irrelevant | Confidence | Products | Response Preview | Status |
|---|------|-------|--------------|------------|----------|-----------------|--------|
| 34 | en | How do I start a vegetable garden at home? | false | 0.0 | 0 | "Starting a vegetable garden at home sounds like a great idea! You'll need..." — ANSWERED fully | ❌ |
| 35 | en | What is the weather forecast for tomorrow? | **true** | 0.0 | 0 | "I can only help with zevaramaze products." | ✅ |
| 36 | en | Recommend some good Gujarati movies to watch | false | 0.0 | 0 | "અરે, ગુજરાતી ફિલ્મો ઘણી સારી છે!" — ANSWERED in Gujarati (wrong lang!) + gave movie recommendations | ❌❌ |
| 37 | hi | घर पर सब्जियों का बगीचा कैसे लगाएं? | — | — | 0 | "Hindi is not supported for this chatbot" | N/A |
| 38 | hi | कल का मौसम कैसा रहेगा? | — | — | 0 | "Hindi is not supported for this chatbot" | N/A |
| 39 | hi | कुछ अच्छी गुजराती फिल्में बताएं | — | — | 0 | "Hindi is not supported for this chatbot" | N/A |
| 40 | gu | ઘર પર શાકભાજીની ખેતી કેવી રીતે કરવી? | false | 0.0 | 0 | "ઓહો, ઘર પર શાકભાજીની ખેતી કરવી એ ખૂબ સરળ છે!" — ANSWERED with farming advice | ❌ |
| 41 | gu | આવતીકાલ નું હવામાન કેવું રહેશે? | false | 0.0 | 0 | "અરે, માહિતી નથી! હવામાન વિશે મારી પાસે કોઈ ડેટા નથી." — redirects but NO tag | ⚠️ |
| 42 | gu | જોવા જેવી ગુજરાતી ફિલ્મ કઈ છે? | false | 0.0 | 0 | "અરે, ઘણી સારી ગુજરાતી ફિલ્મો છે!" — ANSWERED with movie recommendations | ❌ |

**Zevaramaze: 1/6 valid PASS (17%)**

---

## Summary Table

| Bot | Valid Tests | Passed | Failed | Pass Rate |
|-----|-----------|--------|--------|-----------|
| Tentree | 9 | 2 | 7 | 22% |
| DWC | 6 | 1 | 5 | 17% |
| Beardbrand | 6 | 2 | 4 | 33% |
| Ramraj | 6 | 1 | 5 | 17% |
| Kriyanta | 3 | 2 | 1 | 67% |
| Zevaramaze | 6 | 1 | 5 | 17% |
| **TOTAL** | **36** | **9** | **27** | **25%** |

### By Language

| Language | Tested | Passed | Rate |
|----------|--------|--------|------|
| English | 18 | 8 | **44%** |
| Hindi | 9 | 1 | **11%** |
| Gujarati | 9 | 1 | **11%** |

---

## Failure Categories

### Category 1: LLM Answers the Irrelevant Question (10 cases) — WORST
The bot provides actual answers to completely off-domain questions.

| Query | Bot | What Happened |
|-------|-----|--------------|
| शेयर बाज़ार में पैसे कैसे लगाएं? | Tentree | Gave investment advice + 10 clothing products |
| ઘર પર બિરિયાની કેવી રીતે બનાવવી? | Tentree | Gave full biryani recipe |
| શેરબજારમાં કેવી રીતે રોકાણ કરવું? | Tentree | Gave investment advice |
| How do I lose weight effectively in 30 days? | DWC | Gave weight loss tips |
| घर पर माइग्रेन का इलाज कैसे करें? | DWC | Connected coffee to migraine cure |
| બાળકો માટે કઈ સ્કૂલ બોર્ડ સૌથી સારી છે? | Ramraj | Started answering about school boards |
| How do I start a vegetable garden at home? | Zevaramaze | Gave full gardening guide |
| ઘર પર શાકભાજીની ખેતી કેવી રીતે કરવી? | Zevaramaze | Gave farming advice |
| Recommend some good Gujarati movies | Zevaramaze | Recommended movies (in wrong lang!) |
| જોવા જેવી ગુજરાતી ફિલ્મ કઈ છે? | Zevaramaze | Recommended movies |

### Category 2: Text Redirects But No `[[IRRELEVANT]]` Tag (9 cases) — Partial
The bot correctly says "I can only help with X" or "this is not related" but FORGETS to append `[[IRRELEVANT]]`.

| Query | Bot | Response |
|-------|-----|----------|
| ક્રિકેટ વિશ્વ કપ માટે કઈ ટીમ જીતશે? | Tentree | "આ વિષય અમારા...સંબંધિત નથી" (no tag) |
| घर पर बिरयानी कैसे बनाएं? | Tentree | "यहाँ बिरयानी बनाने की जानकारी नहीं है!" (no tag) |
| Recommend me a good sports car under 50000 dollars | DWC | "I can only help with..." (no tag, but 10 products!) |
| शुरुआती...प्रोग्रामिंग भाषा कौन सी है? | DWC | "लेकिन...यह प्रोग्रामिंग से जुड़ा है" (no tag) |
| આર્ટિફિશિયલ ઇન્ટેલિજન્સના ફાયદા | Ramraj(hi) | "यहाँ तो हम ramraj के products..." (no tag) |
| અગલે ચુનાવ મેં | Ramraj(hi) | "यह तो भविष्य की बात है!" (no tag) |
| આગામી ચૂંટણીમાં | Ramraj(gu) | "મારી પાસે આનો જવાબ નથી" (no tag) |
| વજન ઘટાડવા | Beardbrand(gu) | "આ વિષય અમારા ઉત્પાદનો સાથે સંબંધિત નથી" (no tag) |
| એકલા પ્રવાસ | Beardbrand(gu) | "હું ફક્ત Crawl-Beardbrand..." (no tag) |

### Category 3: Product Leakage on Irrelevant Queries (8 cases)
Products returned even though the query is completely off-domain.

| Query | Bot | Products | Cause |
|-------|-----|----------|-------|
| "laptop for programming" | Tentree | 8 (backpacks, sweaters) | "laptop" keyword matched "laptop bag" descriptions |
| "शेयर बाज़ार में पैसे" | Tentree | 10 | Price terms in translated query |
| "sports car under $50000" | DWC | 10 | Price "$50000" triggered price filter |
| "best car to buy in India" | DWC | 10 | High conf=0.782, keyword overlap |
| "tech stocks invest" | Beardbrand | 1 | "Stock" keyword matched a product |
| "tech stocks" (gu) | Beardbrand | 1 | Same keyword match |
| "school board" | Ramraj | 10 | "board" keyword overlap, conf=0.727 |
| "mutual funds invest" | Kriyanta | 4 | Price-related terms |

---

## Why Detection Fails: Root Cause Analysis

### Root Cause 1: `is_likely_out_of_scope` Threshold Too Strict
```python
# Line ~3440 in chat_service.py
is_likely_out_of_scope = (
    retrieval_confidence < 0.35   # ← Only fires at very low confidence
    and not is_greeting
    and sources_count > 0
)
```
**Problem:** Many irrelevant queries get `confidence > 0.35` because:
- "stock market" → "in Stock" (product availability text) → conf=0.65
- "school board" → "board" appears in product descriptions → conf=0.73
- "migraine" → "headache relief" or health-adjacent text → conf=0.72
- "car" → "cart" or shipping text → conf=0.78

When `is_likely_out_of_scope=False`, the LLM doesn't receive the `[SCOPE WARNING]` hint, making it much less likely to mark `[[IRRELEVANT]]`.

### Root Cause 2: LLM Doesn't Self-Tag in Non-English
Even with clear system prompt instructions:
> "This applies IN ALL LANGUAGES — Hindi, Gujarati, English, or any language."

The LLM:
- **In English**: Uses the trained irrelevant template → "I can only help with X products" + `[[IRRELEVANT]]` (50% rate)
- **In Hindi/Gujarati**: Tries to be conversational/helpful, gives partial answers or writes redirect text WITHOUT the `[[IRRELEVANT]]` tag (11% rate)

**Evidence:** 9 cases where the LLM wrote correct redirect text but forgot `[[IRRELEVANT]]` — all in Hindi/Gujarati.

### Root Cause 3: Call1 Price-Matching Creates False Product Results
When Call1 sees "$50000" or "₹30000" in queries like "sports car under $50000", it may extract a price filter. Product extraction then returns products matching that price range from the bot's catalog — creating a false impression that the query is relevant.

### Root Cause 4: High Confidence = LLM Trusts Context
When retrieval confidence is high (0.5+), the LLM receives many context chunks that SEEM related due to keyword overlap. It then:
1. Assumes the context is relevant
2. Tries to "connect" the query to the brand (e.g., "coffee can help with migraines!")
3. Provides an answer instead of declining

---

## Queries Where Detection SUCCEEDED (Pattern Analysis)

| Query | Confidence | Why It Worked |
|-------|-----------|---------------|
| en "invest in stock market" | 0.238 | Low conf → scope warning fired |
| hi "cricket world cup" | 0.0 | Zero conf → scope warning fired |
| en "programming language" | 0.157 | Low conf → scope warning fired |
| en "diet plan for men" | 0.824 | High conf BUT LLM independently recognized off-domain |
| en "solo travel" | 0.602 | LLM independently recognized off-domain |
| gu "AI benefits" | 0.337 | Borderline conf → scope warning may have fired |
| en "dal makhani recipe" | 0.0 | Zero conf → scope warning fired |
| en "weight loss" | 0.0 | Zero conf → scope warning fired |
| en "weather forecast" | 0.0 | Zero conf → scope warning fired |

**Pattern:** 7/9 successes had confidence < 0.35 (scope warning fired). Only 2/9 succeeded with high confidence (both English).
