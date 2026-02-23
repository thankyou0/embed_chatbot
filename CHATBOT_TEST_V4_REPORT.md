# Chatbot Test Suite v4 — OpenRouter + Full Algorithm Analysis

**Generated:** 2026-02-21 13:25:15
**LLM Provider:** OpenRouter (google/gemini-2.0-flash-001)
**Bots tested:** 6

## Executive Summary

| Metric | Value |
|--------|-------|
| Total queries | **558** |
| Passed (≥5/10) | **484** (86%) |
| Failed (<5/10) | **42** (7%) |
| Skipped (rate limit) | 32 |
| Critical issues | 0 |
| Language mismatches | 7 |
| Price format bugs | 0 |

## Score Breakdown by Query Type

| Query Type | Total | Passed | Failed | Avg Score | Pass Rate |
|------------|-------|--------|--------|-----------|-----------|
| about_brand | 14 | 12 | 0 | 8.0 | 100% |
| ambiguous | 30 | 28 | 0 | 7.7 | 100% |
| color_filter | 24 | 24 | 0 | 7.8 | 100% |
| comparison | 18 | 15 | 1 | 8.6 | 93% |
| complaint | 18 | 15 | 0 | 7.6 | 100% |
| edge_case | 48 | 42 | 0 | 7.0 | 100% |
| greeting | 30 | 30 | 0 | 9.0 | 100% |
| irrelevant | 72 | 64 | 4 | 8.8 | 94% |
| missing_info | 42 | 33 | 6 | 6.2 | 84% |
| mixed_lang | 12 | 10 | 0 | 7.0 | 100% |
| non_product | 48 | 38 | 9 | 7.0 | 80% |
| price_filter | 42 | 39 | 3 | 7.5 | 92% |
| price_format | 18 | 15 | 0 | 7.3 | 100% |
| product_browse | 48 | 45 | 3 | 8.3 | 93% |
| romanized | 18 | 16 | 0 | 8.0 | 100% |
| specific_product | 24 | 23 | 1 | 8.3 | 95% |
| suggestions_test | 18 | 1 | 15 | 3.2 | 6% |
| unsupported_lang | 24 | 24 | 0 | 10.0 | 100% |
| unsupported_lang_gujarati | 2 | 2 | 0 | 10.0 | 100% |
| unsupported_lang_hindi | 8 | 8 | 0 | 10.0 | 100% |

## Per-Bot Results

### ramraj (Fashion/Clothing (Indian))
- **Languages:** ['en', 'gu']
- **Queries:** 93 | Pass: 85 | Fail: 8 | Skip: 0
- **Average score:** 7.7/10

| # | Type | Lang | Query | Score | Status | Notes |
|---|------|------|-------|-------|--------|-------|
| 1 | greeting | en | Hi there! | 9/10 | ✅ | - |
| 2 | greeting | en | Hey, what's up? | 9/10 | ✅ | - |
| 3 | greeting | en | Good morning! Can you help me? | 9/10 | ✅ | - |
| 4 | greeting | gu | નમસ્તે! કેમ છો? | 9/10 | ✅ | - |
| 5 | greeting | gu | હેલો! મને હેલ્પ કરો | 9/10 | ✅ | - |
| 6 | product_browse | en | Show me your shirts | 9/10 | ✅ | 4 products |
| 7 | product_browse | en | What dhotis do you have? | 6/10 | ✅ | Mentioned products textually |
| 8 | product_browse | en | I want to browse your collection | 6/10 | ✅ | Mentioned products textually |
| 9 | product_browse | en | What's popular right now? | 6/10 | ✅ | Mentioned products textually |
| 10 | product_browse | en | Show me your best sellers | 9/10 | ✅ | 5 products |
| 11 | product_browse | gu | તમારા shirts બતાવો | 9/10 | ✅ | 4 products |
| 12 | product_browse | gu | શું dhotis available છે? | 4/10 | ❌ | No products returned or mentioned |
| 13 | product_browse | gu | તમારા best selling products કયા છે? | 6/10 | ✅ | Mentioned products textually |
| 14 | specific_product | en | I need a premium shirts | 9/10 | ✅ | 8 products |
| 15 | specific_product | en | Looking for cotton shirts for daily use | 9/10 | ✅ | 10 products |
| 16 | specific_product | en | Do you have formal shirts in stock? | 9/10 | ✅ | 8 products |
| 17 | specific_product | gu | મને shirts જોઈએ છે | 9/10 | ✅ | 1 products |
| 18 | price_filter | en | Show me shirts under $50 | 9/10 | ✅ | - |
| 19 | price_filter | en | shirts between $20 and $100 | 9/10 | ✅ | - |
| 20 | price_filter | en | What's the cheapest dhotis? | 6/10 | ✅ | - |
| 21 | price_filter | en | Budget shirts under 500 | 6/10 | ✅ | - |
| 22 | price_filter | en | Most expensive shirts you have? | 7/10 | ✅ | - |
| 23 | price_filter | gu | ₹500 થી ઓછા shirts બતાવો | 7/10 | ✅ | - |
| 24 | price_filter | gu | સસ્તા shirts છે? | 7/10 | ✅ | - |
| 25 | color_filter | en | Show me shirts in blue | 8/10 | ✅ | 8 products |
| 26 | color_filter | en | Do you have black shirts? | 8/10 | ✅ | 8 products |
| 27 | color_filter | en | I want a red dhotis | 6/10 | ✅ | - |
| 28 | color_filter | gu | લાલ રંગના shirts બતાવો | 8/10 | ✅ | 8 products |
| 29 | non_product | en | What is your return policy? | 7/10 | ✅ | Correctly flagged as missing info |
| 30 | non_product | en | How long does shipping take? | 7/10 | ✅ | Correctly flagged as missing info |
| 31 | non_product | en | Do you offer free delivery? | 8/10 | ✅ | - |
| 32 | non_product | en | What payment methods do you accept? | 7/10 | ✅ | Correctly flagged as missing info |
| 33 | non_product | en | Where are you located? | 8/10 | ✅ | - |
| 34 | non_product | en | Do you have a physical store? | 8/10 | ✅ | - |
| 35 | non_product | gu | રિટર્ન પોલિસી શું છે? | 4/10 | ❌ | - |
| 36 | non_product | gu | ડિલિવરી કેટલા દિવસમાં થાય? | 4/10 | ❌ | - |
| 37 | irrelevant | en | Can you write me a Python script to sort a li | 10/10 | ✅ | Correctly rejected |
| 38 | irrelevant | en | Who is the Prime Minister of India? | 10/10 | ✅ | Correctly rejected |
| 39 | irrelevant | en | What is the capital of France? | 10/10 | ✅ | Correctly rejected |
| 40 | irrelevant | en | Tell me a joke about programming | 10/10 | ✅ | Correctly rejected |
| 41 | irrelevant | en | Explain quantum physics to me | 10/10 | ✅ | Correctly rejected |
| 42 | irrelevant | en | What's the weather like today? | 10/10 | ✅ | Correctly rejected |
| 43 | irrelevant | en | Who won the FIFA World Cup 2022? | 10/10 | ✅ | Correctly rejected |
| 44 | irrelevant | en | How do I make pasta at home? | 10/10 | ✅ | Correctly rejected |
| 45 | irrelevant | en | What is blockchain technology? | 10/10 | ✅ | Correctly rejected |
| 46 | irrelevant | en | Solve this math: 25 x 48 | 10/10 | ✅ | Correctly rejected |
| 47 | irrelevant | gu | ભારતના વડાપ્રધાન કોણ છે? | 10/10 | ✅ | Expected Gujarati response but got non-Gujarati |
| 48 | irrelevant | gu | મને એક જોક કહો | 2/10 | ❌ | Bot answered irrelevant question instead of rejecting |
| 49 | unsupported_lang | fr | Bonjour, montrez-moi vos produits les plus po | 10/10 | ✅ | Correctly rejected unsupported language |
| 50 | unsupported_lang | ja | こんにちは、人気商品を教えてください | 10/10 | ✅ | Correctly rejected unsupported language |
| 51 | unsupported_lang | es | Hola, muéstrame tus productos más vendidos | 10/10 | ✅ | Correctly rejected unsupported language |
| 52 | unsupported_lang | zh | 你好，给我看看你们最好的产品 | 10/10 | ✅ | Correctly rejected unsupported language |
| 53 | unsupported_lang_hindi | hi | नमस्ते! आपके पास कौन से shirts हैं? | 10/10 | ✅ | Correctly rejected unsupported language |
| 54 | unsupported_lang_hindi | hi | 500 रुपये से कम में क्या मिलेगा? | 10/10 | ✅ | Correctly rejected unsupported language |
| 55 | missing_info | en | Show me your product warranty certificates | 7/10 | ✅ | Honestly said info unavailable (no marker) |
| 56 | missing_info | en | What is the GSM rating of your cotton fabric? | 7/10 | ✅ | Honestly said info unavailable (no marker) |
| 57 | missing_info | en | What are your CEO's contact details? | 7/10 | ✅ | Honestly said info unavailable (no marker) |
| 58 | missing_info | en | What year was your company founded? | 7/10 | ✅ | Honestly said info unavailable (no marker) |
| 59 | missing_info | en | Can you show your ISO certification? | 7/10 | ✅ | Honestly said info unavailable (no marker) |
| 60 | missing_info | en | What's the thread count of your premium fabri | 7/10 | ✅ | Honestly said info unavailable (no marker) |
| 61 | missing_info | gu | તમારી company નો GST number શું છે? | 2/10 | ❌ | Bot fabricated info instead of flagging missing |
| 62 | suggestions_test | en | I'm new here, what shirts do you sell? | 3/10 | ❌ | No suggestions returned |
| 63 | suggestions_test | en | What do you recommend for a gift? | 3/10 | ❌ | No suggestions returned |
| 64 | suggestions_test | gu | gift માટે શું recommend કરો? | 3/10 | ❌ | No suggestions returned |
| 65 | romanized | gu-Latn | mane shirts batavo | 8/10 | ✅ | Response received for romanized input |
| 66 | romanized | gu-Latn | sasta wala shu chhe? | 8/10 | ✅ | Response received for romanized input |
| 67 | romanized | gu-Latn | tamari best products batavo | 8/10 | ✅ | Response received for romanized input |
| 68 | mixed_lang | gu-mix | Mane shirts joiye affordable wala | 7/10 | ✅ | Handled mixed-language query |
| 69 | mixed_lang | gu-mix | tumhare best products shu chhe? | 7/10 | ✅ | Handled mixed-language query |
| 70 | ambiguous | en | something nice | 8/10 | ✅ | Handled ambiguous query |
| 71 | ambiguous | en | I need help | 7/10 | ✅ | Handled ambiguous query |
| 72 | ambiguous | en | What do you have? | 8/10 | ✅ | Handled ambiguous query |
| 73 | ambiguous | en | show me options | 8/10 | ✅ | Handled ambiguous query |
| 74 | ambiguous | en | gift ideas | 7/10 | ✅ | Handled ambiguous query |
| 75 | comparison | en | Which shirts is better quality? | 9/10 | ✅ | Showed 8 products for comparison |
| 76 | comparison | en | What's the difference between your shirts and | 9/10 | ✅ | Showed 10 products for comparison |
| 77 | comparison | en | Which shirts would you recommend? | 9/10 | ✅ | Showed 8 products for comparison |
| 78 | edge_case | en | ok | 7/10 | ✅ | Handled edge case gracefully |
| 79 | edge_case | en | thanks | 7/10 | ✅ | Handled edge case gracefully |
| 80 | edge_case | en | yes | 7/10 | ✅ | Handled edge case gracefully |
| 81 | edge_case | en | no | 7/10 | ✅ | Handled edge case gracefully |
| 82 | edge_case | en | hmm | 7/10 | ✅ | Handled edge case gracefully |
| 83 | edge_case | en | ??? | 7/10 | ✅ | Handled edge case gracefully |
| 84 | edge_case | en | lol | 7/10 | ✅ | Handled edge case gracefully |
| 85 | edge_case | en | shirts | 7/10 | ✅ | Handled edge case gracefully |
| 86 | about_brand | en | Tell me about ramraj | 8/10 | ✅ | - |
| 87 | about_brand | en | Who are you and what do you sell? | 8/10 | ✅ | - |
| 88 | complaint | en | Your products are too expensive | 6/10 | ✅ | - |
| 89 | complaint | en | I had a bad experience with my last order | 8/10 | ✅ | Empathetic response |
| 90 | complaint | en | Why is the quality so poor? | 8/10 | ✅ | Empathetic response |
| 91 | price_format | en | Show me shirts with prices | 7/10 | ✅ | - |
| 92 | price_format | en | What's the price range of your products? | 6/10 | ✅ | - |
| 93 | price_format | gu | shirts ની price શું છે? | 7/10 | ✅ | Expected Gujarati response but got non-Gujarati |

