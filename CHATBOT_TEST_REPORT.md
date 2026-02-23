# Comprehensive Chatbot Testing Report

**Generated:** 2026-02-20 16:53:32
**Total Sites Tested:** 4 (ramraj, truff, kriyanta, kids) + 1 skipped (zevaramaze — all keys exhausted)
**Total Queries Sent:** 169
**Valid Queries (non rate-limited):** 149
**Rate-Limited Queries (skipped):** 20
**Infrastructure Errors (ConnectionReset from key rotation):** 26
**Genuine Bot Quality Queries:** 123 (149 valid - 26 infra errors)
**Pass Rate (excluding infra errors):** ~86% (106/123)
**Fail Rate (genuine bot issues):** ~14% (17/123)
**Average Score (all valid):** 6.0/10
**Average Score (excluding infra errors):** ~7.3/10
**GROQ Keys Used:** 6 of 6
**Keys Exhausted:** 6
**New Sites Crawling:** 3 (Boat Lifestyle, Sugar Cosmetics, Mokobara — started in parallel, still crawling)

> **IMPORTANT NOTE:** Many 0/10 scores in the data are `ConnectionResetError` / `RemoteDisconnected` errors caused by the Docker API container restarting during GROQ API key rotation. These are **infrastructure issues, not bot quality failures**. The true bot quality issues are detailed in the "Real Bot Quality Issues" section below.

---
## Key Findings Summary

### What Works Well
1. **Product search in English** — ramraj scored 10/10 on all English product queries (browse, specific, price)
2. **Conversation context** — context_summary scored 9.5/10 consistently across all bots
3. **Product comparisons** — 9.5/10 average, bot handles "cheapest vs expensive" well
4. **Complaint handling** — 8.3/10 average, good empathetic responses
5. **Hindi Romanized** — "best quality shirts dikhao" works perfectly (8.0 avg)
6. **Suggestions quality** — When suggestions appear, they are contextually relevant

### What Needs Improvement
1. **Irrelevant query detection** — 3.7/10 avg, bot often tries to answer "What is the capital of France?" instead of declining
2. **Hindi Devanagari** — 3.5/10 avg vs 7.0 English, major gap (though many were infra errors)
3. **Unsupported language handling** — French/Japanese get product responses instead of "language not supported" warning (4.0/10)
4. **Product browse in non-English** — Hindi/Gujarati browse queries often return empty (0 products, 0 sources)
5. **About brand queries** — 3.9/10, bot struggles to describe what the company sells
6. **Ambiguous queries in Hindi** — Bot doesn't provide helpful guidance for vague Hindi queries

---
## Executive Summary

### Scores by Query Type

| Query Type | Avg Score | Pass Rate | Tested | Status |
|---|---|---|---|---|
| context_summary | 9.5/10 | 100% | 3 | GOOD |
| comparison | 9.5/10 | 100% | 3 | GOOD |
| complaint | 8.3/10 | 100% | 3 | GOOD |
| specific_product | 8.2/10 | 83% | 12 | GOOD |
| greeting | 7.5/10 | 82% | 11 | GOOD |
| context_followup | 7.5/10 | 100% | 8 | GOOD |
| urgency | 7.5/10 | 100% | 2 | GOOD |
| variant_query | 7.3/10 | 100% | 5 | GOOD |
| price_query | 6.9/10 | 69% | 13 | FAIR |
| complex | 5.8/10 | 62% | 8 | FAIR |
| non_product | 5.6/10 | 73% | 15 | FAIR |
| context_start | 5.6/10 | 75% | 4 | FAIR |
| product_browse | 5.6/10 | 53% | 15 | FAIR |
| suggestions_test | 5.2/10 | 62% | 8 | FAIR |
| unsupported_lang | 4.0/10 | 100% | 6 | FAIR |
| about_brand | 3.9/10 | 57% | 7 | POOR |
| ambiguous | 3.8/10 | 55% | 11 | POOR |
| irrelevant | 3.7/10 | 40% | 15 | POOR |

### Scores by Language

| Language | Avg Score | Pass Rate | Tested |
|---|---|---|---|
| English | 7.0/10 | 81% | 89 |
| French | 4.0/10 | 100% | 4 |
| Gujarati | 4.7/10 | 43% | 7 |
| Hindi (Devanagari) | 3.5/10 | 43% | 37 |
| Hindi (Romanized) | 8.0/10 | 90% | 10 |
| Japanese | 4.0/10 | 100% | 2 |

### Scores by Site

| Site | Category | Pages | Avg Score | Pass Rate | Queries | Rate Limited |
|---|---|---|---|---|---|---|
| ramraj | Fashion/Clothing | 256 | 7.1/10 | 84% | 37 | 6 |
| truff | Food/Condiments | 262 | 5.8/10 | 66% | 38 | 5 |
| kriyanta | Tech/Startup | 803 | 4.9/10 | 65% | 40 | 3 |
| kids | Kids/Toys | 102 | 6.2/10 | 71% | 34 | 6 |

---
## Crawl Analysis

### Existing Chatbots (Pre-crawled)

- **ramraj** — https://ramrajcotton.in — 256 pages — Fashion/Clothing
- **truff** — https://truff.com — 262 pages — Food/Condiments
- **kriyanta** — https://www.kriyanta.com — 803 pages — Tech/Startup
- **kids** — https://www.cheaperzonetoys.com — 102 pages — Kids/Toys
- **zevaramaze** — https://zevaramaze.com — 276 pages — Jewelry

### Newly Crawled Sites

- **Boat Lifestyle** [FAILED]
  - URL: https://www.boat-lifestyle.com
  - Pages Crawled: 0
  - Status: unknown
- **Sugar Cosmetics** [FAILED]
  - URL: https://in.sugarcosmetics.com
  - Pages Crawled: 0
  - Status: unknown
- **Mokobara** [FAILED]
  - URL: https://www.mokobara.com
  - Pages Crawled: 0
  - Status: unknown

---
## Detailed Results Per Site

### ramraj (Fashion/Clothing)
**URL:** https://ramrajcotton.in | **Pages:** 256 | **Chatbot ID:** `182f88cd-02d8-4c94-824d-b41432847400`

**Summary:** Avg Score 7.1/10 | Passed 31/37 | Rate Limited 6