### kriyanta (Tech/Startup)
- **Languages:** ['en', 'gu']
- **Queries:** 93 | Pass: 80 | Fail: 13 | Skip: 0
- **Average score:** 7.4/10

| # | Type | Lang | Query | Score | Status | Notes |
|---|------|------|-------|-------|--------|-------|
| 1 | greeting | en | Hi there! | 9/10 | ✅ | - |
| 2 | greeting | en | Hey, what's up? | 9/10 | ✅ | - |
| 3 | greeting | en | Good morning! Can you help me? | 9/10 | ✅ | - |
| 4 | greeting | gu | નમસ્તે! કેમ છો? | 9/10 | ✅ | - |
| 5 | greeting | gu | હેલો! મને હેલ્પ કરો | 9/10 | ✅ | - |
| 6 | product_browse | en | Show me your services | 9/10 | ✅ | 5 products |
| 7 | product_browse | en | What solutions do you have? | 9/10 | ✅ | 7 products |
| 8 | product_browse | en | I want to browse your collection | 9/10 | ✅ | 3 products |
| 9 | product_browse | en | What's popular right now? | 9/10 | ✅ | 10 products |
| 10 | product_browse | en | Show me your best sellers | 9/10 | ✅ | 10 products |
| 11 | product_browse | gu | તમારા services બતાવો | 4/10 | ❌ | No products returned or mentioned |
| 12 | product_browse | gu | શું solutions available છે? | 4/10 | ❌ | No products returned or mentioned |
| 13 | product_browse | gu | તમારા best selling products કયા છે? | 9/10 | ✅ | 5 products |
| 14 | specific_product | en | I need a premium services | 6/10 | ✅ | Mentioned products textually |
| 15 | specific_product | en | Looking for web development for daily use | 6/10 | ✅ | Mentioned products textually |
| 16 | specific_product | en | Do you have app development in stock? | 6/10 | ✅ | Mentioned products textually |
| 17 | specific_product | gu | મને services જોઈએ છે | 4/10 | ❌ | No products returned or mentioned |
| 18 | price_filter | en | Show me services under $50 | 4/10 | ❌ | No price info |
| 19 | price_filter | en | services between $20 and $100 | 4/10 | ❌ | No price info |
| 20 | price_filter | en | What's the cheapest solutions? | 4/10 | ❌ | No price info |
| 21 | price_filter | en | Budget services under 500 | 6/10 | ✅ | - |
| 22 | price_filter | en | Most expensive services you have? | 6/10 | ✅ | - |
| 23 | price_filter | gu | ₹500 થી ઓછા services બતાવો | 9/10 | ✅ | - |
| 24 | price_filter | gu | સસ્તા services છે? | 7/10 | ✅ | - |
| 25 | color_filter | en | Show me services in blue | 8/10 | ✅ | 1 products |
| 26 | color_filter | en | Do you have black services? | 8/10 | ✅ | 8 products |
| 27 | color_filter | en | I want a red solutions | 8/10 | ✅ | 3 products |
| 28 | color_filter | gu | લાલ રંગના services બતાવો | 8/10 | ✅ | 10 products |
| 29 | non_product | en | What is your return policy? | 8/10 | ✅ | - |
| 30 | non_product | en | How long does shipping take? | 7/10 | ✅ | Correctly flagged as missing info |
| 31 | non_product | en | Do you offer free delivery? | 8/10 | ✅ | - |
| 32 | non_product | en | What payment methods do you accept? | 7/10 | ✅ | Correctly flagged as missing info |
| 33 | non_product | en | Where are you located? | 7/10 | ✅ | Correctly flagged as missing info |
| 34 | non_product | en | Do you have a physical store? | 8/10 | ✅ | - |
| 35 | non_product | gu | રિટર્ન પોલિસી શું છે? | 8/10 | ✅ | - |
| 36 | non_product | gu | ડિલિવરી કેટલા દિવસમાં થાય? | 4/10 | ❌ | - |
| 37 | irrelevant | en | Can you write me a Python script to sort a li | 10/10 | ✅ | Correctly rejected |
| 38 | irrelevant | en | Who is the Prime Minister of India? | 10/10 | ✅ | Correctly rejected |
| 39 | irrelevant | en | What is the capital of France? | 10/10 | ✅ | Correctly rejected |
| 40 | irrelevant | en | Tell me a joke about programming | 10/10 | ✅ | Correctly rejected |
| 41 | irrelevant | en | Explain quantum physics to me | 10/10 | ✅ | Correctly rejected |
| 42 | irrelevant | en | What's the weather like today? | 10/10 | ✅ | Correctly rejected |
| 43 | irrelevant | en | Who won the FIFA World Cup 2022? | 10/10 | ✅ | Correctly rejected |
| 44 | irrelevant | en | How do I make pasta at home? | 10/10 | ✅ | Correctly rejected |
| 45 | irrelevant | en | What is blockchain technology? | 10/10 | ✅ | Correctly rejected |
| 46 | irrelevant | en | Solve this math: 25 x 48 | 10/10 | ✅ | Correctly rejected |
| 47 | irrelevant | gu | ભારતના વડાપ્રધાન કોણ છે? | 6/10 | ✅ | Short response (likely deflection) |
| 48 | irrelevant | gu | મને એક જોક કહો | 2/10 | ❌ | Bot answered irrelevant question instead of rejecting |
| 49 | unsupported_lang | fr | Bonjour, montrez-moi vos produits les plus po | 10/10 | ✅ | Correctly rejected unsupported language |
| 50 | unsupported_lang | ja | こんにちは、人気商品を教えてください | 10/10 | ✅ | Correctly rejected unsupported language |
| 51 | unsupported_lang | es | Hola, muéstrame tus productos más vendidos | 10/10 | ✅ | Correctly rejected unsupported language |
| 52 | unsupported_lang | zh | 你好，给我看看你们最好的产品 | 10/10 | ✅ | Correctly rejected unsupported language |
| 53 | unsupported_lang_hindi | hi | नमस्ते! आपके पास कौन से services हैं? | 10/10 | ✅ | Correctly rejected unsupported language |
| 54 | unsupported_lang_hindi | hi | 500 रुपये से कम में क्या मिलेगा? | 10/10 | ✅ | Correctly rejected unsupported language |
| 55 | missing_info | en | Show me your product warranty certificates | 7/10 | ✅ | Honestly said info unavailable (no marker) |
| 56 | missing_info | en | What is the GSM rating of your cotton fabric? | 7/10 | ✅ | Honestly said info unavailable (no marker) |
| 57 | missing_info | en | What are your CEO's contact details? | 7/10 | ✅ | Honestly said info unavailable (no marker) |
| 58 | missing_info | en | What year was your company founded? | 7/10 | ✅ | Honestly said info unavailable (no marker) |
| 59 | missing_info | en | Can you show your ISO certification? | 7/10 | ✅ | Honestly said info unavailable (no marker) |
| 60 | missing_info | en | What's the thread count of your premium fabri | 7/10 | ✅ | Honestly said info unavailable (no marker) |
| 61 | missing_info | gu | તમારી company નો GST number શું છે? | 2/10 | ❌ | Bot fabricated info instead of flagging missing |
| 62 | suggestions_test | en | I'm new here, what services do you sell? | 3/10 | ❌ | No suggestions returned |
| 63 | suggestions_test | en | What do you recommend for a gift? | 3/10 | ❌ | No suggestions returned |
| 64 | suggestions_test | gu | gift માટે શું recommend કરો? | 3/10 | ❌ | No suggestions returned |
| 65 | romanized | gu-Latn | mane services batavo | 8/10 | ✅ | Response received for romanized input |
| 66 | romanized | gu-Latn | sasta wala shu chhe? | 8/10 | ✅ | Response received for romanized input |
| 67 | romanized | gu-Latn | tamari best products batavo | 8/10 | ✅ | Response received for romanized input |
| 68 | mixed_lang | gu-mix | Mane services joiye affordable wala | 7/10 | ✅ | Handled mixed-language query |
| 69 | mixed_lang | gu-mix | tumhare best products shu chhe? | 7/10 | ✅ | Handled mixed-language query |
| 70 | ambiguous | en | something nice | 7/10 | ✅ | Handled ambiguous query |
| 71 | ambiguous | en | I need help | 7/10 | ✅ | Handled ambiguous query |
| 72 | ambiguous | en | What do you have? | 8/10 | ✅ | Handled ambiguous query |
| 73 | ambiguous | en | show me options | 8/10 | ✅ | Handled ambiguous query |
| 74 | ambiguous | en | gift ideas | 8/10 | ✅ | Handled ambiguous query |
| 75 | comparison | en | Which services is better quality? | 9/10 | ✅ | Showed 10 products for comparison |
| 76 | comparison | en | What's the difference between your services a | 4/10 | ❌ | - |
| 77 | comparison | en | Which services would you recommend? | 7/10 | ✅ | Textual comparison |
| 78 | edge_case | en | ok | 7/10 | ✅ | Handled edge case gracefully |
| 79 | edge_case | en | thanks | 7/10 | ✅ | Handled edge case gracefully |
| 80 | edge_case | en | yes | 7/10 | ✅ | Handled edge case gracefully |
| 81 | edge_case | en | no | 7/10 | ✅ | Handled edge case gracefully |
| 82 | edge_case | en | hmm | 7/10 | ✅ | Handled edge case gracefully |
| 83 | edge_case | en | ??? | 7/10 | ✅ | Handled edge case gracefully |
| 84 | edge_case | en | lol | 7/10 | ✅ | Handled edge case gracefully |
| 85 | edge_case | en | services | 7/10 | ✅ | Handled edge case gracefully |
| 86 | about_brand | en | Tell me about kriyanta | 8/10 | ✅ | - |
| 87 | about_brand | en | Who are you and what do you sell? | 8/10 | ✅ | - |
| 88 | complaint | en | Your products are too expensive | 8/10 | ✅ | Empathetic response |
| 89 | complaint | en | I had a bad experience with my last order | 8/10 | ✅ | Empathetic response |
| 90 | complaint | en | Why is the quality so poor? | 8/10 | ✅ | Empathetic response |
| 91 | price_format | en | Show me services with prices | 6/10 | ✅ | - |
| 92 | price_format | en | What's the price range of your products? | 6/10 | ✅ | - |
| 93 | price_format | gu | services ની price શું છે? | 6/10 | ✅ | Expected Gujarati response but got non-Gujarati |