| # | Type | Lang | Query | Score | Prods | Srcs | Suggestions | Issues |
|---|---|---|---|---|---|---|---|---|
| 1 | greeting | en | Hi there! What can you help me with? | 9.5/10 | 0 | 12 | Show me your best-selling shirts, What's the price | - |
| 2 | greeting | hi | नमस्ते! आप मेरी कैसे मदद कर सकते हैं? | 8/10 | 0 | 16 | - | - |
| 3 | greeting | hi_roman | hello bhai, kya help kar sakte ho? | 9.5/10 | 0 | 12 | Mare ramraj ni shirts kayi prakar ni chhe?, Kya sa | - |
| 4 | product_browse | en | Show me your best shirts | 10/10 | 8 | 12 | What's the most popular shirt style?, Do you have  | - |
| 5 | product_browse | en | What dhotis do you have available? | 10/10 | 10 | 12 | What are the different fabrics used for dhotis?, D | - |
| 6 | product_browse | hi | आपके पास कौन से shirts उपलब्ध हैं? | 10/10 | 8 | 12 | રંગની શર્ટ કયા છે?, કયા સાઇઝ મળે છે? | - |
| 7 | product_browse | gu | તમારી પાસે કયા shirts છે? | 10/10 | 8 | 12 | આ બધામાંથી સૌથી popular કયો છે?, Discount version  | - |
| 8 | specific_product | en | I'm looking for a black shirts | 10/10 | 8 | 12 | What are the different materials available?, Do yo | - |
| 9 | specific_product | en | Do you have any premium cotton shirts? | 10/10 | 10 | 12 | What are the different colors available?, Can I ge | - |
| 10 | specific_product | hi | मुझे shirts चाहिए जो बहुत अच्छी क्वालिटी का ह | SKIP | 0 | 0 | - | RATE_LIMITED |
| 11 | specific_product | hi_roman | best quality shirts dikhao | 10/10 | 8 | 12 | Aa shirts ni price ketli chhe?, Best seller shirts | - |
| 12 | price_query | en | Show me shirts under ₹500 | SKIP | 0 | 0 | - | RATE_LIMITED |
| 13 | price_query | en | What's the price range for your dhotis? | 9.5/10 | 10 | 12 | Do you have any dhotis on sale?, What fabrics do y | - |
| 14 | price_query | hi | 500 रुपये से कम के shirts बताओ | SKIP | 0 | 0 | - | RATE_LIMITED |
| 15 | price_query | gu | ₹1000 થી ઓછા shirts બતાવો | 9.5/10 | 7 | 12 | આ બધામાંથી સૌથી popular કયો છે?, Discount version  | - |
| 16 | non_product | en | What is your return policy? | 8.5/10 | 0 | 12 | What's the deadline to return an item?, Can I exch | - |
| 17 | non_product | en | How long does shipping take? | 8.5/10 | 0 | 12 | What's the estimated delivery time for in-stock it | - |
| 18 | non_product | en | Do you offer cash on delivery? | 0/10 | 0 | 0 | - | ERROR: ('Connection aborted.', ConnectionResetError(10054, 'An existin |
| 19 | non_product | hi | रिटर्न पॉलिसी क्या है? | 0/10 | 0 | 0 | - | ERROR: ('Connection aborted.', ConnectionResetError(10054, 'An existin |
| 20 | irrelevant | en | What is the capital of France? | 9/10 | 0 | 12 | What products do you carry?, Tell me about ramraj | - |
| 21 | irrelevant | en | Can you write me a Python script to sort a li | SKIP | 0 | 0 | - | RATE_LIMITED |
| 22 | irrelevant | hi | भारत का प्रधानमंत्री कौन है? | 1/10 | 0 | 12 | - | FAILED to detect irrelevant query - bot tried to answer |
| 23 | irrelevant | en | What's the weather like in Tokyo today? | 9/10 | 0 | 12 | What products do you have?, Tell me about ramraj | - |
| 24 | ambiguous | en | I want something nice for a gift | 8.5/10 | 0 | 12 | What's the price range for these shirts?, Do you h | - |
| 25 | ambiguous | en | What do you recommend for someone new here? | SKIP | 0 | 0 | - | RATE_LIMITED |
| 26 | ambiguous | hi | कुछ अच्छा बताओ ना | 8.5/10 | 0 | 12 | કયો રંગ સૌથી વધારે વેચાય છે?, સૌથી સસ્તું ઓપ્શન શુ | - |
| 27 | complex | en | I need a gift for my sister, she likes shirts | 0/10 | 0 | 0 | - | ERROR: ('Connection aborted.', ConnectionResetError(10054, 'An existin |
| 28 | complex | hi | मेरी बहन के लिए shirts चाहिए, लाल या नीला रंग | 5.5/10 | 10 | 16 | લાલ રંગના શર્ટ કયા છે?, નીલા રંગના શર્ટની કિંમત શુ | Failed to handle multi-intent complex query fully |
| 29 | context_start | en | Show me your most popular shirts | 7.5/10 | 8 | 12 | Which of these shirts is the best seller?, Do any  | - |
| 30 | context_followup | en | Do you have this in a different color? | 7.5/10 | 8 | 12 | Which color is the most popular among customers?,  | - |
| 31 | context_followup | en | What about a larger size? | 7.5/10 | 8 | 12 | Do you have any bigger sizes in stock?, Can I get  | - |
| 32 | context_summary | en | Can you summarize what we've talked about so  | 9.5/10 | 0 | 12 | What are the largest sizes you offer?, Can I get a | - |
| 33 | about_brand | en | Tell me about ramraj and what you sell | SKIP | 0 | 0 | - | RATE_LIMITED |
| 34 | about_brand | hi | ramraj के बारे में बताओ | 0/10 | 0 | 0 | - | ERROR: ('Connection aborted.', ConnectionResetError(10054, 'An existin |
| 35 | unsupported_lang | fr | Bonjour, montrez-moi vos produits les plus po | 4/10 | 8 | 12 | Which of these is the best seller?, Do any come in | No warning about unsupported language |
| 36 | unsupported_lang | ja | こんにちは、人気商品を教えてください | 4/10 | 8 | 12 | What's the price range of these products?, Do you  | No warning about unsupported language |
| 37 | suggestions_test | en | I'm new here, what kind of things do you sell | 6.5/10 | 10 | 12 | What kind of shirts do you have?, Do you carry any | - |
| 38 | suggestions_test | hi | यहां क्या-क्या मिलता है? | 3/10 | 0 | 12 | - | No suggestions generated |
| 39 | comparison | en | What's the difference between your cheapest a | 9.5/10 | 10 | 16 | What's the price range of your colour shirts?, Do  | - |
| 40 | variant_query | en | Do you have shirts in size L or XL? | 7.5/10 | 8 | 12 | Which of these shirts is the most comfortable?, Do | - |
| 41 | variant_query | hi_roman | shirts mein kya sizes available hain? | 7/10 | 8 | 12 | - | - |
| 42 | urgency | en | I need shirts urgently for tomorrow, can you  | 7.5/10 | 8 | 12 | Do you offer same-day delivery?, What's the latest | - |
| 43 | complaint | en | I received a damaged shirts, what should I do | 8.5/10 | 8 | 12 | What's the deadline to return an item?, Can I exch | - |

### truff (Food/Condiments)
**URL:** https://truff.com | **Pages:** 262 | **Chatbot ID:** `e9f5fd28-cfe1-4456-994e-46aeb154388f`

**Summary:** Avg Score 5.8/10 | Passed 25/38 | Rate Limited 5

| # | Type | Lang | Query | Score | Prods | Srcs | Suggestions | Issues |
|---|---|---|---|---|---|---|---|---|
| 1 | greeting | en | Hi there! What can you help me with? | 9.5/10 | 0 | 12 | What products do you have for spicy food lovers?,  | - |
| 2 | greeting | hi | नमस्ते! आप मेरी कैसे मदद कर सकते हैं? | 8/10 | 0 | 0 | - | - |
| 3 | greeting | hi_roman | hello bhai, kya help kar sakte ho? | 9.5/10 | 0 | 0 | What are your most popular truff items?, Do you ha | - |
| 4 | product_browse | en | Show me your best hot sauce | 10/10 | 9 | 12 | What makes this hot sauce so special?, Do you have | - |
| 5 | product_browse | en | What truffle sauce do you have available? | SKIP | 0 | 0 | - | RATE_LIMITED |
| 6 | product_browse | hi | आपके पास कौन से hot sauce उपलब्ध हैं? | 2/10 | 0 | 0 | - | No products/sources for product query |
| 7 | product_browse | gu | તમારી પાસે કયા hot sauce છે? | 2/10 | 0 | 0 | - | No products/sources for product query |
| 8 | specific_product | en | I'm looking for a black hot sauce | SKIP | 0 | 0 | - | RATE_LIMITED |
| 9 | specific_product | en | Do you have any premium pasta sauce? | 10/10 | 8 | 12 | What makes this pasta sauce premium?, Do you have  | - |
| 10 | specific_product | hi | मुझे hot sauce चाहिए जो बहुत अच्छी क्वालिटी क | 2/10 | 0 | 0 | - | No products/sources for product query |
| 11 | specific_product | hi_roman | best quality hot sauce dikhao | 10/10 | 2 | 12 | What's the difference between TRUFF and regular ho | - |
| 12 | price_query | en | Show me hot sauce under ₹500 | 9.5/10 | 3 | 12 | Which of these hot sauces is the most popular?, Do | - |
| 13 | price_query | en | What's the price range for your truffle sauce | 9.5/10 | 3 | 12 | Do you have any truffle sauce bundles?, Is the $19 | - |
| 14 | price_query | hi | 500 रुपये से कम के hot sauce बताओ | 2/10 | 0 | 0 | - | No price info for price query |
| 15 | price_query | gu | ₹1000 થી ઓછા hot sauce બતાવો | 2/10 | 0 | 0 | - | No price info for price query |
| 16 | non_product | en | What is your return policy? | 8.5/10 | 0 | 12 | What's the deadline to return an item?, Can I exch | - |
| 17 | non_product | en | How long does shipping take? | 8.5/10 | 0 | 12 | What's the return policy?, Do you offer expedited  | - |
| 18 | non_product | en | Do you offer cash on delivery? | 0/10 | 0 | 0 | - | ERROR: ('Connection aborted.', RemoteDisconnected('Remote end closed c |
| 19 | non_product | hi | रिटर्न पॉलिसी क्या है? | 0/10 | 0 | 0 | - | ERROR: ('Connection aborted.', RemoteDisconnected('Remote end closed c |
| 20 | irrelevant | en | What is the capital of France? | 0/10 | 0 | 0 | - | ERROR: ('Connection aborted.', RemoteDisconnected('Remote end closed c |
| 21 | irrelevant | en | Can you write me a Python script to sort a li | 0/10 | 0 | 0 | - | ERROR: ('Connection aborted.', RemoteDisconnected('Remote end closed c |
| 22 | irrelevant | hi | भारत का प्रधानमंत्री कौन है? | 0/10 | 0 | 0 | - | ERROR: ('Connection aborted.', ConnectionResetError(10054, 'An existin |
| 23 | irrelevant | en | What's the weather like in Tokyo today? | 9/10 | 0 | 12 | What products do you carry?, Tell me about truff | - |
| 24 | ambiguous | en | I want something nice for a gift | 8.5/10 | 0 | 0 | What's the most popular truff gift set?, Do you ha | - |
| 25 | ambiguous | en | What do you recommend for someone new here? | 0/10 | 0 | 0 | - | ERROR: ('Connection aborted.', ConnectionResetError(10054, 'An existin |
| 26 | ambiguous | hi | कुछ अच्छा बताओ ना | 4/10 | 0 | 0 | - | Could give better guidance for ambiguous query |
| 27 | complex | en | I need a gift for my sister, she likes hot sa | 10/10 | 10 | 16 | Which hot sauce is the most popular among customer | - |
| 28 | complex | hi | मेरी बहन के लिए hot sauce चाहिए, लाल या नीला  | 3/10 | 0 | 0 | - | Failed to handle multi-intent complex query fully |
| 29 | context_start | en | Show me your most popular hot sauce | 7.5/10 | 10 | 12 | What makes this hot sauce so popular?, Do you have | - |
| 30 | context_followup | en | Do you have this in a different color? | 7.5/10 | 0 | 12 | What's the difference between your hot sauces?, Ca | - |
| 31 | context_followup | en | What about a larger size? | 7.5/10 | 2 | 12 | Do you have any hot sauces in larger sizes?, Can I | - |
| 32 | context_summary | en | Can you summarize what we've talked about so  | SKIP | 0 | 0 | - | RATE_LIMITED |
| 33 | about_brand | en | Tell me about truff and what you sell | 8.5/10 | 0 | 12 | What makes your truffle hot sauce so special?, Do  | - |
| 34 | about_brand | hi | truff के बारे में बताओ | 5/10 | 0 | 0 | - | - |
| 35 | unsupported_lang | fr | Bonjour, montrez-moi vos produits les plus po | 4/10 | 10 | 12 | Which of these is the best seller?, Do any come in | No warning about unsupported language |
| 36 | unsupported_lang | ja | こんにちは、人気商品を教えてください | SKIP | 0 | 0 | - | RATE_LIMITED |
| 37 | suggestions_test | en | I'm new here, what kind of things do you sell | 6.5/10 | 10 | 12 | What makes your truffle products unique?, Do you h | - |
| 38 | suggestions_test | hi | यहां क्या-क्या मिलता है? | 3/10 | 0 | 0 | - | No suggestions generated |
| 39 | comparison | en | What's the difference between your cheapest a | 9.5/10 | 2 | 16 | What's the price range of your hot sauces?, Do you | - |
| 40 | variant_query | en | Do you have hot sauce in size L or XL? | SKIP | 0 | 0 | - | RATE_LIMITED |
| 41 | variant_query | hi_roman | hot sauce mein kya sizes available hain? | 7.5/10 | 10 | 12 | What are the prices of your hot sauces?, Do you ha | - |
| 42 | urgency | en | I need hot sauce urgently for tomorrow, can y | 7.5/10 | 10 | 12 | What's the cutoff time for same-day shipping?, Do  | - |
| 43 | complaint | en | I received a damaged hot sauce, what should I | 8.5/10 | 1 | 12 | What's the process for exchanging a damaged item?, | - |

### kriyanta (Tech/Startup)
**URL:** https://www.kriyanta.com | **Pages:** 803 | **Chatbot ID:** `1cb18dc0-4909-409d-ab03-0436524fcec4`

**Summary:** Avg Score 4.9/10 | Passed 26/40 | Rate Limited 3

| # | Type | Lang | Query | Score | Prods | Srcs | Suggestions | Issues |
|---|---|---|---|---|---|---|---|---|
| 1 | greeting | en | Hi there! What can you help me with? | 9.5/10 | 0 | 12 | I'm looking for a gift for my friend, What kind of | - |
| 2 | greeting | hi | नमस्ते! आप मेरी कैसे मदद कर सकते हैं? | SKIP | 0 | 0 | - | RATE_LIMITED |
| 3 | greeting | hi_roman | hello bhai, kya help kar sakte ho? | 0/10 | 0 | 0 | - | ERROR: ('Connection aborted.', RemoteDisconnected('Remote end closed c |
| 4 | product_browse | en | Show me your best services | 0/10 | 0 | 0 | - | ERROR: ('Connection aborted.', RemoteDisconnected('Remote end closed c |
| 5 | product_browse | en | What solutions do you have available? | 0/10 | 0 | 0 | - | ERROR: ('Connection aborted.', ConnectionAbortedError(10053, 'An estab |
| 6 | product_browse | hi | आपके पास कौन से services उपलब्ध हैं? | 0/10 | 0 | 0 | - | ERROR: ('Connection aborted.', RemoteDisconnected('Remote end closed c |
| 7 | product_browse | gu | તમારી પાસે કયા services છે? | 5.5/10 | 0 | 12 | ફ્રી શિપિંગ ક્યાં સુધી છે?, કન્સલ્ટેશન માટે કેવી ર | Sources found but no product cards |
| 8 | specific_product | en | I'm looking for a black services | 10/10 | 1 | 5 | Do you have black phone cases?, Can I customize a  | - |
| 9 | specific_product | en | Do you have any premium portfolio? | 10/10 | 10 | 12 | What makes these portfolios premium?, Can I custom | - |
| 10 | specific_product | hi | मुझे services चाहिए जो बहुत अच्छी क्वालिटी का | 5/10 | 0 | 12 | - | Sources found but no product cards |
| 11 | specific_product | hi_roman | best quality services dikhao | 10/10 | 10 | 12 | What makes your interior decoration consultation u | - |
| 12 | price_query | en | Show me services under ₹500 | 9.5/10 | 2 | 12 | What's the most popular item in this range?, Can I | - |
| 13 | price_query | en | What's the price range for your solutions? | 5.5/10 | 0 | 12 | What's the most popular item in the INR 999 range? | - |
| 14 | price_query | hi | 500 रुपये से कम के services बताओ | 9.5/10 | 5 | 12 | આ બધામાંથી સૌથી popular કયો છે?, Discount version  | - |
| 15 | price_query | gu | ₹1000 થી ઓછા services બતાવો | SKIP | 0 | 0 | - | RATE_LIMITED |
| 16 | non_product | en | What is your return policy? | 8.5/10 | 0 | 12 | What's the process for initiating a return?, Can I | - |
| 17 | non_product | en | How long does shipping take? | 8.5/10 | 0 | 12 | What's the shipping cost for orders under 1000?, C | - |
| 18 | non_product | en | Do you offer cash on delivery? | 8.5/10 | 0 | 12 | What payment methods do you accept?, Can I get a l | - |
| 19 | non_product | hi | रिटर्न पॉलिसी क्या है? | 4/10 | 0 | 0 | - | - |
| 20 | irrelevant | en | What is the capital of France? | 0/10 | 0 | 0 | - | ERROR: ('Connection aborted.', ConnectionResetError(10054, 'An existin |
| 21 | irrelevant | en | Can you write me a Python script to sort a li | 0/10 | 0 | 0 | - | ERROR: ('Connection aborted.', ConnectionResetError(10054, 'An existin |
| 22 | irrelevant | hi | भारत का प्रधानमंत्री कौन है? | 0/10 | 0 | 0 | - | ERROR: ('Connection aborted.', ConnectionResetError(10054, 'An existin |
| 23 | irrelevant | en | What's the weather like in Tokyo today? | 0/10 | 0 | 0 | - | ERROR: ('Connection aborted.', ConnectionResetError(10054, 'An existin |
| 24 | ambiguous | en | I want something nice for a gift | 0/10 | 0 | 0 | - | ERROR: ('Connection aborted.', ConnectionResetError(10054, 'An existin |
| 25 | ambiguous | en | What do you recommend for someone new here? | 0/10 | 0 | 0 | - | ERROR: ('Connection aborted.', ConnectionResetError(10054, 'An existin |
| 26 | ambiguous | hi | कुछ अच्छा बताओ ना | 0/10 | 0 | 0 | - | ERROR: ('Connection aborted.', ConnectionResetError(10054, 'An existin |
| 27 | complex | en | I need a gift for my sister, she likes servic | 9.5/10 | 2 | 16 | Do any of these gifts come in a combination of red | - |
| 28 | complex | hi | मेरी बहन के लिए services चाहिए, लाल या नीला र | 5.5/10 | 7 | 16 | લાલ રંગનું કયું પ્રોડક્ટ સૌથી સસ્તું છે?, નીલા રંગ | Failed to handle multi-intent complex query fully |
| 29 | context_start | en | Show me your most popular services | 0/10 | 0 | 0 | - | ERROR: ('Connection aborted.', ConnectionResetError(10054, 'An existin |
| 30 | context_followup | en | Do you have this in a different color? | 7.5/10 | 0 | 1 | Which colors are available for this product?, Can  | - |
| 31 | context_followup | en | What about a larger size? | 7.5/10 | 10 | 12 | Which products come in extra large sizes?, Can I c | - |
| 32 | context_summary | en | Can you summarize what we've talked about so  | 9.5/10 | 0 | 7 | What products do you have in stock?, Can I customi | - |
| 33 | about_brand | en | Tell me about kriyanta and what you sell | 0/10 | 0 | 0 | - | ERROR: ('Connection aborted.', ConnectionResetError(10054, 'An existin |
| 34 | about_brand | hi | kriyanta के बारे में बताओ | 0/10 | 0 | 0 | - | ERROR: ('Connection aborted.', ConnectionResetError(10054, 'An existin |
| 35 | unsupported_lang | fr | Bonjour, montrez-moi vos produits les plus po | 4/10 | 10 | 12 | Which of these is the best seller?, Do you have an | No warning about unsupported language |
| 36 | unsupported_lang | ja | こんにちは、人気商品を教えてください | 4/10 | 10 | 12 | What are the prices of these products?, Can I get  | No warning about unsupported language |
| 37 | suggestions_test | en | I'm new here, what kind of things do you sell | 6.5/10 | 10 | 12 | What kind of handmade items do you have?, Do you h | - |
| 38 | suggestions_test | hi | यहां क्या-क्या मिलता है? | 6.5/10 | 10 | 12 | આ બધામાંથી સૌથી popular કયો છે?, ડિસ્કાઉન્ટ મળે છે | - |
| 39 | comparison | en | What's the difference between your cheapest a | 9.5/10 | 10 | 16 | What makes the Bedroom Bliss Collection so expensi | - |
| 40 | variant_query | en | Do you have services in size L or XL? | 7.5/10 | 2 | 3 | Do any of these come in a larger size?, Can I cust | - |
| 41 | variant_query | hi_roman | services mein kya sizes available hain? | 7/10 | 0 | 6 | - | - |
| 42 | urgency | en | I need services urgently for tomorrow, can yo | SKIP | 0 | 0 | - | RATE_LIMITED |
| 43 | complaint | en | I received a damaged services, what should I  | 8/10 | 0 | 12 | - | - |

### kids (Kids/Toys)
**URL:** https://www.cheaperzonetoys.com | **Pages:** 102 | **Chatbot ID:** `868f937e-8559-446d-b7c8-ff630ec7fd79`

**Summary:** Avg Score 6.2/10 | Passed 24/34 | Rate Limited 6

| # | Type | Lang | Query | Score | Prods | Srcs | Suggestions | Issues |
|---|---|---|---|---|---|---|---|---|
| 1 | greeting | en | Hi there! What can you help me with? | 9.5/10 | 0 | 12 | What's the most popular product you have?, Do you  | - |
| 2 | greeting | hi | नमस्ते! आप मेरी कैसे मदद कर सकते हैं? | 0/10 | 0 | 0 | - | ERROR: ('Connection aborted.', ConnectionResetError(10054, 'An existin |
| 3 | greeting | hi_roman | hello bhai, kya help kar sakte ho? | 9.5/10 | 0 | 12 | What products do you have for kids?, Can you show  | - |
| 4 | product_browse | en | Show me your best toys | 10/10 | 10 | 12 | Which of these is the most popular?, Do you have a | - |
| 5 | product_browse | en | What board games do you have available? | 10/10 | 10 | 12 | Which games are suitable for kids under 10?, Do yo | - |
| 6 | product_browse | hi | आपके पास कौन से toys उपलब्ध हैं? | 2/10 | 0 | 0 | - | No products/sources for product query |
| 7 | product_browse | gu | તમારી પાસે કયા toys છે? | 2/10 | 0 | 0 | - | No products/sources for product query |
| 8 | specific_product | en | I'm looking for a black toys | 10/10 | 7 | 12 | Do any of these black toys come with a warranty?,  | - |
| 9 | specific_product | en | Do you have any premium action figures? | SKIP | 0 | 0 | - | RATE_LIMITED |
| 10 | specific_product | hi | मुझे toys चाहिए जो बहुत अच्छी क्वालिटी का हो | 2/10 | 0 | 0 | - | No products/sources for product query |
| 11 | specific_product | hi_roman | best quality toys dikhao | SKIP | 0 | 0 | - | RATE_LIMITED |
| 12 | price_query | en | Show me toys under ₹500 | 9.5/10 | 10 | 12 | Which of these toys is best for a 5-year-old?, Do  | - |
| 13 | price_query | en | What's the price range for your board games? | 9.5/10 | 10 | 12 | Which board game is most popular with kids?, Do yo | - |
| 14 | price_query | hi | 500 रुपये से कम के toys बताओ | 2/10 | 0 | 0 | - | No price info for price query |
| 15 | price_query | gu | ₹1000 થી ઓછા toys બતાવો | 2/10 | 0 | 0 | - | No price info for price query |
| 16 | non_product | en | What is your return policy? | 8.5/10 | 0 | 12 | Show me your full collection, What are your best-s | - |
| 17 | non_product | en | How long does shipping take? | SKIP | 0 | 0 | - | RATE_LIMITED |
| 18 | non_product | en | Do you offer cash on delivery? | 8.5/10 | 0 | 12 | What payment methods do you accept?, Can I get hel | - |
| 19 | non_product | hi | रिटर्न पॉलिसी क्या है? | 4/10 | 0 | 0 | - | - |
| 20 | irrelevant | en | What is the capital of France? | 9/10 | 0 | 12 | What products do you carry?, Tell me about Rozzby | - |
| 21 | irrelevant | en | Can you write me a Python script to sort a li | 1/10 | 0 | 16 | What toys do you have for kids?, Can I see your be | FAILED to detect irrelevant query - bot tried to answer |
| 22 | irrelevant | hi | भारत का प्रधानमंत्री कौन है? | 9/10 | 0 | 0 | - | - |
| 23 | irrelevant | en | What's the weather like in Tokyo today? | 9/10 | 0 | 12 | What city's weather can you tell me about?, Do you | - |
| 24 | ambiguous | en | I want something nice for a gift | 8.5/10 | 0 | 12 | What's the best gift for a baby?, Do you have any  | - |
| 25 | ambiguous | en | What do you recommend for someone new here? | 0/10 | 0 | 0 | - | ERROR: ('Connection aborted.', ConnectionResetError(10054, 'An existin |
| 26 | ambiguous | hi | कुछ अच्छा बताओ ना | 4/10 | 0 | 0 | - | Could give better guidance for ambiguous query |
| 27 | complex | en | I need a gift for my sister, she likes toys i | 10/10 | 10 | 16 | What are the best red toys you have under ₹1500?,  | - |
| 28 | complex | hi | मेरी बहन के लिए toys चाहिए, लाल या नीला रंग,  | 3/10 | 0 | 0 | - | Failed to handle multi-intent complex query fully |
| 29 | context_start | en | Show me your most popular toys | 7.5/10 | 10 | 12 | Which of these is the best seller for boys?, Do an | - |
| 30 | context_followup | en | Do you have this in a different color? | 7.5/10 | 10 | 12 | Which of these toys has the most color options?, C | - |
| 31 | context_followup | en | What about a larger size? | 7.5/10 | 10 | 12 | Do larger sizes cost more?, Can I customize the si | - |
| 32 | context_summary | en | Can you summarize what we've talked about so  | 9.5/10 | 0 | 12 | What are the prices for these items?, Do you have  | - |
| 33 | about_brand | en | Tell me about kids and what you sell | 8.5/10 | 0 | 12 | What's the best seller among these products?, Do y | - |
| 34 | about_brand | hi | kids के बारे में बताओ | 5/10 | 0 | 0 | - | - |
| 35 | unsupported_lang | fr | Bonjour, montrez-moi vos produits les plus po | 4/10 | 10 | 12 | Which of these is the best seller?, Do any come in | No warning about unsupported language |
| 36 | unsupported_lang | ja | こんにちは、人気商品を教えてください | SKIP | 0 | 0 | - | RATE_LIMITED |
| 37 | suggestions_test | en | I'm new here, what kind of things do you sell | 6.5/10 | 10 | 12 | What are the most popular toys for kids here?, Do  | - |
| 38 | suggestions_test | hi | यहां क्या-क्या मिलता है? | 3/10 | 0 | 0 | - | No suggestions generated |
| 39 | comparison | en | What's the difference between your cheapest a | SKIP | 0 | 0 | - | RATE_LIMITED |
| 40 | variant_query | en | Do you have toys in size L or XL? | SKIP | 0 | 0 | - | RATE_LIMITED |


---
## Product Display Analysis

How well product cards are returned for product-related queries.

### ramraj (Fashion/Clothing)
- Product queries tested: 14
- Queries returning products: 13/14 (93%)

  **Q:** "Show me your best shirts" [product_browse, en]
  **Score:** 10/10 | **Products:** 8 | **Sources:** 12
  - Men Cotton Rich Shirt Full Sleeves Green T32 TH8 | Price: 945.0 | https://ramrajcotton.in/collections/colour-shirts/products/m
  - Men Cotton Rich Full Sleeves Shirt Mustard T28 TD1 | Price: 945.0 | https://ramrajcotton.in/collections/colour-shirts/products/m
  - Men Cotton Rich Shirt Green Trendy 8 YH1 | Price: 775.0 | https://ramrajcotton.in/collections/colour-shirts/products/m

  **Q:** "What dhotis do you have available?" [product_browse, en]
  **Score:** 10/10 | **Products:** 10 | **Sources:** 12
  - Mens Party Wear Purple Shirt PSS7 | Price: 975.0 | https://ramrajcotton.in/collections/colour-shirts/products/m
  - Mens Party Wear Black Shirt PSS5 | Price: 975.0 | https://ramrajcotton.in/collections/colour-shirts/products/m
  - Men Cotton Spandex Shirt 2 Way Stretch Purple LY5 | Price: 1145.0 | https://ramrajcotton.in/collections/colour-shirts/products/m

  **Q:** "आपके पास कौन से shirts उपलब्ध हैं?" [product_browse, hi]
  **Score:** 10/10 | **Products:** 8 | **Sources:** 12
  - Men Cotton Rich Shirt Full Sleeves Green T32 TH8 | Price: 945.0 | https://ramrajcotton.in/collections/colour-shirts/products/m
  - Men Cotton Blend Full Sleeves Shirt Pista Green T2 | Price: 945.0 | https://ramrajcotton.in/collections/colour-shirts/products/m
  - Men Cotton Blend Full Sleeves Shirt Dark Green T26 | Price: 945.0 | https://ramrajcotton.in/collections/colour-shirts/products/m

  **Q:** "તમારી પાસે કયા shirts છે?" [product_browse, gu]
  **Score:** 10/10 | **Products:** 8 | **Sources:** 12
  - Men Cotton Rich Shirt Full Sleeves Green T32 TH8 | Price: 945.0 | https://ramrajcotton.in/collections/colour-shirts/products/m
  - Men Cotton Blend Full Sleeves Shirt Dark Green T26 | Price: 945.0 | https://ramrajcotton.in/collections/colour-shirts/products/m
  - Men Stretch Poly Shirt Olive Green PS1 | Price: 975.0 | https://ramrajcotton.in/collections/colour-shirts/products/m

  **Q:** "I'm looking for a black shirts" [specific_product, en]
  **Score:** 10/10 | **Products:** 8 | **Sources:** 12
  - Men Cotton Blend Shirt Black MA8 | Price: 835.0 | https://ramrajcotton.in/collections/colour-shirts/products/m
  - Men Cotton Blend Shirt Black | Price: 895.0 | https://ramrajcotton.in/collections/colour-shirts/products/m
  - Men Party Wear Black Shirt PS5 | Price: 975.0 | https://ramrajcotton.in/collections/colour-shirts/products/m

  **Q:** "Do you have any premium cotton shirts?" [specific_product, en]
  **Score:** 10/10 | **Products:** 10 | **Sources:** 12
  - Men Premium Cotton Shirt Orange EL GP15 | Price: 1160.0 | https://ramrajcotton.in/collections/colour-shirts/products/m
  - Men Premium Cotton Shirt Blue EL GP5 | Price: 1160.0 | https://ramrajcotton.in/collections/colour-shirts/products/m
  - Men Cotton Rich Shirt LT Beige T64 ANT6 | Price: 895.0 | https://ramrajcotton.in/collections/colour-shirts/products/m

  **Q:** "best quality shirts dikhao" [specific_product, hi_roman]
  **Score:** 10/10 | **Products:** 8 | **Sources:** 12
  - Men Cotton Rich Shirt Full Sleeves Green T32 TH8 | Price: 945.0 | https://ramrajcotton.in/collections/colour-shirts/products/m
  - Men Cotton Rich Full Sleeves Shirt Mustard T28 TD1 | Price: 945.0 | https://ramrajcotton.in/collections/colour-shirts/products/m
  - Men Cotton Blend Full Sleeves Shirt Dark Green T26 | Price: 945.0 | https://ramrajcotton.in/collections/colour-shirts/products/m

  **Q:** "What's the price range for your dhotis?" [price_query, en]
  **Score:** 9.5/10 | **Products:** 10 | **Sources:** 12
  - Mens Party Wear Purple Shirt PSS7 | Price: 975.0 | https://ramrajcotton.in/collections/colour-shirts/products/m
  - Mens Party Wear Black Shirt PSS5 | Price: 975.0 | https://ramrajcotton.in/collections/colour-shirts/products/m
  - Men Cotton Rich Half Sleeve Shirt Blue Dobby T59 A | Price: 895.0 | https://ramrajcotton.in/collections/colour-shirts/products/m

  **Q:** "₹1000 થી ઓછા shirts બતાવો" [price_query, gu]
  **Score:** 9.5/10 | **Products:** 7 | **Sources:** 12
  - Men 100% Cotton Shirt Green TW1 | Price: 895.0 | https://ramrajcotton.in/collections/colour-shirts/products/m
  - Men 100% Cotton Shirt Copper G105 | Price: 975.0 | https://ramrajcotton.in/collections/colour-shirts/products/m
  - Men Cotton Rich Shirt Full Sleeves Green T32 TH8 | Price: 945.0 | https://ramrajcotton.in/collections/colour-shirts/products/m

  **Q:** "I need a gift for my sister, she likes shirts in red or blue" [complex, en]
  **Score:** 0/10 | **Products:** 0 | **Sources:** 0
  Issues: ERROR: ('Connection aborted.', ConnectionResetError(10054, 'An existing connection was forcibly closed by the remote host', None, 10054, None))

  **Q:** "मेरी बहन के लिए shirts चाहिए, लाल या नीला रंग, 2000 रुपये से" [complex, hi]
  **Score:** 5.5/10 | **Products:** 10 | **Sources:** 16
  - Men Stretch Poly shirt Berry Red PS7 | Price: 975.0 | https://ramrajcotton.in/collections/colour-shirts/products/m
  - Men Stretch Poly Shirt Pink PS9 | Price: 975.0 | https://ramrajcotton.in/collections/colour-shirts/products/m
  - Men Cotton Rich Half Sleeves Shirt Red T32 TH7 | Price: 895.0 | https://ramrajcotton.in/collections/colour-shirts/products/m
  Issues: Failed to handle multi-intent complex query fully

  **Q:** "What's the difference between your cheapest and most expensi" [comparison, en]
  **Score:** 9.5/10 | **Products:** 10 | **Sources:** 16
  - Men Cotton Rich Shirt Green Trendy 8 YH1 | Price: 775.0 | https://ramrajcotton.in/collections/colour-shirts/products/m
  - Men Cotton Rich Shirt Light Purple T61 AKT3 | Price: 895.0 | https://ramrajcotton.in/collections/colour-shirts/products/m
  - Men Cotton Rich Half Sleeves Shirt Red T32 TH7 | Price: 895.0 | https://ramrajcotton.in/collections/colour-shirts/products/m

  **Q:** "Do you have shirts in size L or XL?" [variant_query, en]
  **Score:** 7.5/10 | **Products:** 8 | **Sources:** 12
  - Men Linen Cotton Shirt Yellowish Green LF9 | Price: 1350.0 | https://ramrajcotton.in/collections/colour-shirts/products/m
  - Men Linen Cotton Shirt Maroon LF14 | Price: 1350.0 | https://ramrajcotton.in/collections/colour-shirts/products/m
  - Men Linen Cotton Shirt Grey LF7 | Price: 1350.0 | https://ramrajcotton.in/collections/colour-shirts/products/m

  **Q:** "shirts mein kya sizes available hain?" [variant_query, hi_roman]
  **Score:** 7/10 | **Products:** 8 | **Sources:** 12
  - Men Stretch Poly Shirt Navy PS4 | Price: 975.0 | https://ramrajcotton.in/collections/colour-shirts/products/m
  - Men Stretch Cotton Shirt Olive Green FS32 | Price: 1145.0 | https://ramrajcotton.in/collections/colour-shirts/products/m
  - Men Stretch Poly Shirt Olive Green PS1 | Price: 975.0 | https://ramrajcotton.in/collections/colour-shirts/products/m

### truff (Food/Condiments)
- Product queries tested: 14
- Queries returning products: 8/14 (57%)

  **Q:** "Show me your best hot sauce" [product_browse, en]
  **Score:** 10/10 | **Products:** 9 | **Sources:** 12
  - Spice Up Your Barbecue: A Guide to Hot Sauces for  | Price: rs, | https://truff.com/articles/hot-sauce-grilling
  - What To Put Hot Sauce On | Price: rs, | https://truff.com/articles/what-to-put-hot-sauce-on
  - What Is Hot Sauce Made Of? | Price: rs, | https://truff.com/articles/what-is-hot-sauce-made-of

  **Q:** "आपके पास कौन से hot sauce उपलब्ध हैं?" [product_browse, hi]
  **Score:** 2/10 | **Products:** 0 | **Sources:** 0
  Issues: No products/sources for product query

  **Q:** "તમારી પાસે કયા hot sauce છે?" [product_browse, gu]
  **Score:** 2/10 | **Products:** 0 | **Sources:** 0
  Issues: No products/sources for product query

  **Q:** "Do you have any premium pasta sauce?" [specific_product, en]
  **Score:** 10/10 | **Products:** 8 | **Sources:** 12
  - Pasta Sauce | Price: $25 | https://truff.com/collections/pasta-sauce
  - Truffle Pasta Sauce: How To Use Truffle Pasta Sauc | Price: rs, | https://truff.com/articles/truffle-pasta-sauce
  - Homemade Empanadas | Price: rs, | https://truff.com/articles/empanadas

  **Q:** "मुझे hot sauce चाहिए जो बहुत अच्छी क्वालिटी का हो" [specific_product, hi]
  **Score:** 2/10 | **Products:** 0 | **Sources:** 0
  Issues: No products/sources for product query

  **Q:** "best quality hot sauce dikhao" [specific_product, hi_roman]
  **Score:** 10/10 | **Products:** 2 | **Sources:** 12
  - TRUFF Jalapeño Lime Hot Sauce | Price: 17.98 | https://truff.com/products/truff-jalapeno-lime-hot-sauce
  - TRUFF Original Hot Sauce | Price: 17.98 | https://truff.com/products/truff

  **Q:** "Show me hot sauce under ₹500" [price_query, en]
  **Score:** 9.5/10 | **Products:** 3 | **Sources:** 12
  - TRUFF Jalapeño Lime Hot Sauce | Price: 17.98 | https://truff.com/products/truff-jalapeno-lime-hot-sauce
  - TRUFF Mild Hot Sauce (2 Pack) | Price: 19.99 | https://truff.com/products/truff-mild-hot-sauce-2-pack
  - TRUFF Original Hot Sauce | Price: 17.98 | https://truff.com/products/truff

  **Q:** "What's the price range for your truffle sauce?" [price_query, en]
  **Score:** 9.5/10 | **Products:** 3 | **Sources:** 12
  - TRUFF Original Hot Sauce | Price: 17.98 | https://truff.com/products/truff
  - TRUFF Mild Hot Sauce (2 Pack) | Price: 19.99 | https://truff.com/products/truff-mild-hot-sauce-2-pack
  - TRUFF Jalapeño Lime Hot Sauce | Price: 17.98 | https://truff.com/products/truff-jalapeno-lime-hot-sauce

  **Q:** "500 रुपये से कम के hot sauce बताओ" [price_query, hi]
  **Score:** 2/10 | **Products:** 0 | **Sources:** 0
  Issues: No price info for price query

  **Q:** "₹1000 થી ઓછા hot sauce બતાવો" [price_query, gu]
  **Score:** 2/10 | **Products:** 0 | **Sources:** 0
  Issues: No price info for price query

  **Q:** "I need a gift for my sister, she likes hot sauce in red or b" [complex, en]
  **Score:** 10/10 | **Products:** 10 | **Sources:** 16
  - Unique Food Gifts: Fun Food Holiday Gift Ideas | Price: rs, | https://truff.com/articles/unique-food-gifts
  - Gifts | Price: $25 | https://truff.com/collections/gifts
  - Gifts for Chicken Wing Lovers: Holiday Gift Guide | Price: rs, | https://truff.com/articles/gifts-for-chicken-wing-lovers

  **Q:** "मेरी बहन के लिए hot sauce चाहिए, लाल या नीला रंग, 2000 रुपये" [complex, hi]
  **Score:** 3/10 | **Products:** 0 | **Sources:** 0
  Issues: Failed to handle multi-intent complex query fully

  **Q:** "What's the difference between your cheapest and most expensi" [comparison, en]
  **Score:** 9.5/10 | **Products:** 2 | **Sources:** 16
  - TRUFF Mild Hot Sauce (2 Pack) | Price: 19.99 | https://truff.com/products/truff-mild-hot-sauce-2-pack
  - TRUFF Original Hot Sauce | Price: 17.98 | https://truff.com/products/truff

  **Q:** "hot sauce mein kya sizes available hain?" [variant_query, hi_roman]
  **Score:** 7.5/10 | **Products:** 10 | **Sources:** 12
  - Spice Up Your Barbecue: A Guide to Hot Sauces for  | Price: rs, | https://truff.com/articles/hot-sauce-grilling
  - What To Put Hot Sauce On | Price: rs, | https://truff.com/articles/what-to-put-hot-sauce-on
  - What Is Hot Sauce Made Of? | Price: rs, | https://truff.com/articles/what-is-hot-sauce-made-of

### kriyanta (Tech/Startup)
- Product queries tested: 16
- Queries returning products: 9/16 (56%)

  **Q:** "Show me your best services" [product_browse, en]
  **Score:** 0/10 | **Products:** 0 | **Sources:** 0
  Issues: ERROR: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))

  **Q:** "What solutions do you have available?" [product_browse, en]
  **Score:** 0/10 | **Products:** 0 | **Sources:** 0
  Issues: ERROR: ('Connection aborted.', ConnectionAbortedError(10053, 'An established connection was aborted by the software in your host machine', None, 10053, None))

  **Q:** "आपके पास कौन से services उपलब्ध हैं?" [product_browse, hi]
  **Score:** 0/10 | **Products:** 0 | **Sources:** 0
  Issues: ERROR: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))

  **Q:** "તમારી પાસે કયા services છે?" [product_browse, gu]
  **Score:** 5.5/10 | **Products:** 0 | **Sources:** 12
  Issues: Sources found but no product cards

  **Q:** "I'm looking for a black services" [specific_product, en]
  **Score:** 10/10 | **Products:** 1 | **Sources:** 5
  - Artistic Phone Case | Price: inr 999 | https://www.kriyanta.com/product-detail/artistic-phone-case

  **Q:** "Do you have any premium portfolio?" [specific_product, en]
  **Score:** 10/10 | **Products:** 10 | **Sources:** 12
  - Study Room Focus Collection | Price: 3397.0 | https://www.kriyanta.com/collection-view/study
  - Customized Items | Price: 999.0 | https://www.kriyanta.com/category-view/customized
  - Personalized Gifting | Price: 999.0 | https://www.kriyanta.com/category-view/personalised

  **Q:** "मुझे services चाहिए जो बहुत अच्छी क्वालिटी का हो" [specific_product, hi]
  **Score:** 5/10 | **Products:** 0 | **Sources:** 12
  Issues: Sources found but no product cards

  **Q:** "best quality services dikhao" [specific_product, hi_roman]
  **Score:** 10/10 | **Products:** 10 | **Sources:** 12
  - Study Room Focus Collection | Price: 3397.0 | https://www.kriyanta.com/collection-view/study
  - Kitchen & Dining Warmth Collection | Price: 392.0 | https://www.kriyanta.com/collection-view/kitchen
  - Living Room Luxe Collection | Price: 3397.0 | https://www.kriyanta.com/collection-view/living

  **Q:** "Show me services under ₹500" [price_query, en]
  **Score:** 9.5/10 | **Products:** 2 | **Sources:** 12
  - Kitchen & Dining Warmth Collection | Price: 392.0 | https://www.kriyanta.com/collection-view/kitchen
  - Compact Wooden Office Home Temple: Stylish Workspa | Price: 499.0 | https://www.kriyanta.com/product-detail/compact-wooden-offic

  **Q:** "What's the price range for your solutions?" [price_query, en]
  **Score:** 5.5/10 | **Products:** 0 | **Sources:** 12

  **Q:** "500 रुपये से कम के services बताओ" [price_query, hi]
  **Score:** 9.5/10 | **Products:** 5 | **Sources:** 12
  - Kitchen & Dining Warmth Collection | Price: 392.0 | https://www.kriyanta.com/collection-view/kitchen
  - Compact Wooden Office Home Temple: Stylish Workspa | Price: 499.0 | https://www.kriyanta.com/product-detail/compact-wooden-offic
  - Wall Mounted Wooden Home Temple for home or office | Price: 259.0 | https://www.kriyanta.com/product-detail/wall-mounted-wooden-

  **Q:** "I need a gift for my sister, she likes services in red or bl" [complex, en]
  **Score:** 9.5/10 | **Products:** 2 | **Sources:** 16
  - Baby Puzzle Candle (Set of 2) | Price: 629.0 | https://www.kriyanta.com/product-detail/baby-puzzle-candle-s
  - Peony Bud Candle ( Set of 3 ) | Price: 399.0 | https://www.kriyanta.com/product-detail/peony-bud-candle-set

  **Q:** "मेरी बहन के लिए services चाहिए, लाल या नीला रंग, 2000 रुपये " [complex, hi]
  **Score:** 5.5/10 | **Products:** 7 | **Sources:** 16
  - Home Decor | Price: inr 999 | https://www.kriyanta.com/category-view/decor
  - Gifting | Price: inr 999 | https://www.kriyanta.com/category-view/gifting
  - Personalized Gifting | Price: inr 999 | https://www.kriyanta.com/category-view/personalised
  Issues: Failed to handle multi-intent complex query fully

  **Q:** "What's the difference between your cheapest and most expensi" [comparison, en]
  **Score:** 9.5/10 | **Products:** 10 | **Sources:** 16
  - Customized Items | Price: 999.0 | https://www.kriyanta.com/category-view/customized
  - Home Decor | Price: 999.0 | https://www.kriyanta.com/category-view/decor
  - Personalized Gifting | Price: 999.0 | https://www.kriyanta.com/category-view/personalised

  **Q:** "Do you have services in size L or XL?" [variant_query, en]
  **Score:** 7.5/10 | **Products:** 2 | **Sources:** 3
  - Bowl Big | Price: 3920.0 | https://www.kriyanta.com/product-detail/bowl-big
  - Bowl Small | Price: 2520.0 | https://www.kriyanta.com/product-detail/bowl-small

  **Q:** "services mein kya sizes available hain?" [variant_query, hi_roman]
  **Score:** 7/10 | **Products:** 0 | **Sources:** 6

### kids (Kids/Toys)
- Product queries tested: 12
- Queries returning products: 6/12 (50%)

  **Q:** "Show me your best toys" [product_browse, en]
  **Score:** 10/10 | **Products:** 10 | **Sources:** 12
  - Kids Toys -1 | Price: 260.0 | https://www.cheaperzonetoys.com/kids-toys-1.html
  - Kids Toys | Price: 350.0 | https://www.cheaperzonetoys.com/kids-toys.html
  - Baby Toys | Price: 190.0 | https://www.cheaperzonetoys.com/baby-toys.html

  **Q:** "What board games do you have available?" [product_browse, en]
  **Score:** 10/10 | **Products:** 10 | **Sources:** 12
  - Board Games | Price: 110.0 | https://www.cheaperzonetoys.com/board-games.html
  - Kids Games | Price: 110.0 | https://www.cheaperzonetoys.com/kids-games.html
  - Activity Toys | Price: 470.0 | https://www.cheaperzonetoys.com/activity-toys.html

  **Q:** "आपके पास कौन से toys उपलब्ध हैं?" [product_browse, hi]
  **Score:** 2/10 | **Products:** 0 | **Sources:** 0
  Issues: No products/sources for product query

  **Q:** "તમારી પાસે કયા toys છે?" [product_browse, gu]
  **Score:** 2/10 | **Products:** 0 | **Sources:** 0
  Issues: No products/sources for product query

  **Q:** "I'm looking for a black toys" [specific_product, en]
  **Score:** 10/10 | **Products:** 7 | **Sources:** 12
  - Soft Toys | Price: 55.0 | https://www.cheaperzonetoys.com/soft-toys.html
  - Toys | Price: 845.0 | https://www.cheaperzonetoys.com/toys.html
  - Kids Toys | Price: 350.0 | https://www.cheaperzonetoys.com/kids-toys.html

  **Q:** "मुझे toys चाहिए जो बहुत अच्छी क्वालिटी का हो" [specific_product, hi]
  **Score:** 2/10 | **Products:** 0 | **Sources:** 0
  Issues: No products/sources for product query

  **Q:** "Show me toys under ₹500" [price_query, en]
  **Score:** 9.5/10 | **Products:** 10 | **Sources:** 12
  - Kids Games | Price: 110.0 | https://www.cheaperzonetoys.com/kids-games.html
  - Baby Toys | Price: 190.0 | https://www.cheaperzonetoys.com/baby-toys.html
  - Kitchen Set | Price: 220.0 | https://www.cheaperzonetoys.com/kitchen-set.html

  **Q:** "What's the price range for your board games?" [price_query, en]
  **Score:** 9.5/10 | **Products:** 10 | **Sources:** 12
  - Activity Toys | Price: 470.0 | https://www.cheaperzonetoys.com/activity-toys.html
  - Board Games | Price: 110.0 | https://www.cheaperzonetoys.com/board-games.html
  - Kids Games | Price: 110.0 | https://www.cheaperzonetoys.com/kids-games.html

  **Q:** "500 रुपये से कम के toys बताओ" [price_query, hi]
  **Score:** 2/10 | **Products:** 0 | **Sources:** 0
  Issues: No price info for price query

  **Q:** "₹1000 થી ઓછા toys બતાવો" [price_query, gu]
  **Score:** 2/10 | **Products:** 0 | **Sources:** 0
  Issues: No price info for price query

  **Q:** "I need a gift for my sister, she likes toys in red or blue, " [complex, en]
  **Score:** 10/10 | **Products:** 10 | **Sources:** 16
  - Kids Games | Price: 110.0 | https://www.cheaperzonetoys.com/kids-games.html
  - Activity Toys | Price: 470.0 | https://www.cheaperzonetoys.com/activity-toys.html
  - Kids Toys | Price: 350.0 | https://www.cheaperzonetoys.com/kids-toys.html

  **Q:** "मेरी बहन के लिए toys चाहिए, लाल या नीला रंग, 2000 रुपये से क" [complex, hi]
  **Score:** 3/10 | **Products:** 0 | **Sources:** 0
  Issues: Failed to handle multi-intent complex query fully


---
## Suggestions Analysis

- Queries with suggestions: 82/128 (64%)
- Queries without suggestions: 46/128

**Sample suggestions (first 30):**
- Show me your best-selling shirts
- What's the price range of your shirts?
- Mare ramraj ni shirts kayi prakar ni chhe?
- Kya sare products available chhe?
- What's the most popular shirt style?
- Do you have any shirts with unique designs?
- What are the different fabrics used for dhotis?
- Do you have dhotis in various colors?
- રંગની શર્ટ કયા છે?
- કયા સાઇઝ મળે છે?
- આ બધામાંથી સૌથી popular કયો છે?
- Discount version મળે છે?
- What are the different materials available?
- Do you have any black shirts under $50?
- What are the different colors available?
- Can I get a slim fit premium cotton shirt?
- Aa shirts ni price ketli chhe?
- Best seller shirts shu chhe?
- Do you have any dhotis on sale?
- What fabrics do your dhotis come in?
- આ બધામાંથી સૌથી popular કયો છે?
- Discount version મળે છે?
- What's the deadline to return an item?
- Can I exchange instead of returning?
- What's the estimated delivery time for in-stock items?
- Do you offer express shipping options?
- What's the price range for these shirts?
- Do you have any gift wrapping options?
- કયો રંગ સૌથી વધારે વેચાય છે?
- સૌથી સસ્તું ઓપ્શન શું છે?

---
## Issues and Failures Summary

**Total issues found:** 55

### Issue: ERROR: ('Connection aborted.', ConnectionResetError(10054, ' (18 occurrences)
| Site | Query Type | Language | Query | Score |
|---|---|---|---|---|
| ramraj | non_product | en | Do you offer cash on delivery? | 0/10 |
| ramraj | non_product | hi | रिटर्न पॉलिसी क्या है? | 0/10 |
| ramraj | complex | en | I need a gift for my sister, she likes s | 0/10 |
| ramraj | about_brand | hi | ramraj के बारे में बताओ | 0/10 |
| truff | irrelevant | hi | भारत का प्रधानमंत्री कौन है? | 0/10 |
| truff | ambiguous | en | What do you recommend for someone new he | 0/10 |
| kriyanta | irrelevant | en | What is the capital of France? | 0/10 |
| kriyanta | irrelevant | en | Can you write me a Python script to sort | 0/10 |
| kriyanta | irrelevant | hi | भारत का प्रधानमंत्री कौन है? | 0/10 |
| kriyanta | irrelevant | en | What's the weather like in Tokyo today? | 0/10 |
| kriyanta | ambiguous | en | I want something nice for a gift | 0/10 |
| kriyanta | ambiguous | en | What do you recommend for someone new he | 0/10 |
| kriyanta | ambiguous | hi | कुछ अच्छा बताओ ना | 0/10 |
| kriyanta | context_start | en | Show me your most popular services | 0/10 |
| kriyanta | about_brand | en | Tell me about kriyanta and what you sell | 0/10 |
| ... | ... | ... | +3 more | ... |

### Issue: ERROR: ('Connection aborted.', RemoteDisconnected('Remote en (7 occurrences)
| Site | Query Type | Language | Query | Score |
|---|---|---|---|---|
| truff | non_product | en | Do you offer cash on delivery? | 0/10 |
| truff | non_product | hi | रिटर्न पॉलिसी क्या है? | 0/10 |
| truff | irrelevant | en | What is the capital of France? | 0/10 |
| truff | irrelevant | en | Can you write me a Python script to sort | 0/10 |
| kriyanta | greeting | hi_roman | hello bhai, kya help kar sakte ho? | 0/10 |
| kriyanta | product_browse | en | Show me your best services | 0/10 |
| kriyanta | product_browse | hi | आपके पास कौन से services उपलब्ध हैं? | 0/10 |

### Issue: No warning about unsupported language (6 occurrences)
| Site | Query Type | Language | Query | Score |
|---|---|---|---|---|
| ramraj | unsupported_lang | fr | Bonjour, montrez-moi vos produits les pl | 4/10 |
| ramraj | unsupported_lang | ja | こんにちは、人気商品を教えてください | 4/10 |
| truff | unsupported_lang | fr | Bonjour, montrez-moi vos produits les pl | 4/10 |
| kriyanta | unsupported_lang | fr | Bonjour, montrez-moi vos produits les pl | 4/10 |
| kriyanta | unsupported_lang | ja | こんにちは、人気商品を教えてください | 4/10 |
| kids | unsupported_lang | fr | Bonjour, montrez-moi vos produits les pl | 4/10 |

### Issue: No products/sources for product query (6 occurrences)
| Site | Query Type | Language | Query | Score |
|---|---|---|---|---|
| truff | product_browse | hi | आपके पास कौन से hot sauce उपलब्ध हैं? | 2/10 |
| truff | product_browse | gu | તમારી પાસે કયા hot sauce છે? | 2/10 |
| truff | specific_product | hi | मुझे hot sauce चाहिए जो बहुत अच्छी क्वाल | 2/10 |
| kids | product_browse | hi | आपके पास कौन से toys उपलब्ध हैं? | 2/10 |
| kids | product_browse | gu | તમારી પાસે કયા toys છે? | 2/10 |
| kids | specific_product | hi | मुझे toys चाहिए जो बहुत अच्छी क्वालिटी क | 2/10 |

### Issue: Failed to handle multi-intent complex query fully (4 occurrences)
| Site | Query Type | Language | Query | Score |
|---|---|---|---|---|
| ramraj | complex | hi | मेरी बहन के लिए shirts चाहिए, लाल या नील | 5.5/10 |
| truff | complex | hi | मेरी बहन के लिए hot sauce चाहिए, लाल या  | 3/10 |
| kriyanta | complex | hi | मेरी बहन के लिए services चाहिए, लाल या न | 5.5/10 |
| kids | complex | hi | मेरी बहन के लिए toys चाहिए, लाल या नीला  | 3/10 |

### Issue: No price info for price query (4 occurrences)
| Site | Query Type | Language | Query | Score |
|---|---|---|---|---|
| truff | price_query | hi | 500 रुपये से कम के hot sauce बताओ | 2/10 |
| truff | price_query | gu | ₹1000 થી ઓછા hot sauce બતાવો | 2/10 |
| kids | price_query | hi | 500 रुपये से कम के toys बताओ | 2/10 |
| kids | price_query | gu | ₹1000 થી ઓછા toys બતાવો | 2/10 |

### Issue: No suggestions generated (3 occurrences)
| Site | Query Type | Language | Query | Score |
|---|---|---|---|---|
| ramraj | suggestions_test | hi | यहां क्या-क्या मिलता है? | 3/10 |
| truff | suggestions_test | hi | यहां क्या-क्या मिलता है? | 3/10 |
| kids | suggestions_test | hi | यहां क्या-क्या मिलता है? | 3/10 |

### Issue: FAILED to detect irrelevant query - bot tried to answer (2 occurrences)
| Site | Query Type | Language | Query | Score |
|---|---|---|---|---|
| ramraj | irrelevant | hi | भारत का प्रधानमंत्री कौन है? | 1/10 |
| kids | irrelevant | en | Can you write me a Python script to sort | 1/10 |

### Issue: Could give better guidance for ambiguous query (2 occurrences)
| Site | Query Type | Language | Query | Score |
|---|---|---|---|---|
| truff | ambiguous | hi | कुछ अच्छा बताओ ना | 4/10 |
| kids | ambiguous | hi | कुछ अच्छा बताओ ना | 4/10 |

### Issue: Sources found but no product cards (2 occurrences)
| Site | Query Type | Language | Query | Score |
|---|---|---|---|---|
| kriyanta | product_browse | gu | તમારી પાસે કયા services છે? | 5.5/10 |
| kriyanta | specific_product | hi | मुझे services चाहिए जो बहुत अच्छी क्वालि | 5/10 |

### Issue: ERROR: ('Connection aborted.', ConnectionAbortedError(10053, (1 occurrences)
| Site | Query Type | Language | Query | Score |
|---|---|---|---|---|
| kriyanta | product_browse | en | What solutions do you have available? | 0/10 |


---
## Sample Responses

Representative responses for each query type.

### Query Type: greeting
**Site:** ramraj | **Lang:** en | **Score:** 9.5/10
**Query:** "Hi there! What can you help me with?"

**Bot Response:**
```
*We've got a fantastic collection of shirts at Ramraj*. You can browse through our **Men Stretch Poly shirts** or **Men Cotton Spandex shirts**. We've got a variety of colors and styles to choose from, like the **Dark Peach PS3** or **Light Pink LY9**. What's on your mind? Are you looking for something specific or just want to explore our collection?


```

**Suggestions:** ['Show me your best-selling shirts', "What's the price range of your shirts?"]

### Query Type: product_browse
**Site:** ramraj | **Lang:** en | **Score:** 10/10
**Query:** "Show me your best shirts"

**Bot Response:**
```
Oh nice, here's what we've got! We've curated a selection of our finest shirts for you to browse through, each one showcasing a unique blend of style and comfort.


```

**Suggestions:** ["What's the most popular shirt style?", 'Do you have any shirts with unique designs?']
**Products:** 8 returned
- Men Cotton Rich Shirt Full Sleeves Green T32 TH8 | 945.0
- Men Cotton Rich Full Sleeves Shirt Mustard T28 TD1 | 945.0

### Query Type: specific_product
**Site:** ramraj | **Lang:** en | **Score:** 10/10
**Query:** "I'm looking for a black shirts"

**Bot Response:**
```
Oh nice, here's what we've got! We have a variety of black shirts from Ramraj that you can check out in our carousel. 

```

**Suggestions:** ['What are the different materials available?', 'Do you have any black shirts under $50?']
**Products:** 8 returned
- Men Cotton Blend Shirt Black MA8 | 835.0
- Men Cotton Blend Shirt Black | 895.0

### Query Type: price_query
**Site:** ramraj | **Lang:** en | **Score:** 9.5/10
**Query:** "What's the price range for your dhotis?"

**Bot Response:**
```
Oh nice, here's what we've got! We've got a variety of dhotis, but I don't have the specific price range for them right now
```

**Suggestions:** ['Do you have any dhotis on sale?', 'What fabrics do your dhotis come in?']
**Products:** 10 returned
- Mens Party Wear Purple Shirt PSS7 | 975.0
- Mens Party Wear Black Shirt PSS5 | 975.0

### Query Type: non_product
**Site:** ramraj | **Lang:** en | **Score:** 8.5/10
**Query:** "What is your return policy?"

**Bot Response:**
```
Hmm, let me check... Unfortunately, I couldn't find any specific information about Ramraj's return policy in our knowledge base. If you're looking to return an item, I recommend checking the product page or reaching out to our support team for more details.

```

**Suggestions:** ["What's the deadline to return an item?", 'Can I exchange instead of returning?']

### Query Type: irrelevant
**Site:** ramraj | **Lang:** en | **Score:** 9/10
**Query:** "What is the capital of France?"

**Bot Response:**
```
Hmm, let me check... Unfortunately, I don't have any information about the capital of France in our context, which is mainly about ramraj products. 
```

**Suggestions:** ['What products do you carry?', 'Tell me about ramraj']

### Query Type: ambiguous
**Site:** ramraj | **Lang:** en | **Score:** 8.5/10
**Query:** "I want something nice for a gift"

**Bot Response:**
```
You're looking for a great gift idea. We've got some fantastic options at Ramraj Cotton. Our **Ramraj Colour Shirts** are a popular choice, and they come in a wide range of vibrant colours and styles. Whether the person you're gifting is into traditional or modern looks, we've got something that's sure to impress. 
- They're made from high-quality cotton, ensuring comfort and durability.
- The collection includes a variety of colours and patterns, so you can choose one that suits the person's ta
```

**Suggestions:** ["What's the price range for these shirts?", 'Do you have any gift wrapping options?']

### Query Type: complex
**Site:** ramraj | **Lang:** en | **Score:** 0/10
**Query:** "I need a gift for my sister, she likes shirts in red or blue, budget around ₹150"

**Bot Response:**
```
(empty)
```


### Query Type: context_start
**Site:** ramraj | **Lang:** en | **Score:** 7.5/10
**Query:** "Show me your most popular shirts"

**Bot Response:**
```
Take a look at these beauties! We've got a great selection of our most popular shirts for you to browse through, all available in the carousel.
```

**Suggestions:** ['Which of these shirts is the best seller?', 'Do any of these come in a different color?']
**Products:** 8 returned
- Men Cotton Rich Shirt Green Trendy 8 YH1 | 775.0
- Men Cotton Rich Shirt Full Sleeves Green T32 TH8 | 945.0

### Query Type: context_followup
**Site:** ramraj | **Lang:** en | **Score:** 7.5/10
**Query:** "Do you have this in a different color?"

**Bot Response:**
```
We've got a range of colors for you to choose from - take a look at these beauties!
```

**Suggestions:** ['Which color is the most popular among customers?', 'Can I see a comparison of all the colors?']
**Products:** 8 returned
- Men Stretch Poly Shirt Olive Green PS1 | 975.0
- Men Stretch Poly Shirt Grayish Green PS8 | 975.0

### Query Type: context_summary
**Site:** ramraj | **Lang:** en | **Score:** 9.5/10
**Query:** "Can you summarize what we've talked about so far?"

**Bot Response:**
```
We've discussed the products available at ramraj, and you've asked about different colors and larger sizes. I didn't have a chance to provide a detailed answer about sizes yet, though - let me check that for you.
```

**Suggestions:** ['What are the largest sizes you offer?', 'Can I get a size chart for these shirts?']

### Query Type: about_brand
**Site:** ramraj | **Lang:** hi | **Score:** 0/10
**Query:** "ramraj के बारे में बताओ"

**Bot Response:**
```
(empty)
```


### Query Type: unsupported_lang
**Site:** ramraj | **Lang:** fr | **Score:** 4/10
**Query:** "Bonjour, montrez-moi vos produits les plus populaires"

**Bot Response:**
```
Oh nice, here's what we've got! We've got quite a range of popular products, let me show you what ramraj has to offer.

```

**Suggestions:** ['Which of these is the best seller?', 'Do any come in a different color?']
**Products:** 8 returned
- Men 100% Cotton Shirt Cream CL2 GT15 | 1045.0
- Men Silk Look Shirt Cream | 995.0

### Query Type: suggestions_test
**Site:** ramraj | **Lang:** en | **Score:** 6.5/10
**Query:** "I'm new here, what kind of things do you sell?"

**Bot Response:**
```
Take a look at these beauties! We've got a wide range of shirts and other apparel from Ramraj, so you're in the right place if you're looking for some great clothing options.
```

**Suggestions:** ['What kind of shirts do you have?', 'Do you carry anything besides clothing?']
**Products:** 10 returned
- Men Cotton Rich Shirt Devotional Culture Club Black | 745.0
- Men Cotton Rich Shirt Devotional Culture Club Kaavi | 745.0

### Query Type: comparison
**Site:** ramraj | **Lang:** en | **Score:** 9.5/10
**Query:** "What's the difference between your cheapest and most expensive shirts?"

**Bot Response:**
```
Take a look at these beauties! Our **colour shirts** range from affordable to premium, with the main differences often being the quality of the fabric, the complexity of the design, and the attention to detail in the craftsmanship.
```

**Suggestions:** ["What's the price range of your colour shirts?", 'Do the more expensive shirts have any special features?']
**Products:** 10 returned
- Men Cotton Rich Shirt Green Trendy 8 YH1 | 775.0
- Men Cotton Rich Shirt Light Purple T61 AKT3 | 895.0

### Query Type: variant_query
**Site:** ramraj | **Lang:** en | **Score:** 7.5/10
**Query:** "Do you have shirts in size L or XL?"

**Bot Response:**
```
We've got a range of shirts in different sizes. Check these out!
```

**Suggestions:** ['Which of these shirts is the most comfortable?', 'Do you have any XL shirts on sale?']
**Products:** 8 returned
- Men Linen Cotton Shirt Yellowish Green LF9 | 1350.0
- Men Linen Cotton Shirt Maroon LF14 | 1350.0

### Query Type: urgency
**Site:** ramraj | **Lang:** en | **Score:** 7.5/10
**Query:** "I need shirts urgently for tomorrow, can you deliver that fast?"

**Bot Response:**
```
We've got you covered for urgent deliveries. Check these out and see which ones are available for quick shipping. 

```

**Suggestions:** ['Do you offer same-day delivery?', "What's the latest time I can order for tomorrow?"]
**Products:** 8 returned
- Men Cotton Rich Shirt LT Beige Grey T61 AKT5 | 895.0
- Men's Cotton Rich Knit Shirt Navy | 1295.0

### Query Type: complaint
**Site:** ramraj | **Lang:** en | **Score:** 8.5/10
**Query:** "I received a damaged shirts, what should I do?"

**Bot Response:**
```
Oh no, sorry to hear that! You can definitely get in touch with our customer support team to initiate a return or exchange process for the damaged shirt.

```

**Suggestions:** ["What's the deadline to return an item?", 'Can I exchange instead of returning?']
**Products:** 8 returned
- Men's Cotton Rich Knit Shirt Navy | 1295.0
- Men Cotton Rich Shirt Full Sleeves Green T32 TH8 | 945.0


---
## Conversation Context Analysis

Testing whether the bot maintains conversation context across messages.

### ramraj

**[context_start]** "Show me your most popular shirts"
Score: 7.5/10
```
Take a look at these beauties! We've got a great selection of our most popular shirts for you to browse through, all available in the carousel.
```

**[context_followup]** "Do you have this in a different color?"
Score: 7.5/10
```
We've got a range of colors for you to choose from - take a look at these beauties!
```

**[context_followup]** "What about a larger size?"
Score: 7.5/10
```
Oh nice, here's what we've got! Our shirts usually come in a variety of sizes, but let me check the specific one you're looking at - I can see if we have a larger size available for you.

```

**[context_summary]** "Can you summarize what we've talked about so far?"
Score: 9.5/10
```
We've discussed the products available at ramraj, and you've asked about different colors and larger sizes. I didn't have a chance to provide a detailed answer about sizes yet, though - let me check that for you.
```

### truff

**[context_start]** "Show me your most popular hot sauce"
Score: 7.5/10
```
Oh nice, here's what we've got! Take a look at these beauties! 

```

**[context_followup]** "Do you have this in a different color?"
Score: 7.5/10
```
Our **TRUFF White Truffle Hot Sauce** is a fan favorite, and it comes in a special edition white and gold VIP box. As for different colors, we don't have this specific sauce in other colors, but we do have other hot sauce options with unique packaging. 

```

**[context_followup]** "What about a larger size?"
Score: 7.5/10
```
We've got a range of sizes for our hot sauces, but unfortunately, the specific details on larger sizes for the **TRUFF White Truffle Hot Sauce** aren't available here 
```

### kriyanta

**[context_start]** "Show me your most popular services"
Score: 0/10
```
(empty)
```
Issues: ERROR: ('Connection aborted.', ConnectionResetError(10054, 'An existing connection was forcibly closed by the remote host', None, 10054, None))

**[context_followup]** "Do you have this in a different color?"
Score: 7.5/10
```
We've got a variety of colors for some of our products, but I'd need to check the specific one you're interested in. Since we've got **Handmade Treasures from Over 350 Indian Artists**, it's possible that some of these artists might have created the same product in different colors. Can you tell me 
```

**[context_followup]** "What about a larger size?"
Score: 7.5/10
```
Check these out! We've got a range of sizes available for many of our products, so you can find the perfect fit for your space.
```

**[context_summary]** "Can you summarize what we've talked about so far?"
Score: 9.5/10
```
We've had a quick chat so far - you initially asked if a product is available in a different color, and then inquired about the possibility of getting it in a larger size. That's about it for now!
```

### kids

**[context_start]** "Show me your most popular toys"
Score: 7.5/10
```
Oh nice, here's what we've got! We've got quite a range of popular toys that kids love, and I can show you some of our best sellers.

```

**[context_followup]** "Do you have this in a different color?"
Score: 7.5/10
```
Take a look at these beauties! Since we have a variety of products, the color options might differ for each one - let me see what's available for the specific toy you're interested in. 

```

**[context_followup]** "What about a larger size?"
Score: 7.5/10
```
Check these out! I found these for you! 

```

**[context_summary]** "Can you summarize what we've talked about so far?"
Score: 9.5/10
```
We've had a chat about the products available, and you asked about different colors and larger sizes. That's about it so far! 


```


---
## Multi-Language Handling Analysis

### Hindi (Devanagari)
- Queries: 37 | Avg Score: 3.5/10 | Passed: 16/37
  - **Q:** "नमस्ते! आप मेरी कैसे मदद कर सकते हैं?" -> Score: 8/10
    Response: નમસ્તે! મેં તમને રામરાજ પ્રોડક્ટ્સ વિશે માહિતી આપી શકું છું. તમે કયા પ્રોડક્ટ વિશે જાણવા માંગો છો? જેમકે, **Men Cotton Spandex Shirt** અથવા **Men Stre...
  - **Q:** "आपके पास कौन से shirts उपलब्ध हैं?" -> Score: 10/10
    Response: અરે, ઘણા saras ઓપ્શન છે! જુઓ ramraj પાસે શું છે.
...
  - **Q:** "रिटर्न पॉलिसी क्या है?" -> Score: 0/10

### Hindi (Romanized)
- Queries: 10 | Avg Score: 8.0/10 | Passed: 9/10
  - **Q:** "hello bhai, kya help kar sakte ho?" -> Score: 9.5/10
    Response: Are, namaste! Haan bhai, main tamaru ramraj ni shopping madhe help karu chhu. Juo product tne search karo chho, te batavo, hju main tamaru sahi guidan...
  - **Q:** "best quality shirts dikhao" -> Score: 10/10
    Response: Oh nice, best quality shirts tamne dikhavu! Ramraj ne saras collection chhe, jo **high-quality** fabrics thi bani chhe. 
...
  - **Q:** "shirts mein kya sizes available hain?" -> Score: 7/10
    Response: Ahiya ketlak saras options chhe! Ramraj mein **S**, **M**, **L**, **XL**, **XXL** jevu sizes available chhe....

### Gujarati
- Queries: 7 | Avg Score: 4.7/10 | Passed: 3/7
  - **Q:** "તમારી પાસે કયા shirts છે?" -> Score: 10/10
    Response: અહીં કેટલાક સરસ ઓપ્શન છે! આ પર એક નજર નાખો!
...
  - **Q:** "₹1000 થી ઓછા shirts બતાવો" -> Score: 9.5/10
    Response: અરે, ઘણા saras options છે! જુઓ ramraj પાસે શું છે....
  - **Q:** "તમારી પાસે કયા hot sauce છે?" -> Score: 2/10
    Response: I'm sorry, Gujarati (ગુજરાતી) is not supported. I can help you in English. Please ask your question in one of the supported languages....

### French
- Queries: 4 | Avg Score: 4.0/10 | Passed: 4/4
  - **Q:** "Bonjour, montrez-moi vos produits les plus populai" -> Score: 4/10
    Response: Oh nice, here's what we've got! We've got quite a range of popular products, let me show you what ramraj has to offer.
...
  - **Q:** "Bonjour, montrez-moi vos produits les plus populai" -> Score: 4/10
    Response: Oh nice, here's what we've got! I'd be happy to show you our most popular **truff** products.

...
  - **Q:** "Bonjour, montrez-moi vos produits les plus populai" -> Score: 4/10
    Response: Oh nice, here's what we've got! Take a look at these beauties, and you'll find our most popular items showcased in the carousel....

### Japanese
- Queries: 2 | Avg Score: 4.0/10 | Passed: 2/2
  - **Q:** "こんにちは、人気商品を教えてください" -> Score: 4/10
    Response: Oh nice, here's what we've got! We've found some popular products for you, take a look at these beauties!...
  - **Q:** "こんにちは、人気商品を教えてください" -> Score: 4/10
    Response: Oh nice, here's what we've got! We've found some great products for you, take a look at these beauties!
...


---
## Real Bot Quality Issues (Excluding Infrastructure Errors)

These are the genuine failures where the bot gave a wrong or poor response (not ConnectionReset errors):

### 1. Irrelevant Query Detection Failures
- **"What is the capital of France?"** — truff bot answered with product info instead of declining (0/10)
- **"Can you write me a Python script?"** — truff bot answered with product info (0/10), kids bot scored 1/10
- **"भारत का प्रधानमंत्री कौन है?"** (Hindi: Who is PM of India?) — ramraj bot tried to answer (1/10), truff scored 0/10
- **Root cause:** The irrelevant detection in the unified LLM call isn't working reliably. When it does work (English for ramraj: 9/10), it's great. But it fails for 2 out of 4 bots.

### 2. Hindi/Gujarati Queries Return Empty Results
- **truff:** "आपके पास कौन से hot sauce उपलब्ध हैं?" → 0 products, 0 sources (2/10)
- **truff:** "₹1000 થી ઓછા hot sauce બતાવો" → 0 products, 0 sources (2/10)
- **kids:** "आपके पास कौन से toys उपलब्ध हैं?" → 0 products, 0 sources (2/10)
- **Root cause:** The Hindi/Gujarati → English translation in the unified LLM call may not be producing good search queries. The embedding search then finds nothing relevant.

### 3. Unsupported Language Not Warned
- **French "Bonjour, montrez-moi vos produits"** — All 4 bots happily responded with products in English instead of warning "French is not supported" (4/10 each)
- **Japanese queries** — Same behavior: responded in English with products
- **Root cause:** Language detection works, but there's no enforcement to reject unsupported languages

### 4. No Suggestions for Hindi Queries
- **"यहां क्या-क्या मिलता है?"** — 3/10 for ramraj, truff, kids (no suggestions generated)
- **Root cause:** When the bot responds in Gujarati (which it tends to do for Hindi queries), suggestion generation may fail

### 5. Complex Query Multi-Intent Handling
- **ramraj Hindi complex query** — Only addressed 1 of 4 aspects (color, budget, product, policy) → 5.5/10
- **truff Hindi complex query** — Only addressed 0 aspects → 3/10
- **Root cause:** Hindi complex queries lose information during translation

### 6. About Brand Queries Fail Under Load
- **kriyanta "Tell me about kriyanta"** — ConnectionError (likely key switch timing)
- **ramraj Hindi "ramraj के बारे में बताओ"** — ConnectionError
- When these work (truff English: 8.5/10), the brand info is good

---
## Recommendations and Improvements

### [HIGH] Irrelevant Query Detection
**Problem:** Average score 3.7/10 for irrelevant queries. Bot tries to answer off-topic questions.
**Fix:** 1) Strengthen system prompt to firmly decline off-topic queries. 2) Add confidence threshold — when retrieval scores are very low across all chunks, default to 'outside my knowledge'. 3) If query analysis detects intent='irrelevant', short-circuit to a polite decline without KB search.

### [HIGH] Product Card Display
**Problem:** Product browsing score 5.6/10. Product cards may not be extracted from crawled content.
**Fix:** 1) Improve product extraction — parse JSON-LD, Open Graph, and microdata from crawled pages. 2) Detect product pages by URL patterns (/product/, /p/, /item/). 3) Store structured product data (name, price, image, URL) during crawl for reliable product card display.

### [HIGH] Hindi Performance Gap
**Problem:** Hindi avg 4.5 vs English avg 7.0. Hindi queries underperform.
**Fix:** 1) Ensure query translation in unified LLM call produces good English queries for KB search. 2) Add Hindi few-shot examples in system prompt. 3) Consider bilingual embedding model.

### [HIGH] Rate Limiting / API Key Management
**Problem:** 20 queries were rate-limited.
**Fix:** 1) Implement API key rotation in the chat service itself. 2) Add request queuing and backoff. 3) Consider using a cheaper/unlimited LLM for simple queries (greetings, irrelevant detection).

### [HIGH] Crawl Failures
**Problem:** 3 sites failed to crawl: Boat Lifestyle, Sugar Cosmetics, Mokobara
**Fix:** 1) Auto-detect sitemap.xml and use it as crawl source. 2) Better JS rendering for SPA sites. 3) User-agent rotation. 4) Give clear warnings about blocked/JS-heavy sites. 5) Automatic retry with headless browser for failed HTML-only crawls.

### [MEDIUM] Gujarati Performance Gap
**Problem:** Gujarati avg 4.7 vs English avg 7.0.
**Fix:** Same as Hindi recommendations. Gujarati may need extra translation quality checks.

### [MEDIUM] Non-Product Query Handling
**Problem:** Policy/info queries score 5.6/10.
**Fix:** 1) Ensure crawler follows links to /policy, /faq, /shipping, /about pages. 2) Prioritize these pages in crawl. 3) Add explicit FAQ extraction from crawled content.

### [LOW] General Improvements
**Problem:** General observations from testing.
**Fix:** 1) Add confidence scores in API response for debugging. 2) Improve response formatting consistency. 3) Add response quality logging. 4) Consider caching frequent queries within same chatbot.