### zevaramaze (Jewelry)
- **Languages:** ['en', 'hi', 'gu']
- **Queries:** 112 | Pass: 103 | Fail: 9 | Skip: 0
- **Average score:** 7.7/10

| # | Type | Lang | Query | Score | Status | Notes |
|---|------|------|-------|-------|--------|-------|
| 1 | greeting | en | Hi there! | 9/10 | ✅ | - |
| 2 | greeting | en | Hey, what's up? | 9/10 | ✅ | - |
| 3 | greeting | en | Good morning! Can you help me? | 9/10 | ✅ | - |
| 4 | greeting | hi | नमस्ते! | 9/10 | ✅ | - |
| 5 | greeting | hi | हेलो, कैसे हो? | 9/10 | ✅ | - |
| 6 | greeting | gu | નમસ્તે! કેમ છો? | 9/10 | ✅ | - |
| 7 | greeting | gu | હેલો! મને હેલ્પ કરો | 9/10 | ✅ | - |
| 8 | product_browse | en | Show me your bracelets | 9/10 | ✅ | 10 products |
| 9 | product_browse | en | What necklaces do you have? | 9/10 | ✅ | 10 products |
| 10 | product_browse | en | I want to browse your collection | 6/10 | ✅ | Mentioned products textually |
| 11 | product_browse | en | What's popular right now? | 9/10 | ✅ | 10 products |
| 12 | product_browse | en | Show me your best sellers | 9/10 | ✅ | 10 products |
| 13 | product_browse | hi | आपके पास कौन से bracelets हैं? | 9/10 | ✅ | 10 products |
| 14 | product_browse | hi | मुझे necklaces दिखाओ | 9/10 | ✅ | 10 products |
| 15 | product_browse | hi | सबसे ज्यादा बिकने वाले products दिखाओ | 9/10 | ✅ | 10 products |
| 16 | product_browse | gu | તમારા bracelets બતાવો | 9/10 | ✅ | 10 products |
| 17 | product_browse | gu | શું necklaces available છે? | 9/10 | ✅ | 10 products |
| 18 | product_browse | gu | તમારા best selling products કયા છે? | 9/10 | ✅ | 10 products |
| 19 | specific_product | en | I need a premium bracelets | 9/10 | ✅ | 10 products |
| 20 | specific_product | en | Looking for rings for daily use | 9/10 | ✅ | 10 products |
| 21 | specific_product | en | Do you have earrings in stock? | 9/10 | ✅ | 10 products |
| 22 | specific_product | hi | मुझे bracelets चाहिए जो comfortable हो | 9/10 | ✅ | Expected Hindi response but got non-Hindi |
| 23 | specific_product | gu | મને bracelets જોઈએ છે | 9/10 | ✅ | 10 products |
| 24 | price_filter | en | Show me bracelets under $50 | 9/10 | ✅ | - |
| 25 | price_filter | en | bracelets between $20 and $100 | 9/10 | ✅ | - |
| 26 | price_filter | en | What's the cheapest necklaces? | 9/10 | ✅ | - |
| 27 | price_filter | en | Budget bracelets under 500 | 9/10 | ✅ | - |
| 28 | price_filter | en | Most expensive bracelets you have? | 7/10 | ✅ | - |
| 29 | price_filter | hi | 500 रुपये से कम के bracelets बताओ | 7/10 | ✅ | - |
| 30 | price_filter | hi | 1000 से 2000 रुपये वाले bracelets | 7/10 | ✅ | - |
| 31 | price_filter | gu | ₹500 થી ઓછા bracelets બતાવો | 9/10 | ✅ | - |
| 32 | price_filter | gu | સસ્તા bracelets છે? | 7/10 | ✅ | - |
| 33 | color_filter | en | Show me bracelets in blue | 6/10 | ✅ | - |
| 34 | color_filter | en | Do you have black bracelets? | 8/10 | ✅ | 1 products |
| 35 | color_filter | en | I want a red necklaces | 8/10 | ✅ | 1 products |
| 36 | color_filter | hi | काले रंग के bracelets दिखाओ | 8/10 | ✅ | 1 products |
| 37 | color_filter | gu | લાલ રંગના bracelets બતાવો | 8/10 | ✅ | 2 products |
| 38 | non_product | en | What is your return policy? | 7/10 | ✅ | Correctly flagged as missing info |
| 39 | non_product | en | How long does shipping take? | 7/10 | ✅ | Correctly flagged as missing info |
| 40 | non_product | en | Do you offer free delivery? | 8/10 | ✅ | - |
| 41 | non_product | en | What payment methods do you accept? | 8/10 | ✅ | - |
| 42 | non_product | en | Where are you located? | 8/10 | ✅ | - |
| 43 | non_product | en | Do you have a physical store? | 8/10 | ✅ | - |
| 44 | non_product | hi | रिटर्न पॉलिसी क्या है? | 8/10 | ✅ | - |
| 45 | non_product | hi | delivery कितने दिन में होती है? | 8/10 | ✅ | - |
| 46 | non_product | gu | રિટર્ન પોલિસી શું છે? | 4/10 | ❌ | - |
| 47 | non_product | gu | ડિલિવરી કેટલા દિવસમાં થાય? | 4/10 | ❌ | - |
| 48 | irrelevant | en | Can you write me a Python script to sort a li | 10/10 | ✅ | Correctly rejected |
| 49 | irrelevant | en | Who is the Prime Minister of India? | 10/10 | ✅ | Correctly rejected |
| 50 | irrelevant | en | What is the capital of France? | 7/10 | ✅ | Rejected but response too long (may include partial answer) |
| 51 | irrelevant | en | Tell me a joke about programming | 10/10 | ✅ | Correctly rejected |
| 52 | irrelevant | en | Explain quantum physics to me | 7/10 | ✅ | Rejected but response too long (may include partial answer) |
| 53 | irrelevant | en | What's the weather like today? | 7/10 | ✅ | Rejected but response too long (may include partial answer) |
| 54 | irrelevant | en | Who won the FIFA World Cup 2022? | 7/10 | ✅ | Rejected but response too long (may include partial answer) |
| 55 | irrelevant | en | How do I make pasta at home? | 10/10 | ✅ | Correctly rejected |
| 56 | irrelevant | en | What is blockchain technology? | 10/10 | ✅ | Correctly rejected |
| 57 | irrelevant | en | Solve this math: 25 x 48 | 7/10 | ✅ | Rejected but response too long (may include partial answer) |
| 58 | irrelevant | hi | भारत का प्रधानमंत्री कौन है? | 6/10 | ✅ | Short response (likely deflection) |
| 59 | irrelevant | hi | पायथन स्क्रिप्ट लिखो | 10/10 | ✅ | Expected Hindi response but got non-Hindi |
| 60 | irrelevant | hi | चांद पर कौन गया था? | 2/10 | ❌ | Bot answered irrelevant question instead of rejecting |
| 61 | unsupported_lang | fr | Bonjour, montrez-moi vos produits les plus po | 10/10 | ✅ | Correctly rejected unsupported language |
| 62 | unsupported_lang | ja | こんにちは、人気商品を教えてください | 10/10 | ✅ | Correctly rejected unsupported language |
| 63 | unsupported_lang | es | Hola, muéstrame tus productos más vendidos | 10/10 | ✅ | Correctly rejected unsupported language |
| 64 | unsupported_lang | zh | 你好，给我看看你们最好的产品 | 10/10 | ✅ | Correctly rejected unsupported language |
| 65 | missing_info | en | Show me your product warranty certificates | 7/10 | ✅ | Honestly said info unavailable (no marker) |
| 66 | missing_info | en | What is the GSM rating of your cotton fabric? | 7/10 | ✅ | Honestly said info unavailable (no marker) |
| 67 | missing_info | en | What are your CEO's contact details? | 7/10 | ✅ | Honestly said info unavailable (no marker) |
| 68 | missing_info | en | What year was your company founded? | 7/10 | ✅ | Honestly said info unavailable (no marker) |
| 69 | missing_info | en | Can you show your ISO certification? | 7/10 | ✅ | Honestly said info unavailable (no marker) |
| 70 | missing_info | en | What's the thread count of your premium fabri | 7/10 | ✅ | Honestly said info unavailable (no marker) |
| 71 | missing_info | hi | आपकी कंपनी का GSTIN नंबर क्या है? | 2/10 | ❌ | Bot fabricated info instead of flagging missing |
| 72 | missing_info | gu | તમારી company નો GST number શું છે? | 2/10 | ❌ | Expected Gujarati response but got non-Gujarati; Bot fabrica |
| 73 | suggestions_test | en | I'm new here, what bracelets do you sell? | 3/10 | ❌ | No suggestions returned |
| 74 | suggestions_test | en | What do you recommend for a gift? | 3/10 | ❌ | No suggestions returned |
| 75 | suggestions_test | hi | यहां क्या-क्या मिलता है? | 3/10 | ❌ | No suggestions returned |
| 76 | suggestions_test | gu | gift માટે શું recommend કરો? | 3/10 | ❌ | Expected Gujarati response but got non-Gujarati; No suggesti |
| 77 | romanized | hi-Latn | mujhe bracelets dikhao | 8/10 | ✅ | Response received for romanized input |
| 78 | romanized | hi-Latn | saste wale products batao | 8/10 | ✅ | Response received for romanized input |
| 79 | romanized | hi-Latn | kya discount chal raha hai? | 8/10 | ✅ | Response received for romanized input |
| 80 | romanized | gu-Latn | mane bracelets batavo | 8/10 | ✅ | Response received for romanized input |
| 81 | romanized | gu-Latn | sasta wala shu chhe? | 8/10 | ✅ | Response received for romanized input |
| 82 | romanized | gu-Latn | tamari best products batavo | 8/10 | ✅ | Response received for romanized input |
| 83 | mixed_lang | hi-mix | Mujhe bracelets chahiye blue color mein | 7/10 | ✅ | Handled mixed-language query |
| 84 | mixed_lang | hi-mix | price range kya hai aapka? | 7/10 | ✅ | Handled mixed-language query |
| 85 | mixed_lang | gu-mix | Mane bracelets joiye affordable wala | 7/10 | ✅ | Handled mixed-language query |
| 86 | mixed_lang | gu-mix | tumhare best products shu chhe? | 7/10 | ✅ | Handled mixed-language query |
| 87 | ambiguous | en | something nice | 8/10 | ✅ | Handled ambiguous query |
| 88 | ambiguous | en | I need help | 7/10 | ✅ | Handled ambiguous query |
| 89 | ambiguous | en | What do you have? | 8/10 | ✅ | Handled ambiguous query |
| 90 | ambiguous | en | show me options | 8/10 | ✅ | Handled ambiguous query |
| 91 | ambiguous | en | gift ideas | 7/10 | ✅ | Handled ambiguous query |
| 92 | comparison | en | Which bracelets is better quality? | 9/10 | ✅ | Showed 10 products for comparison |
| 93 | comparison | en | What's the difference between your bracelets  | 9/10 | ✅ | Showed 10 products for comparison |
| 94 | comparison | en | Which bracelets would you recommend? | 9/10 | ✅ | Showed 10 products for comparison |
| 95 | edge_case | en | ok | 7/10 | ✅ | Handled edge case gracefully |
| 96 | edge_case | en | thanks | 7/10 | ✅ | Handled edge case gracefully |
| 97 | edge_case | en | yes | 7/10 | ✅ | Handled edge case gracefully |
| 98 | edge_case | en | no | 7/10 | ✅ | Handled edge case gracefully |
| 99 | edge_case | en | hmm | 7/10 | ✅ | Handled edge case gracefully |
| 100 | edge_case | en | ??? | 7/10 | ✅ | Handled edge case gracefully |
| 101 | edge_case | en | lol | 7/10 | ✅ | Handled edge case gracefully |
| 102 | edge_case | en | bracelets | 7/10 | ✅ | Handled edge case gracefully |
| 103 | about_brand | en | Tell me about zevaramaze | 8/10 | ✅ | - |
| 104 | about_brand | en | Who are you and what do you sell? | 8/10 | ✅ | - |
| 105 | about_brand | hi | zevaramaze के बारे में बताओ | 8/10 | ✅ | - |
| 106 | complaint | en | Your products are too expensive | 6/10 | ✅ | - |
| 107 | complaint | en | I had a bad experience with my last order | 8/10 | ✅ | Empathetic response |
| 108 | complaint | en | Why is the quality so poor? | 8/10 | ✅ | Empathetic response |
| 109 | price_format | en | Show me bracelets with prices | 9/10 | ✅ | - |
| 110 | price_format | en | What's the price range of your products? | 6/10 | ✅ | - |
| 111 | price_format | hi | bracelets का price क्या है? | 9/10 | ✅ | - |
| 112 | price_format | gu | bracelets ની price શું છે? | 9/10 | ✅ | - |

### beardbrand (Grooming/Lifestyle)
- **Languages:** ['en']
- **Queries:** 73 | Pass: 70 | Fail: 3 | Skip: 0
- **Average score:** 8.1/10

| # | Type | Lang | Query | Score | Status | Notes |
|---|------|------|-------|-------|--------|-------|
| 1 | greeting | en | Hi there! | 9/10 | ✅ | - |
| 2 | greeting | en | Hey, what's up? | 9/10 | ✅ | - |
| 3 | greeting | en | Good morning! Can you help me? | 9/10 | ✅ | - |
| 4 | product_browse | en | Show me your beard oil | 8/10 | ✅ | 10 products |
| 5 | product_browse | en | What beard balm do you have? | 8/10 | ✅ | 10 products |
| 6 | product_browse | en | I want to browse your collection | 8/10 | ✅ | 10 products |
| 7 | product_browse | en | What's popular right now? | 8/10 | ✅ | 10 products |
| 8 | product_browse | en | Show me your best sellers | 8/10 | ✅ | 10 products |
| 9 | specific_product | en | I need a premium beard oil | 8/10 | ✅ | 10 products |
| 10 | specific_product | en | Looking for utility balm for daily use | 8/10 | ✅ | 10 products |
| 11 | specific_product | en | Do you have grooming kit in stock? | 8/10 | ✅ | 10 products |
| 12 | price_filter | en | Show me beard oil under $50 | 7/10 | ✅ | - |
| 13 | price_filter | en | beard oil between $20 and $100 | 7/10 | ✅ | - |
| 14 | price_filter | en | What's the cheapest beard balm? | 7/10 | ✅ | - |
| 15 | price_filter | en | Budget beard oil under 500 | 7/10 | ✅ | - |
| 16 | price_filter | en | Most expensive beard oil you have? | 7/10 | ✅ | - |
| 17 | color_filter | en | Show me beard oil in blue | 8/10 | ✅ | 10 products |
| 18 | color_filter | en | Do you have black beard oil? | 8/10 | ✅ | 2 products |
| 19 | color_filter | en | I want a red beard balm | 8/10 | ✅ | 10 products |
| 20 | non_product | en | What is your return policy? | 4/10 | ❌ | - |
| 21 | non_product | en | How long does shipping take? | 8/10 | ✅ | - |
| 22 | non_product | en | Do you offer free delivery? | 8/10 | ✅ | - |
| 23 | non_product | en | What payment methods do you accept? | 8/10 | ✅ | - |
| 24 | non_product | en | Where are you located? | 7/10 | ✅ | Correctly flagged as missing info |
| 25 | non_product | en | Do you have a physical store? | 8/10 | ✅ | - |
| 26 | irrelevant | en | Can you write me a Python script to sort a li | 10/10 | ✅ | Correctly rejected |
| 27 | irrelevant | en | Who is the Prime Minister of India? | 10/10 | ✅ | Correctly rejected |
| 28 | irrelevant | en | What is the capital of France? | 10/10 | ✅ | Correctly rejected |
| 29 | irrelevant | en | Tell me a joke about programming | 10/10 | ✅ | Correctly rejected |
| 30 | irrelevant | en | Explain quantum physics to me | 10/10 | ✅ | Correctly rejected |
| 31 | irrelevant | en | What's the weather like today? | 10/10 | ✅ | Correctly rejected |
| 32 | irrelevant | en | Who won the FIFA World Cup 2022? | 10/10 | ✅ | Correctly rejected |
| 33 | irrelevant | en | How do I make pasta at home? | 10/10 | ✅ | Correctly rejected |
| 34 | irrelevant | en | What is blockchain technology? | 10/10 | ✅ | Correctly rejected |
| 35 | irrelevant | en | Solve this math: 25 x 48 | 10/10 | ✅ | Correctly rejected |
| 36 | unsupported_lang | fr | Bonjour, montrez-moi vos produits les plus po | 10/10 | ✅ | Correctly rejected unsupported language |
| 37 | unsupported_lang | ja | こんにちは、人気商品を教えてください | 10/10 | ✅ | Correctly rejected unsupported language |
| 38 | unsupported_lang | es | Hola, muéstrame tus productos más vendidos | 10/10 | ✅ | Correctly rejected unsupported language |
| 39 | unsupported_lang | zh | 你好，给我看看你们最好的产品 | 10/10 | ✅ | Correctly rejected unsupported language |
| 40 | unsupported_lang_hindi | hi | नमस्ते! आपके पास कौन से beard oil हैं? | 10/10 | ✅ | Correctly rejected unsupported language |
| 41 | unsupported_lang_hindi | hi | 500 रुपये से कम में क्या मिलेगा? | 10/10 | ✅ | Correctly rejected unsupported language |
| 42 | unsupported_lang_gujarati | gu | તમારી પાસે કયા beard oil છે? | 10/10 | ✅ | Correctly rejected unsupported language |
| 43 | missing_info | en | Show me your product warranty certificates | 7/10 | ✅ | Honestly said info unavailable (no marker) |
| 44 | missing_info | en | What is the GSM rating of your cotton fabric? | 7/10 | ✅ | Honestly said info unavailable (no marker) |
| 45 | missing_info | en | What are your CEO's contact details? | 7/10 | ✅ | Honestly said info unavailable (no marker) |
| 46 | missing_info | en | What year was your company founded? | 7/10 | ✅ | Honestly said info unavailable (no marker) |
| 47 | missing_info | en | Can you show your ISO certification? | 7/10 | ✅ | Honestly said info unavailable (no marker) |
| 48 | missing_info | en | What's the thread count of your premium fabri | 7/10 | ✅ | Honestly said info unavailable (no marker) |
| 49 | suggestions_test | en | I'm new here, what beard oil do you sell? | 3/10 | ❌ | No suggestions returned |
| 50 | suggestions_test | en | What do you recommend for a gift? | 3/10 | ❌ | No suggestions returned |
| 51 | ambiguous | en | something nice | 8/10 | ✅ | Handled ambiguous query |
| 52 | ambiguous | en | I need help | 7/10 | ✅ | Handled ambiguous query |
| 53 | ambiguous | en | What do you have? | 8/10 | ✅ | Handled ambiguous query |
| 54 | ambiguous | en | show me options | 8/10 | ✅ | Handled ambiguous query |
| 55 | ambiguous | en | gift ideas | 8/10 | ✅ | Handled ambiguous query |
| 56 | comparison | en | Which beard oil is better quality? | 9/10 | ✅ | Showed 10 products for comparison |
| 57 | comparison | en | What's the difference between your beard oil  | 9/10 | ✅ | Showed 10 products for comparison |
| 58 | comparison | en | Which beard oil would you recommend? | 9/10 | ✅ | Showed 10 products for comparison |
| 59 | edge_case | en | ok | 7/10 | ✅ | Handled edge case gracefully |
| 60 | edge_case | en | thanks | 7/10 | ✅ | Handled edge case gracefully |
| 61 | edge_case | en | yes | 7/10 | ✅ | Handled edge case gracefully |
| 62 | edge_case | en | no | 7/10 | ✅ | Handled edge case gracefully |
| 63 | edge_case | en | hmm | 7/10 | ✅ | Handled edge case gracefully |
| 64 | edge_case | en | ??? | 7/10 | ✅ | Handled edge case gracefully |
| 65 | edge_case | en | lol | 7/10 | ✅ | Handled edge case gracefully |
| 66 | edge_case | en | beard oil | 7/10 | ✅ | Handled edge case gracefully |
| 67 | about_brand | en | Tell me about beardbrand | 8/10 | ✅ | - |
| 68 | about_brand | en | Who are you and what do you sell? | 8/10 | ✅ | - |
| 69 | complaint | en | Your products are too expensive | 8/10 | ✅ | Empathetic response |
| 70 | complaint | en | I had a bad experience with my last order | 8/10 | ✅ | Empathetic response |
| 71 | complaint | en | Why is the quality so poor? | 8/10 | ✅ | Empathetic response |
| 72 | price_format | en | Show me beard oil with prices | 7/10 | ✅ | - |
| 73 | price_format | en | What's the price range of your products? | 9/10 | ✅ | - |

### deathwish (Coffee/Beverage)
- **Languages:** ['en', 'hi']
- **Queries:** 94 | Pass: 88 | Fail: 6 | Skip: 0
- **Average score:** 7.7/10

| # | Type | Lang | Query | Score | Status | Notes |
|---|------|------|-------|-------|--------|-------|
| 1 | greeting | en | Hi there! | 9/10 | ✅ | - |
| 2 | greeting | en | Hey, what's up? | 9/10 | ✅ | - |
| 3 | greeting | en | Good morning! Can you help me? | 9/10 | ✅ | - |
| 4 | greeting | hi | नमस्ते! | 9/10 | ✅ | - |
| 5 | greeting | hi | हेलो, कैसे हो? | 9/10 | ✅ | - |
| 6 | product_browse | en | Show me your coffee | 9/10 | ✅ | 10 products |
| 7 | product_browse | en | What ground coffee do you have? | 9/10 | ✅ | 10 products |
| 8 | product_browse | en | I want to browse your collection | 9/10 | ✅ | 10 products |
| 9 | product_browse | en | What's popular right now? | 9/10 | ✅ | 10 products |
| 10 | product_browse | en | Show me your best sellers | 9/10 | ✅ | 10 products |
| 11 | product_browse | hi | आपके पास कौन से coffee हैं? | 9/10 | ✅ | 10 products |
| 12 | product_browse | hi | मुझे ground coffee दिखाओ | 9/10 | ✅ | 10 products |
| 13 | product_browse | hi | सबसे ज्यादा बिकने वाले products दिखाओ | 9/10 | ✅ | 10 products |
| 14 | specific_product | en | I need a premium coffee | 9/10 | ✅ | 10 products |
| 15 | specific_product | en | Looking for K-cups for daily use | 9/10 | ✅ | 10 products |
| 16 | specific_product | en | Do you have death cups in stock? | 9/10 | ✅ | 10 products |
| 17 | specific_product | hi | मुझे coffee चाहिए जो comfortable हो | 9/10 | ✅ | 10 products |
| 18 | price_filter | en | Show me coffee under $50 | 9/10 | ✅ | - |
| 19 | price_filter | en | coffee between $20 and $100 | 7/10 | ✅ | - |
| 20 | price_filter | en | What's the cheapest ground coffee? | 7/10 | ✅ | - |
| 21 | price_filter | en | Budget coffee under 500 | 7/10 | ✅ | - |
| 22 | price_filter | en | Most expensive coffee you have? | 7/10 | ✅ | - |
| 23 | price_filter | hi | 500 रुपये से कम के coffee बताओ | 7/10 | ✅ | - |
| 24 | price_filter | hi | 1000 से 2000 रुपये वाले coffee | 7/10 | ✅ | - |
| 25 | color_filter | en | Show me coffee in blue | 8/10 | ✅ | 2 products |
| 26 | color_filter | en | Do you have black coffee? | 8/10 | ✅ | 10 products |
| 27 | color_filter | en | I want a red ground coffee | 8/10 | ✅ | 10 products |
| 28 | color_filter | hi | काले रंग के coffee दिखाओ | 8/10 | ✅ | 9 products |
| 29 | non_product | en | What is your return policy? | 7/10 | ✅ | Correctly flagged as missing info |
| 30 | non_product | en | How long does shipping take? | 8/10 | ✅ | - |
| 31 | non_product | en | Do you offer free delivery? | 8/10 | ✅ | - |
| 32 | non_product | en | What payment methods do you accept? | 7/10 | ✅ | Correctly flagged as missing info |
| 33 | non_product | en | Where are you located? | 8/10 | ✅ | - |
| 34 | non_product | en | Do you have a physical store? | 8/10 | ✅ | - |
| 35 | non_product | hi | रिटर्न पॉलिसी क्या है? | 4/10 | ❌ | - |
| 36 | non_product | hi | delivery कितने दिन में होती है? | 4/10 | ❌ | - |
| 37 | irrelevant | en | Can you write me a Python script to sort a li | 10/10 | ✅ | Correctly rejected |
| 38 | irrelevant | en | Who is the Prime Minister of India? | 7/10 | ✅ | Rejected but response too long (may include partial answer) |
| 39 | irrelevant | en | What is the capital of France? | 7/10 | ✅ | Rejected but response too long (may include partial answer) |
| 40 | irrelevant | en | Tell me a joke about programming | 7/10 | ✅ | Rejected but response too long (may include partial answer) |
| 41 | irrelevant | en | Explain quantum physics to me | 7/10 | ✅ | Rejected but response too long (may include partial answer) |
| 42 | irrelevant | en | What's the weather like today? | 7/10 | ✅ | Rejected but response too long (may include partial answer) |
| 43 | irrelevant | en | Who won the FIFA World Cup 2022? | 7/10 | ✅ | Rejected but response too long (may include partial answer) |
| 44 | irrelevant | en | How do I make pasta at home? | 7/10 | ✅ | Rejected but response too long (may include partial answer) |
| 45 | irrelevant | en | What is blockchain technology? | 7/10 | ✅ | Rejected but response too long (may include partial answer) |
| 46 | irrelevant | en | Solve this math: 25 x 48 | 7/10 | ✅ | Rejected but response too long (may include partial answer) |
| 47 | irrelevant | hi | भारत का प्रधानमंत्री कौन है? | 10/10 | ✅ | Correctly rejected |
| 48 | irrelevant | hi | पायथन स्क्रिप्ट लिखो | 10/10 | ✅ | Correctly rejected |
| 49 | irrelevant | hi | चांद पर कौन गया था? | 10/10 | ✅ | Correctly rejected |
| 50 | unsupported_lang | fr | Bonjour, montrez-moi vos produits les plus po | 10/10 | ✅ | Correctly rejected unsupported language |
| 51 | unsupported_lang | ja | こんにちは、人気商品を教えてください | 10/10 | ✅ | Correctly rejected unsupported language |
| 52 | unsupported_lang | es | Hola, muéstrame tus productos más vendidos | 10/10 | ✅ | Correctly rejected unsupported language |
| 53 | unsupported_lang | zh | 你好，给我看看你们最好的产品 | 10/10 | ✅ | Correctly rejected unsupported language |
| 54 | unsupported_lang_gujarati | gu | તમારી પાસે કયા coffee છે? | 10/10 | ✅ | Correctly rejected unsupported language |
| 55 | missing_info | en | Show me your product warranty certificates | 7/10 | ✅ | Honestly said info unavailable (no marker) |
| 56 | missing_info | en | What is the GSM rating of your cotton fabric? | 7/10 | ✅ | Honestly said info unavailable (no marker) |
| 57 | missing_info | en | What are your CEO's contact details? | 7/10 | ✅ | Honestly said info unavailable (no marker) |
| 58 | missing_info | en | What year was your company founded? | 7/10 | ✅ | Honestly said info unavailable (no marker) |
| 59 | missing_info | en | Can you show your ISO certification? | 7/10 | ✅ | Honestly said info unavailable (no marker) |
| 60 | missing_info | en | What's the thread count of your premium fabri | 7/10 | ✅ | Honestly said info unavailable (no marker) |
| 61 | missing_info | hi | आपकी कंपनी का GSTIN नंबर क्या है? | 2/10 | ❌ | Bot fabricated info instead of flagging missing |
| 62 | suggestions_test | en | I'm new here, what coffee do you sell? | 3/10 | ❌ | No suggestions returned |
| 63 | suggestions_test | en | What do you recommend for a gift? | 3/10 | ❌ | No suggestions returned |
| 64 | suggestions_test | hi | यहां क्या-क्या मिलता है? | 3/10 | ❌ | No suggestions returned |
| 65 | romanized | hi-Latn | mujhe coffee dikhao | 8/10 | ✅ | Response received for romanized input |
| 66 | romanized | hi-Latn | saste wale products batao | 8/10 | ✅ | Response received for romanized input |
| 67 | romanized | hi-Latn | kya discount chal raha hai? | 8/10 | ✅ | Response received for romanized input |
| 68 | mixed_lang | hi-mix | Mujhe coffee chahiye blue color mein | 7/10 | ✅ | Handled mixed-language query |
| 69 | mixed_lang | hi-mix | price range kya hai aapka? | 7/10 | ✅ | Handled mixed-language query |
| 70 | ambiguous | en | something nice | 8/10 | ✅ | Handled ambiguous query |
| 71 | ambiguous | en | I need help | 7/10 | ✅ | Handled ambiguous query |
| 72 | ambiguous | en | What do you have? | 8/10 | ✅ | Handled ambiguous query |
| 73 | ambiguous | en | show me options | 8/10 | ✅ | Handled ambiguous query |
| 74 | ambiguous | en | gift ideas | 8/10 | ✅ | Handled ambiguous query |
| 75 | comparison | en | Which coffee is better quality? | 9/10 | ✅ | Showed 10 products for comparison |
| 76 | comparison | en | What's the difference between your coffee and | 9/10 | ✅ | Showed 10 products for comparison |
| 77 | comparison | en | Which coffee would you recommend? | 9/10 | ✅ | Showed 10 products for comparison |
| 78 | edge_case | en | ok | 7/10 | ✅ | Handled edge case gracefully |
| 79 | edge_case | en | thanks | 7/10 | ✅ | Handled edge case gracefully |
| 80 | edge_case | en | yes | 7/10 | ✅ | Handled edge case gracefully |
| 81 | edge_case | en | no | 7/10 | ✅ | Handled edge case gracefully |
| 82 | edge_case | en | hmm | 7/10 | ✅ | Handled edge case gracefully |
| 83 | edge_case | en | ??? | 7/10 | ✅ | Handled edge case gracefully |
| 84 | edge_case | en | lol | 7/10 | ✅ | Handled edge case gracefully |
| 85 | edge_case | en | coffee | 7/10 | ✅ | Handled edge case gracefully |
| 86 | about_brand | en | Tell me about deathwish | 8/10 | ✅ | - |
| 87 | about_brand | en | Who are you and what do you sell? | 8/10 | ✅ | - |
| 88 | about_brand | hi | deathwish के बारे में बताओ | 8/10 | ✅ | - |
| 89 | complaint | en | Your products are too expensive | 6/10 | ✅ | - |
| 90 | complaint | en | I had a bad experience with my last order | 8/10 | ✅ | Empathetic response |
| 91 | complaint | en | Why is the quality so poor? | 8/10 | ✅ | Empathetic response |
| 92 | price_format | en | Show me coffee with prices | 7/10 | ✅ | - |
| 93 | price_format | en | What's the price range of your products? | 9/10 | ✅ | - |
| 94 | price_format | hi | coffee का price क्या है? | 7/10 | ✅ | - |

### tentree (Fashion/Eco-friendly)
- **Languages:** ['en', 'gu']
- **Queries:** 93 | Pass: 58 | Fail: 3 | Skip: 32
- **Average score:** 8.4/10

| # | Type | Lang | Query | Score | Status | Notes |
|---|------|------|-------|-------|--------|-------|
| 1 | greeting | en | Hi there! | 9/10 | ✅ | - |
| 2 | greeting | en | Hey, what's up? | 9/10 | ✅ | - |
| 3 | greeting | en | Good morning! Can you help me? | 9/10 | ✅ | - |
| 4 | greeting | gu | નમસ્તે! કેમ છો? | 9/10 | ✅ | - |
| 5 | greeting | gu | હેલો! મને હેલ્પ કરો | 9/10 | ✅ | - |
| 6 | product_browse | en | Show me your t-shirts | 9/10 | ✅ | 4 products |
| 7 | product_browse | en | What hoodies do you have? | 9/10 | ✅ | 6 products |
| 8 | product_browse | en | I want to browse your collection | 9/10 | ✅ | 10 products |
| 9 | product_browse | en | What's popular right now? | 9/10 | ✅ | 2 products |
| 10 | product_browse | en | Show me your best sellers | 9/10 | ✅ | 6 products |
| 11 | product_browse | gu | તમારા t-shirts બતાવો | 9/10 | ✅ | 4 products |
| 12 | product_browse | gu | શું hoodies available છે? | 9/10 | ✅ | 6 products |
| 13 | product_browse | gu | તમારા best selling products કયા છે? | 9/10 | ✅ | 3 products |
| 14 | specific_product | en | I need a premium t-shirts | 9/10 | ✅ | 6 products |
| 15 | specific_product | en | Looking for joggers for daily use | 9/10 | ✅ | 7 products |
| 16 | specific_product | en | Do you have jackets in stock? | 9/10 | ✅ | 10 products |
| 17 | specific_product | gu | મને t-shirts જોઈએ છે | 9/10 | ✅ | 3 products |
| 18 | price_filter | en | Show me t-shirts under $50 | 9/10 | ✅ | - |
| 19 | price_filter | en | t-shirts between $20 and $100 | 9/10 | ✅ | - |
| 20 | price_filter | en | What's the cheapest hoodies? | 9/10 | ✅ | - |
| 21 | price_filter | en | Budget t-shirts under 500 | 9/10 | ✅ | - |
| 22 | price_filter | en | Most expensive t-shirts you have? | 9/10 | ✅ | - |
| 23 | price_filter | gu | ₹500 થી ઓછા t-shirts બતાવો | 9/10 | ✅ | - |
| 24 | price_filter | gu | સસ્તા t-shirts છે? | 9/10 | ✅ | - |
| 25 | color_filter | en | Show me t-shirts in blue | 8/10 | ✅ | 2 products |
| 26 | color_filter | en | Do you have black t-shirts? | 8/10 | ✅ | 1 products |
| 27 | color_filter | en | I want a red hoodies | 8/10 | ✅ | 2 products |
| 28 | color_filter | gu | લાલ રંગના t-shirts બતાવો | 8/10 | ✅ | 3 products |
| 29 | non_product | en | What is your return policy? | 7/10 | ✅ | Correctly flagged as missing info |
| 30 | non_product | en | How long does shipping take? | 8/10 | ✅ | - |
| 31 | non_product | en | Do you offer free delivery? | 8/10 | ✅ | - |
| 32 | non_product | en | What payment methods do you accept? | 8/10 | ✅ | - |
| 33 | non_product | en | Where are you located? | 8/10 | ✅ | - |
| 34 | non_product | en | Do you have a physical store? | 8/10 | ✅ | - |
| 35 | non_product | gu | રિટર્ન પોલિસી શું છે? | SKIP | ✅ | RATE_LIMITED |
| 36 | non_product | gu | ડિલિવરી કેટલા દિવસમાં થાય? | 4/10 | ❌ | - |
| 37 | irrelevant | en | Can you write me a Python script to sort a li | 10/10 | ✅ | Correctly rejected |
| 38 | irrelevant | en | Who is the Prime Minister of India? | SKIP | ✅ | RATE_LIMITED |
| 39 | irrelevant | en | What is the capital of France? | 10/10 | ✅ | Correctly rejected |
| 40 | irrelevant | en | Tell me a joke about programming | 10/10 | ✅ | Correctly rejected |
| 41 | irrelevant | en | Explain quantum physics to me | SKIP | ✅ | RATE_LIMITED |
| 42 | irrelevant | en | What's the weather like today? | 10/10 | ✅ | Correctly rejected |
| 43 | irrelevant | en | Who won the FIFA World Cup 2022? | 10/10 | ✅ | Correctly rejected |
| 44 | irrelevant | en | How do I make pasta at home? | SKIP | ✅ | RATE_LIMITED |
| 45 | irrelevant | en | What is blockchain technology? | 10/10 | ✅ | Correctly rejected |
| 46 | irrelevant | en | Solve this math: 25 x 48 | 10/10 | ✅ | Correctly rejected |
| 47 | irrelevant | gu | ભારતના વડાપ્રધાન કોણ છે? | SKIP | ✅ | RATE_LIMITED |
| 48 | irrelevant | gu | મને એક જોક કહો | 2/10 | ❌ | Bot answered irrelevant question instead of rejecting |
| 49 | unsupported_lang | fr | Bonjour, montrez-moi vos produits les plus po | 10/10 | ✅ | Correctly rejected unsupported language |
| 50 | unsupported_lang | ja | こんにちは、人気商品を教えてください | 10/10 | ✅ | Correctly rejected unsupported language |
| 51 | unsupported_lang | es | Hola, muéstrame tus productos más vendidos | 10/10 | ✅ | Correctly rejected unsupported language |
| 52 | unsupported_lang | zh | 你好，给我看看你们最好的产品 | 10/10 | ✅ | Correctly rejected unsupported language |
| 53 | unsupported_lang_hindi | hi | नमस्ते! आपके पास कौन से t-shirts हैं? | 10/10 | ✅ | Correctly rejected unsupported language |
| 54 | unsupported_lang_hindi | hi | 500 रुपये से कम में क्या मिलेगा? | 10/10 | ✅ | Correctly rejected unsupported language |
| 55 | missing_info | en | Show me your product warranty certificates | 7/10 | ✅ | Honestly said info unavailable (no marker) |
| 56 | missing_info | en | What is the GSM rating of your cotton fabric? | SKIP | ✅ | RATE_LIMITED |
| 57 | missing_info | en | What are your CEO's contact details? | 7/10 | ✅ | Honestly said info unavailable (no marker) |
| 58 | missing_info | en | What year was your company founded? | 7/10 | ✅ | Honestly said info unavailable (no marker) |
| 59 | missing_info | en | Can you show your ISO certification? | SKIP | ✅ | RATE_LIMITED |
| 60 | missing_info | en | What's the thread count of your premium fabri | SKIP | ✅ | RATE_LIMITED |
| 61 | missing_info | gu | તમારી company નો GST number શું છે? | 2/10 | ❌ | Bot fabricated info instead of flagging missing |
| 62 | suggestions_test | en | I'm new here, what t-shirts do you sell? | SKIP | ✅ | RATE_LIMITED |
| 63 | suggestions_test | en | What do you recommend for a gift? | SKIP | ✅ | RATE_LIMITED |
| 64 | suggestions_test | gu | gift માટે શું recommend કરો? | 6/10 | ✅ | Decent suggestions |
| 65 | romanized | gu-Latn | mane t-shirts batavo | SKIP | ✅ | RATE_LIMITED |
| 66 | romanized | gu-Latn | sasta wala shu chhe? | SKIP | ✅ | RATE_LIMITED |
| 67 | romanized | gu-Latn | tamari best products batavo | 8/10 | ✅ | Response received for romanized input |
| 68 | mixed_lang | gu-mix | Mane t-shirts joiye affordable wala | SKIP | ✅ | RATE_LIMITED |
| 69 | mixed_lang | gu-mix | tumhare best products shu chhe? | SKIP | ✅ | RATE_LIMITED |
| 70 | ambiguous | en | something nice | 8/10 | ✅ | Handled ambiguous query |
| 71 | ambiguous | en | I need help | 8/10 | ✅ | Handled ambiguous query |
| 72 | ambiguous | en | What do you have? | SKIP | ✅ | RATE_LIMITED |
| 73 | ambiguous | en | show me options | 8/10 | ✅ | Handled ambiguous query |
| 74 | ambiguous | en | gift ideas | SKIP | ✅ | RATE_LIMITED |
| 75 | comparison | en | Which t-shirts is better quality? | SKIP | ✅ | RATE_LIMITED |
| 76 | comparison | en | What's the difference between your t-shirts a | 9/10 | ✅ | Showed 10 products for comparison |
| 77 | comparison | en | Which t-shirts would you recommend? | SKIP | ✅ | RATE_LIMITED |
| 78 | edge_case | en | ok | 7/10 | ✅ | Handled edge case gracefully |
| 79 | edge_case | en | thanks | 7/10 | ✅ | Handled edge case gracefully |
| 80 | edge_case | en | yes | SKIP | ✅ | RATE_LIMITED |
| 81 | edge_case | en | no | SKIP | ✅ | RATE_LIMITED |
| 82 | edge_case | en | hmm | SKIP | ✅ | RATE_LIMITED |
| 83 | edge_case | en | ??? | SKIP | ✅ | RATE_LIMITED |
| 84 | edge_case | en | lol | SKIP | ✅ | RATE_LIMITED |
| 85 | edge_case | en | t-shirts | SKIP | ✅ | RATE_LIMITED |
| 86 | about_brand | en | Tell me about tentree | SKIP | ✅ | RATE_LIMITED |
| 87 | about_brand | en | Who are you and what do you sell? | SKIP | ✅ | RATE_LIMITED |
| 88 | complaint | en | Your products are too expensive | SKIP | ✅ | RATE_LIMITED |
| 89 | complaint | en | I had a bad experience with my last order | SKIP | ✅ | RATE_LIMITED |
| 90 | complaint | en | Why is the quality so poor? | SKIP | ✅ | RATE_LIMITED |
| 91 | price_format | en | Show me t-shirts with prices | SKIP | ✅ | RATE_LIMITED |
| 92 | price_format | en | What's the price range of your products? | SKIP | ✅ | RATE_LIMITED |
| 93 | price_format | gu | t-shirts ની price શું છે? | SKIP | ✅ | RATE_LIMITED |

## ✅ No Critical Issues

## Price Format Validation

### ✅ All prices correctly formatted (no $₹ double symbol)

## Language Handling

### Mismatches (7)
- **ramraj** (gu): "ભારતના વડાપ્રધાન કોણ છે?" — Expected Gujarati response but got non-Gujarati
- **ramraj** (gu): "shirts ની price શું છે?" — Expected Gujarati response but got non-Gujarati
- **kriyanta** (gu): "services ની price શું છે?" — Expected Gujarati response but got non-Gujarati
- **zevaramaze** (hi): "मुझे bracelets चाहिए जो comfortable हो" — Expected Hindi response but got non-Hindi
- **zevaramaze** (hi): "पायथन स्क्रिप्ट लिखो" — Expected Hindi response but got non-Hindi
- **zevaramaze** (gu): "તમારી company નો GST number શું છે?" — Expected Gujarati response but got non-Gujarati; Bot fabricated info instead of flagging missing
- **zevaramaze** (gu): "gift માટે શું recommend કરો?" — Expected Gujarati response but got non-Gujarati; No suggestions returned

### Unsupported Language Rejection
| Bot | Lang | Query | Score | Rejected? |
|-----|------|-------|-------|-----------|
| ramraj | fr | Bonjour, montrez-moi vos produits les pl | 10/10 | ✅ |
| ramraj | ja | こんにちは、人気商品を教えてください | 10/10 | ✅ |
| ramraj | es | Hola, muéstrame tus productos más vendid | 10/10 | ✅ |
| ramraj | zh | 你好，给我看看你们最好的产品 | 10/10 | ✅ |
| ramraj | hi | नमस्ते! आपके पास कौन से shirts हैं? | 10/10 | ✅ |
| ramraj | hi | 500 रुपये से कम में क्या मिलेगा? | 10/10 | ✅ |
| kriyanta | fr | Bonjour, montrez-moi vos produits les pl | 10/10 | ✅ |
| kriyanta | ja | こんにちは、人気商品を教えてください | 10/10 | ✅ |
| kriyanta | es | Hola, muéstrame tus productos más vendid | 10/10 | ✅ |
| kriyanta | zh | 你好，给我看看你们最好的产品 | 10/10 | ✅ |
| kriyanta | hi | नमस्ते! आपके पास कौन से services हैं? | 10/10 | ✅ |
| kriyanta | hi | 500 रुपये से कम में क्या मिलेगा? | 10/10 | ✅ |
| zevaramaze | fr | Bonjour, montrez-moi vos produits les pl | 10/10 | ✅ |
| zevaramaze | ja | こんにちは、人気商品を教えてください | 10/10 | ✅ |
| zevaramaze | es | Hola, muéstrame tus productos más vendid | 10/10 | ✅ |
| zevaramaze | zh | 你好，给我看看你们最好的产品 | 10/10 | ✅ |
| beardbrand | fr | Bonjour, montrez-moi vos produits les pl | 10/10 | ✅ |
| beardbrand | ja | こんにちは、人気商品を教えてください | 10/10 | ✅ |
| beardbrand | es | Hola, muéstrame tus productos más vendid | 10/10 | ✅ |
| beardbrand | zh | 你好，给我看看你们最好的产品 | 10/10 | ✅ |
| beardbrand | hi | नमस्ते! आपके पास कौन से beard oil हैं? | 10/10 | ✅ |
| beardbrand | hi | 500 रुपये से कम में क्या मिलेगा? | 10/10 | ✅ |
| beardbrand | gu | તમારી પાસે કયા beard oil છે? | 10/10 | ✅ |
| deathwish | fr | Bonjour, montrez-moi vos produits les pl | 10/10 | ✅ |
| deathwish | ja | こんにちは、人気商品を教えてください | 10/10 | ✅ |
| deathwish | es | Hola, muéstrame tus productos más vendid | 10/10 | ✅ |
| deathwish | zh | 你好，给我看看你们最好的产品 | 10/10 | ✅ |
| deathwish | gu | તમારી પાસે કયા coffee છે? | 10/10 | ✅ |
| tentree | fr | Bonjour, montrez-moi vos produits les pl | 10/10 | ✅ |
| tentree | ja | こんにちは、人気商品を教えてください | 10/10 | ✅ |
| tentree | es | Hola, muéstrame tus productos más vendid | 10/10 | ✅ |
| tentree | zh | 你好，给我看看你们最好的产品 | 10/10 | ✅ |
| tentree | hi | नमस्ते! आपके पास कौन से t-shirts हैं? | 10/10 | ✅ |
| tentree | hi | 500 रुपये से कम में क्या मिलेगा? | 10/10 | ✅ |

## Missing Info Detection

Detection rate: **33/39** (84%)

| Bot | Query | Detected? | Score |
|-----|-------|-----------|-------|
| ramraj | Show me your product warranty certificates | ✅ | 7/10 |
| ramraj | What is the GSM rating of your cotton fabric? | ✅ | 7/10 |
| ramraj | What are your CEO's contact details? | ✅ | 7/10 |
| ramraj | What year was your company founded? | ✅ | 7/10 |
| ramraj | Can you show your ISO certification? | ✅ | 7/10 |
| ramraj | What's the thread count of your premium fabric? | ✅ | 7/10 |
| ramraj | તમારી company નો GST number શું છે? | ❌ Fabricated | 2/10 |
| kriyanta | Show me your product warranty certificates | ✅ | 7/10 |
| kriyanta | What is the GSM rating of your cotton fabric? | ✅ | 7/10 |
| kriyanta | What are your CEO's contact details? | ✅ | 7/10 |
| kriyanta | What year was your company founded? | ✅ | 7/10 |
| kriyanta | Can you show your ISO certification? | ✅ | 7/10 |
| kriyanta | What's the thread count of your premium fabric? | ✅ | 7/10 |
| kriyanta | તમારી company નો GST number શું છે? | ❌ Fabricated | 2/10 |
| zevaramaze | Show me your product warranty certificates | ✅ | 7/10 |
| zevaramaze | What is the GSM rating of your cotton fabric? | ✅ | 7/10 |
| zevaramaze | What are your CEO's contact details? | ✅ | 7/10 |
| zevaramaze | What year was your company founded? | ✅ | 7/10 |
| zevaramaze | Can you show your ISO certification? | ✅ | 7/10 |
| zevaramaze | What's the thread count of your premium fabric? | ✅ | 7/10 |
| zevaramaze | आपकी कंपनी का GSTIN नंबर क्या है? | ❌ Fabricated | 2/10 |
| zevaramaze | તમારી company નો GST number શું છે? | ❌ Fabricated | 2/10 |
| beardbrand | Show me your product warranty certificates | ✅ | 7/10 |
| beardbrand | What is the GSM rating of your cotton fabric? | ✅ | 7/10 |
| beardbrand | What are your CEO's contact details? | ✅ | 7/10 |
| beardbrand | What year was your company founded? | ✅ | 7/10 |
| beardbrand | Can you show your ISO certification? | ✅ | 7/10 |
| beardbrand | What's the thread count of your premium fabric? | ✅ | 7/10 |
| deathwish | Show me your product warranty certificates | ✅ | 7/10 |
| deathwish | What is the GSM rating of your cotton fabric? | ✅ | 7/10 |
| deathwish | What are your CEO's contact details? | ✅ | 7/10 |
| deathwish | What year was your company founded? | ✅ | 7/10 |
| deathwish | Can you show your ISO certification? | ✅ | 7/10 |
| deathwish | What's the thread count of your premium fabric? | ✅ | 7/10 |
| deathwish | आपकी कंपनी का GSTIN नंबर क्या है? | ❌ Fabricated | 2/10 |
| tentree | Show me your product warranty certificates | ✅ | 7/10 |
| tentree | What are your CEO's contact details? | ✅ | 7/10 |
| tentree | What year was your company founded? | ✅ | 7/10 |
| tentree | તમારી company નો GST number શું છે? | ❌ Fabricated | 2/10 |

## Irrelevant Query Rejection

Rejection rate: **68/72** (94%)

| Bot | Lang | Query | Score | Response Preview |
|-----|------|-------|-------|-----------------|
| ramraj | en | Can you write me a Python script to sort a li | 10/10 ✅ | I can only help with Ramraj products. What are you looking f |
| ramraj | en | Who is the Prime Minister of India? | 10/10 ✅ | I can only help with ramraj products. What are you looking f |
| ramraj | en | What is the capital of France? | 10/10 ✅ | I can only help with ramraj products. What are you looking f |
| ramraj | en | Tell me a joke about programming | 10/10 ✅ | I can only help with ramraj products. What are you looking f |
| ramraj | en | Explain quantum physics to me | 10/10 ✅ | I can only help with ramraj products. What are you looking f |
| ramraj | en | What's the weather like today? | 10/10 ✅ | I can only help with ramraj products. What are you looking f |
| ramraj | en | Who won the FIFA World Cup 2022? | 10/10 ✅ | I can only help with ramraj products. What are you looking f |
| ramraj | en | How do I make pasta at home? | 10/10 ✅ | I can only help with ramraj products. What are you looking f |
| ramraj | en | What is blockchain technology? | 10/10 ✅ | I can only help with ramraj products. What are you looking f |
| ramraj | en | Solve this math: 25 x 48 | 10/10 ✅ | I can only help with ramraj products. What are you looking f |
| ramraj | gu | ભારતના વડાપ્રધાન કોણ છે? | 10/10 ✅ | I can only help with Ramraj products. What are you looking f |
| ramraj | gu | મને એક જોક કહો | 2/10 ❌ | હું ફક્ત રામરાજ પ્રોડક્ટ્સ વિશે જ માહિતી આપી શકું છું. તમારે |
| kriyanta | en | Can you write me a Python script to sort a li | 10/10 ✅ | I can only help with Kriyanta products. What are you looking |
| kriyanta | en | Who is the Prime Minister of India? | 10/10 ✅ | I can only help with Kriyanta products. What are you looking |
| kriyanta | en | What is the capital of France? | 10/10 ✅ | I can only help with Kriyanta products. What are you looking |
| kriyanta | en | Tell me a joke about programming | 10/10 ✅ | I can only help with Kriyanta products. What are you looking |
| kriyanta | en | Explain quantum physics to me | 10/10 ✅ | I can only help with Kriyanta products. What are you looking |
| kriyanta | en | What's the weather like today? | 10/10 ✅ | I can only help with Kriyanta products. What are you looking |
| kriyanta | en | Who won the FIFA World Cup 2022? | 10/10 ✅ | I can only help with Kriyanta products. What are you looking |
| kriyanta | en | How do I make pasta at home? | 10/10 ✅ | I can only help with Kriyanta products. What are you looking |
| kriyanta | en | What is blockchain technology? | 10/10 ✅ | I can only help with Kriyanta products. What are you looking |
| kriyanta | en | Solve this math: 25 x 48 | 10/10 ✅ | I can only help with Kriyanta products. What are you looking |
| kriyanta | gu | ભારતના વડાપ્રધાન કોણ છે? | 6/10 ✅ | માફ કરજો, હું ફક્ત Kriyanta પ્રોડક્ટ્સ વિશે માહિતી આપી શકું  |
| kriyanta | gu | મને એક જોક કહો | 2/10 ❌ | માફ કરજો, હું ફક્ત Kriyanta પ્રોડક્ટ્સ વિશે માહિતી આપી શકું  |
| zevaramaze | en | Can you write me a Python script to sort a li | 10/10 ✅ | I can only help with Zevaramaze products. What are you looki |
| zevaramaze | en | Who is the Prime Minister of India? | 10/10 ✅ | I can only help with Zevaramaze products. What are you looki |
| zevaramaze | en | What is the capital of France? | 7/10 ✅ | I can only help with Zevaramaze products. What are you looki |
| zevaramaze | en | Tell me a joke about programming | 10/10 ✅ | I can only help with Zevaramaze products. What are you looki |
| zevaramaze | en | Explain quantum physics to me | 7/10 ✅ | I can only help with Zevaramaze products. What are you looki |
| zevaramaze | en | What's the weather like today? | 7/10 ✅ | I can only help with Zevaramaze products. What are you looki |
| zevaramaze | en | Who won the FIFA World Cup 2022? | 7/10 ✅ | I can only help with Zevaramaze products. What are you looki |
| zevaramaze | en | How do I make pasta at home? | 10/10 ✅ | I can only help with Zevaramaze products. What are you looki |
| zevaramaze | en | What is blockchain technology? | 10/10 ✅ | I can only help with Zevaramaze products. What are you looki |
| zevaramaze | en | Solve this math: 25 x 48 | 7/10 ✅ | I can only help with Zevaramaze products. What are you looki |
| zevaramaze | hi | भारत का प्रधानमंत्री कौन है? | 6/10 ✅ | मैं सिर्फ़ Zevaramaze के products के बारे में बता सकती हूँ।  |
| zevaramaze | hi | पायथन स्क्रिप्ट लिखो | 10/10 ✅ | I can only help with Zevaramaze products. What are you looki |
| zevaramaze | hi | चांद पर कौन गया था? | 2/10 ❌ | मैं सिर्फ़ Zevaramaze के products के बारे में बता सकती हूँ।  |
| beardbrand | en | Can you write me a Python script to sort a li | 10/10 ✅ | I can only help with Crawl-Beardbrand products. What are you |
| beardbrand | en | Who is the Prime Minister of India? | 10/10 ✅ | I can only help with Crawl-Beardbrand products. What are you |
| beardbrand | en | What is the capital of France? | 10/10 ✅ | I can only help with Crawl-Beardbrand products. What are you |
| beardbrand | en | Tell me a joke about programming | 10/10 ✅ | I can only help with Crawl-Beardbrand products. What are you |
| beardbrand | en | Explain quantum physics to me | 10/10 ✅ | I can only help with Crawl-Beardbrand products. What are you |
| beardbrand | en | What's the weather like today? | 10/10 ✅ | I can only help with Crawl-Beardbrand products. What are you |
| beardbrand | en | Who won the FIFA World Cup 2022? | 10/10 ✅ | I can only help with Crawl-Beardbrand products. What are you |
| beardbrand | en | How do I make pasta at home? | 10/10 ✅ | I can only help with Crawl-Beardbrand products. What are you |
| beardbrand | en | What is blockchain technology? | 10/10 ✅ | I can only help with Crawl-Beardbrand products. What are you |
| beardbrand | en | Solve this math: 25 x 48 | 10/10 ✅ | I can only help with Crawl-Beardbrand products. What are you |
| deathwish | en | Can you write me a Python script to sort a li | 10/10 ✅ | I can only help with Crawl-Death Wish Coffee products. What  |
| deathwish | en | Who is the Prime Minister of India? | 7/10 ✅ | I can only help with Crawl-Death Wish Coffee products. What  |
| deathwish | en | What is the capital of France? | 7/10 ✅ | I can only help with Crawl-Death Wish Coffee products. What  |
| deathwish | en | Tell me a joke about programming | 7/10 ✅ | I can only help with Crawl-Death Wish Coffee products. What  |
| deathwish | en | Explain quantum physics to me | 7/10 ✅ | I can only help with Crawl-Death Wish Coffee products. What  |
| deathwish | en | What's the weather like today? | 7/10 ✅ | I can only help with Crawl-Death Wish Coffee products. What  |
| deathwish | en | Who won the FIFA World Cup 2022? | 7/10 ✅ | I can only help with Crawl-Death Wish Coffee products. What  |
| deathwish | en | How do I make pasta at home? | 7/10 ✅ | I can only help with Crawl-Death Wish Coffee products. What  |
| deathwish | en | What is blockchain technology? | 7/10 ✅ | I can only help with Crawl-Death Wish Coffee products. What  |
| deathwish | en | Solve this math: 25 x 48 | 7/10 ✅ | I can only help with Crawl-Death Wish Coffee products. What  |
| deathwish | hi | भारत का प्रधानमंत्री कौन है? | 10/10 ✅ | I can only help with Crawl-Death Wish Coffee products. What  |
| deathwish | hi | पायथन स्क्रिप्ट लिखो | 10/10 ✅ | I can only help with Crawl-Death Wish Coffee products. What  |
| deathwish | hi | चांद पर कौन गया था? | 10/10 ✅ | I can only help with Crawl-Death Wish Coffee products. What  |
| tentree | en | Can you write me a Python script to sort a li | 10/10 ✅ | I can only help with Crawl-Tentree products. What are you lo |
| tentree | en | Who is the Prime Minister of India? | -1/10 ✅ | I'm sorry, I'm getting a lot of requests right now. Please t |
| tentree | en | What is the capital of France? | 10/10 ✅ | I can only help with Crawl-Tentree products. What are you lo |
| tentree | en | Tell me a joke about programming | 10/10 ✅ | I can only help with Crawl-Tentree products. What are you lo |
| tentree | en | Explain quantum physics to me | -1/10 ✅ | I'm sorry, I'm getting a lot of requests right now. Please t |
| tentree | en | What's the weather like today? | 10/10 ✅ | I can only help with Crawl-Tentree products. What are you lo |
| tentree | en | Who won the FIFA World Cup 2022? | 10/10 ✅ | I can only help with Crawl-Tentree products. What are you lo |
| tentree | en | How do I make pasta at home? | -1/10 ✅ | I'm sorry, I'm getting a lot of requests right now. Please t |
| tentree | en | What is blockchain technology? | 10/10 ✅ | I can only help with Crawl-Tentree products. What are you lo |
| tentree | en | Solve this math: 25 x 48 | 10/10 ✅ | I can only help with Crawl-Tentree products. What are you lo |
| tentree | gu | ભારતના વડાપ્રધાન કોણ છે? | -1/10 ✅ | I'm sorry, I'm getting a lot of requests right now. Please t |
| tentree | gu | મને એક જોક કહો | 2/10 ❌ | માફ કરજો, હું જોક કહી શકતો નથી. હું Crawl-Tentree ના પ્રોડક્ |

## Poorly Performing Queries (Score < 5)

### `suggestions_test` — 15 failures
- **ramraj** (en): "I'm new here, what shirts do you sell?" → 3/10
  Issues: No suggestions returned
  Response: "Oh nice, here's what we've got! Take a look at these beauties!
```json
[
  "Whic..."
- **ramraj** (en): "What do you recommend for a gift?" → 3/10
  Issues: No suggestions returned
  Response: "I don't have enough information to recommend a specific gift. ..."
- **ramraj** (gu): "gift માટે શું recommend કરો?" → 3/10
  Issues: No suggestions returned
  Response: "Gift માટે શું જોઈએ છે એના પર આધાર રાખે છે! Ramraj માંથી તમને શું ગમે છે એ કહો, પ..."
- **kriyanta** (en): "I'm new here, what services do you sell?" → 3/10
  Issues: No suggestions returned
  Response: "We've got a heaven for unique and customized products! We also offer:
- Free Int..."
- **kriyanta** (en): "What do you recommend for a gift?" → 3/10
  Issues: No suggestions returned
  Response: "Oh nice, here's what we've got! Take a look at these beauties!
```json
[
  "What..."
- **kriyanta** (gu): "gift માટે શું recommend કરો?" → 3/10
  Issues: No suggestions returned
  Response: "તમારું કલેક્શન છે આ! Kriyanta માં gifts માટે આ રહ્યા options.
```json
[
  "મારે ..."
- **zevaramaze** (en): "I'm new here, what bracelets do you sell?" → 3/10
  Issues: No suggestions returned
  Response: "Oh nice, here's what we've got! I can show you the bracelets we have in stock.
`..."
- **zevaramaze** (en): "What do you recommend for a gift?" → 3/10
  Issues: No suggestions returned
  Response: "I'd be glad to help you find a gift! Can you tell me a bit about who you're shop..."
- **zevaramaze** (hi): "यहां क्या-क्या मिलता है?" → 3/10
  Issues: No suggestions returned
  Response: "अरे वाह, यहाँ बहुत कुछ है! Zevaramaze में आपको कई तरह के options मिल जाएंगे!
```..."
- **zevaramaze** (gu): "gift માટે શું recommend કરો?" → 3/10
  Issues: Expected Gujarati response but got non-Gujarati; No suggestions returned
  Response: "Gift mate? Hmm, tame konanaa mate kharidi karo chho ane occasion kai chhe?..."

### `non_product` — 9 failures
- **ramraj** (gu): "રિટર્ન પોલિસી શું છે?" → 4/10
  Response: "મારી પાસે એ માહિતી નથી. ..."
- **ramraj** (gu): "ડિલિવરી કેટલા દિવસમાં થાય?" → 4/10
  Response: "એ માહિતી અત્યારે મારી પાસે નથી. ..."
- **kriyanta** (gu): "ડિલિવરી કેટલા દિવસમાં થાય?" → 4/10
  Response: "મને એ માહિતી નથી. ..."
- **zevaramaze** (gu): "રિટર્ન પોલિસી શું છે?" → 4/10
  Response: "માફ કરશો, પણ રિટર્ન પોલિસી વિશે information currently available નથી. ..."
- **zevaramaze** (gu): "ડિલિવરી કેટલા દિવસમાં થાય?" → 4/10
  Response: "માફ કરશો, ડિલિવરી કેટલા દિવસમાં થાય છે એ માહિતી મારી પાસે નથી. ..."
- **beardbrand** (en): "What is your return policy?" → 4/10
  Response: "[SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl...."
- **deathwish** (hi): "रिटर्न पॉलिसी क्या है?" → 4/10
  Response: "मुझे वह जानकारी नहीं है। ..."
- **deathwish** (hi): "delivery कितने दिन में होती है?" → 4/10
  Response: "मुझे वह जानकारी नहीं है। ..."
- **tentree** (gu): "ડિલિવરી કેટલા દિવસમાં થાય?" → 4/10
  Response: "ડિલિવરી વિશે માહિતી અહીં ઉપલબ્ધ નથી ..."

### `missing_info` — 6 failures
- **ramraj** (gu): "તમારી company નો GST number શું છે?" → 2/10
  Issues: Bot fabricated info instead of flagging missing
  Response: "માફ કરશો, મારી પાસે એ information નથી. ..."
- **kriyanta** (gu): "તમારી company નો GST number શું છે?" → 2/10
  Issues: Bot fabricated info instead of flagging missing
  Response: "માફ કરશો, GST નંબર વિશે માહિતી મારી પાસે નથી. ..."
- **zevaramaze** (hi): "आपकी कंपनी का GSTIN नंबर क्या है?" → 2/10
  Issues: Bot fabricated info instead of flagging missing
  Response: "Sorry, मेरे पास ये information नहीं है। ..."
- **zevaramaze** (gu): "તમારી company નો GST number શું છે?" → 2/10
  Issues: Expected Gujarati response but got non-Gujarati; Bot fabricated info instead of flagging missing
  Response: "Sorry, mara pase e information nathi. ..."
- **deathwish** (hi): "आपकी कंपनी का GSTIN नंबर क्या है?" → 2/10
  Issues: Bot fabricated info instead of flagging missing
  Response: "Sorry, मुझे वो information नहीं है। ..."
- **tentree** (gu): "તમારી company નો GST number શું છે?" → 2/10
  Issues: Bot fabricated info instead of flagging missing
  Response: "માફ કરશો, એ માહિતી અહીં ઉપલબ્ધ નથી ..."

### `irrelevant` — 4 failures
- **ramraj** (gu): "મને એક જોક કહો" → 2/10
  Issues: Bot answered irrelevant question instead of rejecting
  Response: "હું ફક્ત રામરાજ પ્રોડક્ટ્સ વિશે જ માહિતી આપી શકું છું. તમારે શું જોઈએ છે?
```jso..."
- **kriyanta** (gu): "મને એક જોક કહો" → 2/10
  Issues: Bot answered irrelevant question instead of rejecting
  Response: "માફ કરજો, હું ફક્ત Kriyanta પ્રોડક્ટ્સ વિશે માહિતી આપી શકું છું. તમારે શું જોઈએ ..."
- **zevaramaze** (hi): "चांद पर कौन गया था?" → 2/10
  Issues: Bot answered irrelevant question instead of rejecting
  Response: "मैं सिर्फ़ Zevaramaze के products के बारे में बता सकती हूँ। आपको क्या चाहिए?
```..."
- **tentree** (gu): "મને એક જોક કહો" → 2/10
  Issues: Bot answered irrelevant question instead of rejecting
  Response: "માફ કરજો, હું જોક કહી શકતો નથી. હું Crawl-Tentree ના પ્રોડક્ટ્સ વિશે મદદ કરી શકુ..."

### `product_browse` — 3 failures
- **ramraj** (gu): "શું dhotis available છે?" → 4/10
  Issues: No products returned or mentioned
  Response: "જી હા, ચોક્કસ! Dhotis તો અમારી પાસે ઘણી જાતના છે. તમે કઈ type ની dhoti શોધી રહ્ય..."
- **kriyanta** (gu): "તમારા services બતાવો" → 4/10
  Issues: No products returned or mentioned
  Response: "અરે વાહ! Kriyanta તમને આ બધું offer કરે છે:
- Unique અને customized પ્રોડક્ટ્સ
-..."
- **kriyanta** (gu): "શું solutions available છે?" → 4/10
  Issues: No products returned or mentioned
  Response: "મને બરાબર ખબર નથી કે તમે શેના વિશે વાત કરી રહ્યા છો. શું તમે પ્રોડક્ટ વિશે પૂછી ..."

### `price_filter` — 3 failures
- **kriyanta** (en): "Show me services under $50" → 4/10
  Issues: No price info
  Response: "I can only help with kriyanta products. What are you looking for?
```json
[
"Wha..."
- **kriyanta** (en): "services between $20 and $100" → 4/10
  Issues: No price info
  Response: "I can only help with kriyanta products. What are you looking for? ..."
- **kriyanta** (en): "What's the cheapest solutions?" → 4/10
  Issues: No price info
  Response: "I can only help with kriyanta products. What are you looking for?
```json
[
"Wha..."

### `specific_product` — 1 failures
- **kriyanta** (gu): "મને services જોઈએ છે" → 4/10
  Issues: No products returned or mentioned
  Response: "માફ કરશો, હું ફક્ત kriyanta પ્રોડક્ટ્સ વિશે જ માહિતી આપી શકું છુ. તમે શું શોધી ર..."

### `comparison` — 1 failures
- **kriyanta** (en): "What's the difference between your services and so" → 4/10
  Response: "I am sorry, I don't have that information. ..."

## Algorithm Health Scorecard

| Capability | Status | Details |
|------------|--------|---------|
| Language Detection | ✅ 100% | 24/24 passed, avg 10.0/10 |
| Hindi Rejection (on non-hi bots) | ✅ 100% | 8/8 passed, avg 10.0/10 |
| Irrelevant Query Rejection | ✅ 94% | 64/68 passed, avg 8.8/10 |
| Missing Info Detection | ✅ 84% | 33/39 passed, avg 6.2/10 |
| Product Search | ✅ 93% | 45/48 passed, avg 8.3/10 |
| Price Filtering | ✅ 92% | 39/42 passed, avg 7.5/10 |
| Color Filtering | ✅ 100% | 24/24 passed, avg 7.8/10 |
| Greetings | ✅ 100% | 30/30 passed, avg 9.0/10 |
| Policy/FAQ | ✅ 80% | 38/47 passed, avg 7.0/10 |
| Comparison Queries | ✅ 93% | 15/16 passed, avg 8.6/10 |
| Edge Cases | ✅ 100% | 42/42 passed, avg 7.0/10 |
| Romanized Text | ✅ 100% | 16/16 passed, avg 8.0/10 |
| Brand Info | ✅ 100% | 12/12 passed, avg 8.0/10 |