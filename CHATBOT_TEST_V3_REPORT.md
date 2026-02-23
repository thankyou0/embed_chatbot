# Chatbot Test Suite v3 — Post-Fix Validation Report

**Generated:** 2026-02-21 11:42:54
**Bots tested:** 6

## Summary
| Metric | Value |
|--------|-------|
| Total queries | 113 |
| Passed | 96 (84%) |
| Failed | 17 (15%) |
| Skipped (rate limit) | 0 |

## Per-Bot Results

### ramraj (Fashion/Clothing)
- **Languages configured:** ['en', 'gu']
- **Queries:** 18 | Passed: 18 | Failed: 0 | Skipped: 0
- **Average score:** 8.5/10

| # | Type | Lang | Query | Score | Status | Issues |
|---|------|------|-------|-------|--------|--------|
| 1 | greeting | en | Hi there! What can you help me with? | 10/10 | ✅ | - |
| 2 | greeting | gu | નમસ્તે! તમે મને કેવી રીતે મદદ કરી શકો? | 10/10 | ✅ | - |
| 3 | product_browse | en | Show me your best shirts | 9/10 | ✅ | - |
| 4 | product_browse | en | What dhotis do you have? | 6/10 | ✅ | - |
| 5 | product_browse | gu | તમારી પાસે કયા shirts છે? | 9/10 | ✅ | - |
| 6 | specific_product | en | I'm looking for a premium cotton shirts | 9/10 | ✅ | - |
| 7 | price_query | en | Show me shirts under $50 | 8/10 | ✅ | - |
| 8 | non_product | en | What is your return policy? | 8/10 | ✅ | - |
| 9 | irrelevant | en | Can you write me a Python script to sort a list? | 6/10 | ✅ | - |
| 10 | irrelevant | gu | ભારતના વડાપ્રધાન કોણ છે? | 6/10 | ✅ | - |
| 11 | unsupported_lang | fr | Bonjour, montrez-moi vos produits les plus populai | 10/10 | ✅ | - |
| 12 | unsupported_lang | ja | こんにちは、人気商品を教えてください | 10/10 | ✅ | - |
| 13 | unsupported_lang_hindi | hi | नमस्ते! आपके पास कौन से शर्ट्स उपलब्ध हैं? | 10/10 | ✅ | Hindi query on non-Hindi bot got non-English response (should be rejected) |
| 14 | unsupported_lang_hindi | hi | 500 रुपये से कम के shirts बताओ | 10/10 | ✅ | Hindi query on non-Hindi bot got non-English response (should be rejected) |
| 15 | suggestions_test | en | I'm new here, what kind of shirts do you sell? | 10/10 | ✅ | - |
| 16 | missing_info | en | What are the exact fabric materials and GSM for ea | 7/10 | ✅ | - |
| 17 | missing_info | en | Can you show me your product warranty certificates | 7/10 | ✅ | - |
| 18 | about_brand | en | Tell me about ramraj and what you sell | 8/10 | ✅ | - |

### kriyanta (Tech/Startup)
- **Languages configured:** ['en', 'gu']
- **Queries:** 18 | Passed: 15 | Failed: 3 | Skipped: 0
- **Average score:** 7.4/10

| # | Type | Lang | Query | Score | Status | Issues |
|---|------|------|-------|-------|--------|--------|
| 1 | greeting | en | Hi there! What can you help me with? | 10/10 | ✅ | - |
| 2 | greeting | gu | નમસ્તે! તમે મને કેવી રીતે મદદ કરી શકો? | 10/10 | ✅ | - |
| 3 | product_browse | en | Show me your best services | 6/10 | ✅ | - |
| 4 | product_browse | en | What solutions do you have? | 6/10 | ✅ | - |
| 5 | product_browse | gu | તમારી પાસે કયા services છે? | 4/10 | ❌ | No products returned or mentioned |
| 6 | specific_product | en | I'm looking for a premium portfolio | 8/10 | ✅ | 1 products have data quality issues |
| 7 | price_query | en | Show me services under $50 | 8/10 | ✅ | - |
| 8 | non_product | en | What is your return policy? | 8/10 | ✅ | - |
| 9 | irrelevant | en | Can you write me a Python script to sort a list? | 2/10 | ❌ | Bot answered irrelevant question instead of rejecting |
| 10 | irrelevant | gu | ભારતના વડાપ્રધાન કોણ છે? | 6/10 | ✅ | - |
| 11 | unsupported_lang | fr | Bonjour, montrez-moi vos produits les plus populai | 10/10 | ✅ | - |
| 12 | unsupported_lang | ja | こんにちは、人気商品を教えてください | 10/10 | ✅ | - |
| 13 | unsupported_lang_hindi | hi | नमस्ते! आपके पास कौन से शर्ट्स उपलब्ध हैं? | 10/10 | ✅ | Hindi query on non-Hindi bot got non-English response (should be rejected) |
| 14 | unsupported_lang_hindi | hi | 500 रुपये से कम के shirts बताओ | 10/10 | ✅ | Hindi query on non-Hindi bot got non-English response (should be rejected) |
| 15 | suggestions_test | en | I'm new here, what kind of services do you sell? | 8/10 | ✅ | - |
| 16 | missing_info | en | What are the exact fabric materials and GSM for ea | 7/10 | ✅ | - |
| 17 | missing_info | en | Can you show me your product warranty certificates | 2/10 | ❌ | Bot fabricated info instead of flagging missing data |
| 18 | about_brand | en | Tell me about kriyanta and what you sell | 8/10 | ✅ | - |

### zevaramaze (Jewelry)
- **Languages configured:** ['en', 'hi', 'gu']
- **Queries:** 22 | Passed: 18 | Failed: 4 | Skipped: 0
- **Average score:** 7.4/10

| # | Type | Lang | Query | Score | Status | Issues |
|---|------|------|-------|-------|--------|--------|
| 1 | greeting | en | Hi there! What can you help me with? | 10/10 | ✅ | - |
| 2 | greeting | hi | नमस्ते! आप मेरी कैसे मदद कर सकते हैं? | 9/10 | ✅ | - |
| 3 | greeting | gu | નમસ્તે! તમે મને કેવી રીતે મદદ કરી શકો? | 9/10 | ✅ | - |
| 4 | product_browse | en | Show me your best bracelets | 6/10 | ✅ | - |
| 5 | product_browse | en | What necklaces do you have? | 9/10 | ✅ | - |
| 6 | product_browse | hi | आपके पास कौन से bracelets उपलब्ध हैं? | 9/10 | ✅ | - |
| 7 | product_browse | gu | તમારી પાસે કયા bracelets છે? | 9/10 | ✅ | - |
| 8 | specific_product | en | I'm looking for a premium rings | 9/10 | ✅ | - |
| 9 | specific_product | hi | मुझे bracelets चाहिए जो बहुत अच्छी क्वालिटी का हो | 9/10 | ✅ | - |
| 10 | price_query | en | Show me bracelets under $50 | 8/10 | ✅ | - |
| 11 | price_query | hi | 500 रुपये से कम के bracelets बताओ | 4/10 | ❌ | No price info in response |
| 12 | non_product | en | What is your return policy? | 8/10 | ✅ | - |
| 13 | non_product | hi | रिटर्न पॉलिसी क्या है? | 4/10 | ❌ | No policy information found |
| 14 | irrelevant | en | Can you write me a Python script to sort a list? | 2/10 | ❌ | Bot answered irrelevant question instead of rejecting |
| 15 | irrelevant | hi | भारत का प्रधानमंत्री कौन है? | 6/10 | ✅ | - |
| 16 | unsupported_lang | fr | Bonjour, montrez-moi vos produits les plus populai | 10/10 | ✅ | - |
| 17 | unsupported_lang | ja | こんにちは、人気商品を教えてください | 10/10 | ✅ | - |
| 18 | suggestions_test | en | I'm new here, what kind of bracelets do you sell? | 10/10 | ✅ | - |
| 19 | suggestions_test | hi | यहां क्या-क्या मिलता है? | 8/10 | ✅ | - |
| 20 | missing_info | en | What are the exact fabric materials and GSM for ea | 7/10 | ✅ | - |
| 21 | missing_info | en | Can you show me your product warranty certificates | 7/10 | ✅ | - |
| 22 | about_brand | en | Tell me about zevaramaze and what you sell | 0/10 | ❌ | ERROR: ('Connection aborted.', ConnectionResetError(10054, 'An existing connecti |

### beardbrand (Grooming)
- **Languages configured:** ['en']
- **Queries:** 16 | Passed: 14 | Failed: 2 | Skipped: 0
- **Average score:** 7.7/10

| # | Type | Lang | Query | Score | Status | Issues |
|---|------|------|-------|-------|--------|--------|
| 1 | greeting | en | Hi there! What can you help me with? | 0/10 | ❌ | ERROR: ('Connection aborted.', ConnectionResetError(10054, 'An existing connecti |
| 2 | product_browse | en | Show me your best beard oil | 8/10 | ✅ | 4 products have data quality issues |
| 3 | product_browse | en | What beard balm do you have? | 8/10 | ✅ | 4 products have data quality issues |
| 4 | specific_product | en | I'm looking for a premium grooming kit | 8/10 | ✅ | 3 products have data quality issues |
| 5 | price_query | en | Show me beard oil under $50 | 8/10 | ✅ | - |
| 6 | non_product | en | What is your return policy? | 8/10 | ✅ | - |
| 7 | irrelevant | en | Can you write me a Python script to sort a list? | 6/10 | ✅ | - |
| 8 | unsupported_lang | fr | Bonjour, montrez-moi vos produits les plus populai | 10/10 | ✅ | - |
| 9 | unsupported_lang | ja | こんにちは、人気商品を教えてください | 10/10 | ✅ | - |
| 10 | unsupported_lang_hindi | hi | नमस्ते! आपके पास कौन से शर्ट्स उपलब्ध हैं? | 10/10 | ✅ | Hindi query on non-Hindi bot got non-English response (should be rejected) |
| 11 | unsupported_lang_hindi | hi | 500 रुपये से कम के shirts बताओ | 10/10 | ✅ | Hindi query on non-Hindi bot got non-English response (should be rejected) |
| 12 | unsupported_lang_gujarati | gu | નમસ્તે! તમારી પાસે કયા products છે? | 10/10 | ✅ | Gujarati query on non-Gujarati bot got script response (should be rejected) |
| 13 | suggestions_test | en | I'm new here, what kind of beard oil do you sell? | 10/10 | ✅ | - |
| 14 | missing_info | en | What are the exact fabric materials and GSM for ea | 7/10 | ✅ | - |
| 15 | missing_info | en | Can you show me your product warranty certificates | 2/10 | ❌ | Bot fabricated info instead of flagging missing data |
| 16 | about_brand | en | Tell me about beardbrand and what you sell | 8/10 | ✅ | - |

### deathwish (Coffee/Beverage)
- **Languages configured:** ['en', 'hi']
- **Queries:** 21 | Passed: 17 | Failed: 4 | Skipped: 0
- **Average score:** 7.4/10

| # | Type | Lang | Query | Score | Status | Issues |
|---|------|------|-------|-------|--------|--------|
| 1 | greeting | en | Hi there! What can you help me with? | 10/10 | ✅ | - |
| 2 | greeting | hi | नमस्ते! आप मेरी कैसे मदद कर सकते हैं? | 10/10 | ✅ | - |
| 3 | product_browse | en | Show me your best coffee | 9/10 | ✅ | - |
| 4 | product_browse | en | What ground coffee do you have? | 9/10 | ✅ | - |
| 5 | product_browse | hi | आपके पास कौन से coffee उपलब्ध हैं? | 9/10 | ✅ | - |
| 6 | specific_product | en | I'm looking for a premium K-cups | 9/10 | ✅ | - |
| 7 | specific_product | hi | मुझे coffee चाहिए जो बहुत अच्छी क्वालिटी का हो | 9/10 | ✅ | - |
| 8 | price_query | en | Show me coffee under $50 | 8/10 | ✅ | - |
| 9 | price_query | hi | 500 रुपये से कम के coffee बताओ | 8/10 | ✅ | - |
| 10 | non_product | en | What is your return policy? | 8/10 | ✅ | - |
| 11 | non_product | hi | रिटर्न पॉलिसी क्या है? | 4/10 | ❌ | No policy information found |
| 12 | irrelevant | en | Can you write me a Python script to sort a list? | 2/10 | ❌ | Bot answered irrelevant question instead of rejecting |
| 13 | irrelevant | hi | भारत का प्रधानमंत्री कौन है? | 6/10 | ✅ | - |
| 14 | unsupported_lang | fr | Bonjour, montrez-moi vos produits les plus populai | 10/10 | ✅ | - |
| 15 | unsupported_lang | ja | こんにちは、人気商品を教えてください | 1/10 | ❌ | CRITICAL: No language rejection — responded in unsupported language |
| 16 | unsupported_lang_gujarati | gu | નમસ્તે! તમારી પાસે કયા products છે? | 10/10 | ✅ | Gujarati query on non-Gujarati bot got script response (should be rejected) |
| 17 | suggestions_test | en | I'm new here, what kind of coffee do you sell? | 10/10 | ✅ | - |
| 18 | suggestions_test | hi | यहां क्या-क्या मिलता है? | 6/10 | ✅ | - |
| 19 | missing_info | en | What are the exact fabric materials and GSM for ea | 7/10 | ✅ | - |
| 20 | missing_info | en | Can you show me your product warranty certificates | 2/10 | ❌ | Bot fabricated info instead of flagging missing data |
| 21 | about_brand | en | Tell me about deathwish and what you sell | 8/10 | ✅ | - |

### tentree (Fashion/Eco)
- **Languages configured:** ['en', 'gu']
- **Queries:** 18 | Passed: 14 | Failed: 4 | Skipped: 0
- **Average score:** 7.3/10

| # | Type | Lang | Query | Score | Status | Issues |
|---|------|------|-------|-------|--------|--------|
| 1 | greeting | en | Hi there! What can you help me with? | 10/10 | ✅ | - |
| 2 | greeting | gu | નમસ્તે! તમે મને કેવી રીતે મદદ કરી શકો? | 10/10 | ✅ | - |
| 3 | product_browse | en | Show me your best t-shirts | 9/10 | ✅ | - |
| 4 | product_browse | en | What hoodies do you have? | 9/10 | ✅ | - |
| 5 | product_browse | gu | તમારી પાસે કયા t-shirts છે? | 9/10 | ✅ | - |
| 6 | specific_product | en | I'm looking for a premium joggers | 9/10 | ✅ | - |
| 7 | price_query | en | Show me t-shirts under $50 | 8/10 | ✅ | - |
| 8 | non_product | en | What is your return policy? | 8/10 | ✅ | - |
| 9 | irrelevant | en | Can you write me a Python script to sort a list? | 2/10 | ❌ | Bot answered irrelevant question instead of rejecting |
| 10 | irrelevant | gu | ભારતના વડાપ્રધાન કોણ છે? | 2/10 | ❌ | Bot answered irrelevant question instead of rejecting |
| 11 | unsupported_lang | fr | Bonjour, montrez-moi vos produits les plus populai | 1/10 | ❌ | CRITICAL: No language rejection — responded in unsupported language |
| 12 | unsupported_lang | ja | こんにちは、人気商品を教えてください | 10/10 | ✅ | - |
| 13 | unsupported_lang_hindi | hi | नमस्ते! आपके पास कौन से शर्ट्स उपलब्ध हैं? | 10/10 | ✅ | Hindi query on non-Hindi bot got non-English response (should be rejected) |
| 14 | unsupported_lang_hindi | hi | 500 रुपये से कम के shirts बताओ | 10/10 | ✅ | Hindi query on non-Hindi bot got non-English response (should be rejected) |
| 15 | suggestions_test | en | I'm new here, what kind of t-shirts do you sell? | 10/10 | ✅ | - |
| 16 | missing_info | en | What are the exact fabric materials and GSM for ea | 7/10 | ✅ | - |
| 17 | missing_info | en | Can you show me your product warranty certificates | 7/10 | ✅ | - |
| 18 | about_brand | en | Tell me about tentree and what you sell | 0/10 | ❌ | ERROR: ('Connection aborted.', ConnectionResetError(10054, 'An existing connecti |

## 🚨 Critical Issues
- **deathwish**: CRITICAL: No language rejection — responded in unsupported language — Query: "こんにちは、人気商品を教えてください"
- **tentree**: CRITICAL: No language rejection — responded in unsupported language — Query: "Bonjour, montrez-moi vos produits les plus populaires"

## Language Handling Analysis

### ❌ Language Mismatches (10)
- **ramraj** (hi): "नमस्ते! आपके पास कौन से शर्ट्स उपलब्ध हैं?" — Hindi query on non-Hindi bot got non-English response (should be rejected)
- **ramraj** (hi): "500 रुपये से कम के shirts बताओ" — Hindi query on non-Hindi bot got non-English response (should be rejected)
- **kriyanta** (hi): "नमस्ते! आपके पास कौन से शर्ट्स उपलब्ध हैं?" — Hindi query on non-Hindi bot got non-English response (should be rejected)
- **kriyanta** (hi): "500 रुपये से कम के shirts बताओ" — Hindi query on non-Hindi bot got non-English response (should be rejected)
- **beardbrand** (hi): "नमस्ते! आपके पास कौन से शर्ट्स उपलब्ध हैं?" — Hindi query on non-Hindi bot got non-English response (should be rejected)
- **beardbrand** (hi): "500 रुपये से कम के shirts बताओ" — Hindi query on non-Hindi bot got non-English response (should be rejected)
- **beardbrand** (gu): "નમસ્તે! તમારી પાસે કયા products છે?" — Gujarati query on non-Gujarati bot got script response (should be rejected)
- **deathwish** (gu): "નમસ્તે! તમારી પાસે કયા products છે?" — Gujarati query on non-Gujarati bot got script response (should be rejected)
- **tentree** (hi): "नमस्ते! आपके पास कौन से शर्ट्स उपलब्ध हैं?" — Hindi query on non-Hindi bot got non-English response (should be rejected)
- **tentree** (hi): "500 रुपये से कम के shirts बताओ" — Hindi query on non-Hindi bot got non-English response (should be rejected)

### Unsupported Language Rejection Tests
| Bot | Lang | Query | Score | Rejected? | Response Preview |
|-----|------|-------|-------|-----------|-----------------|
| ramraj | fr | Bonjour, montrez-moi vos produits les pl | 10/10 | ✅ Yes | I'm sorry, this language is not supported for this chatbot.  |
| ramraj | ja | こんにちは、人気商品を教えてください | 10/10 | ✅ Yes | I'm sorry, this language is not supported for this chatbot.  |
| ramraj | hi | नमस्ते! आपके पास कौन से शर्ट्स उपलब्ध है | 10/10 | ✅ Yes | I'm sorry, Hindi (हिंदी) is not supported for this chatbot.  |
| ramraj | hi | 500 रुपये से कम के shirts बताओ | 10/10 | ✅ Yes | I'm sorry, Hindi (हिंदी) is not supported for this chatbot.  |
| kriyanta | fr | Bonjour, montrez-moi vos produits les pl | 10/10 | ✅ Yes | I'm sorry, this language is not supported for this chatbot.  |
| kriyanta | ja | こんにちは、人気商品を教えてください | 10/10 | ✅ Yes | I'm sorry, this language is not supported for this chatbot.  |
| kriyanta | hi | नमस्ते! आपके पास कौन से शर्ट्स उपलब्ध है | 10/10 | ✅ Yes | I'm sorry, Hindi (हिंदी) is not supported for this chatbot.  |
| kriyanta | hi | 500 रुपये से कम के shirts बताओ | 10/10 | ✅ Yes | I'm sorry, Hindi (हिंदी) is not supported for this chatbot.  |
| zevaramaze | fr | Bonjour, montrez-moi vos produits les pl | 10/10 | ✅ Yes | I'm sorry, this language is not supported for this chatbot.  |
| zevaramaze | ja | こんにちは、人気商品を教えてください | 10/10 | ✅ Yes | I'm sorry, this language is not supported for this chatbot.  |
| beardbrand | fr | Bonjour, montrez-moi vos produits les pl | 10/10 | ✅ Yes | I'm sorry, this language is not supported for this chatbot.  |
| beardbrand | ja | こんにちは、人気商品を教えてください | 10/10 | ✅ Yes | I'm sorry, this language is not supported for this chatbot.  |
| beardbrand | hi | नमस्ते! आपके पास कौन से शर्ट्स उपलब्ध है | 10/10 | ✅ Yes | I'm sorry, Hindi (हिंदी) is not supported for this chatbot.  |
| beardbrand | hi | 500 रुपये से कम के shirts बताओ | 10/10 | ✅ Yes | I'm sorry, Hindi (हिंदी) is not supported for this chatbot.  |
| beardbrand | gu | નમસ્તે! તમારી પાસે કયા products છે? | 10/10 | ✅ Yes | I'm sorry, Gujarati (ગુજરાતી) is not supported for this chat |
| deathwish | fr | Bonjour, montrez-moi vos produits les pl | 10/10 | ✅ Yes | I'm sorry, this language is not supported for this chatbot.  |
| deathwish | ja | こんにちは、人気商品を教えてください | 1/10 | ❌ No | अरे, यहाँ हम **कॉफ़ी** के बारे में बात करते हैं! यह प्रश्न ह |
| deathwish | gu | નમસ્તે! તમારી પાસે કયા products છે? | 10/10 | ✅ Yes | I'm sorry, Gujarati (ગુજરાતી) is not supported for this chat |
| tentree | fr | Bonjour, montrez-moi vos produits les pl | 1/10 | ❌ No | Take a look at these beauties! We've got a great selection o |
| tentree | ja | こんにちは、人気商品を教えてください | 10/10 | ✅ Yes | I'm sorry, this language is not supported for this chatbot.  |
| tentree | hi | नमस्ते! आपके पास कौन से शर्ट्स उपलब्ध है | 10/10 | ✅ Yes | I'm sorry, Hindi (हिंदी) is not supported for this chatbot.  |
| tentree | hi | 500 रुपये से कम के shirts बताओ | 10/10 | ✅ Yes | I'm sorry, Hindi (हिंदी) is not supported for this chatbot.  |

## Suggestion Quality Analysis
| Bot | Query | Score | Quality | Details |
|-----|-------|-------|---------|---------|
| ramraj | I'm new here, what kind of shi | 10/10 | Excellent suggestions | [6/6] "What's the price range of your shirts?" (product_relevant, user_perspecti |
| kriyanta | I'm new here, what kind of ser | 8/10 | Good suggestions | [5/6] "What products do you have under $50?" (generically_useful, user_perspecti |
| zevaramaze | I'm new here, what kind of bra | 10/10 | Excellent suggestions | [6/6] "What's the price range of these bracelet" (product_relevant, user_perspec |
| zevaramaze | यहां क्या-क्या मिलता है? | 8/10 | Good suggestions | [4/6] "इनमें से सबसे popular कौनसा है?" (generically_useful) | [4/6] "क्या इसका  |
| beardbrand | I'm new here, what kind of bea | 10/10 | Excellent suggestions | [4/6] "What's the difference between the variou" (possibly_generic, user_perspec |
| deathwish | I'm new here, what kind of cof | 10/10 | Excellent suggestions | [5/6] "What's the best seller among these produ" (generically_useful, user_persp |
| deathwish | यहां क्या-क्या मिलता है? | 6/10 | Decent suggestions | [3/6] "कौनसा कॉफी सबसे ज़्यादा बिकता है?" (possibly_generic) | [4/6] "क्या यहां  |
| tentree | I'm new here, what kind of t-s | 10/10 | Excellent suggestions | [5/6] "What's the most affordable option?" (generically_useful, user_perspective |

## Missing Info Detection
| Bot | Query | Detected? | Score | Notes |
|-----|-------|-----------|-------|-------|
| ramraj | What are the exact fabric materials and  | ✅ Yes | 7/10 | |
| ramraj | Can you show me your product warranty ce | ✅ Yes | 7/10 | |
| kriyanta | What are the exact fabric materials and  | ✅ Yes | 7/10 | |
| kriyanta | Can you show me your product warranty ce | ❌ No (fabricated) | 2/10 | |
| zevaramaze | What are the exact fabric materials and  | ✅ Yes | 7/10 | |
| zevaramaze | Can you show me your product warranty ce | ✅ Yes | 7/10 | |
| beardbrand | What are the exact fabric materials and  | ✅ Yes | 7/10 | |
| beardbrand | Can you show me your product warranty ce | ❌ No (fabricated) | 2/10 | |
| deathwish | What are the exact fabric materials and  | ✅ Yes | 7/10 | |
| deathwish | Can you show me your product warranty ce | ❌ No (fabricated) | 2/10 | |
| tentree | What are the exact fabric materials and  | ✅ Yes | 7/10 | |
| tentree | Can you show me your product warranty ce | ✅ Yes | 7/10 | |

## Product Data Quality Issues

**kriyanta** — Query: "I'm looking for a premium portfolio"
- Gifting: missing_image

**beardbrand** — Query: "Show me your best beard oil"
- 10 Mistakes That Might Be Destroying Your Beard: missing_image
- 2014: missing_image
- Beardbrand Launches Silver Line Travel Size Beard Wash & Softener: missing_image
- Brandon Burk: missing_image

**beardbrand** — Query: "What beard balm do you have?"
- 5 Things a Woman Wants From Her Beardsman: missing_image
- 10 Mistakes That Might Be Destroying Your Beard: missing_image
- 4 Things Beardsmen Can Get Away With That Others Can’t: missing_image
- 2014: missing_image

**beardbrand** — Query: "I'm looking for a premium grooming kit"
- 5 Things a Woman Wants From Her Beardsman: missing_image
- 10 Mistakes That Might Be Destroying Your Beard: missing_image
- 2014: missing_image

## Poorly Performing Queries (Score < 5)

These query TYPES consistently fail and need attention:


### `irrelevant` — 5 failure(s)
- **kriyanta** (en): "Can you write me a Python script to sort a list?" → Score: 2/10
  - Issues: Bot answered irrelevant question instead of rejecting
  - Response: "That's a bit off-topic for me, I'm afraid. I'm here to help you with kriyanta's products and service..."
- **zevaramaze** (en): "Can you write me a Python script to sort a list?" → Score: 2/10
  - Issues: Bot answered irrelevant question instead of rejecting
  - Response: "That's a bit off-topic for Zevaramaze, but I can give you a quick answer. However, I'd rather help y..."
- **deathwish** (en): "Can you write me a Python script to sort a list?" → Score: 2/10
  - Issues: Bot answered irrelevant question instead of rejecting
  - Response: "That's not really what we do here - we're all about **Death Wish Coffee**. Let's get back to coffee,..."
- **tentree** (en): "Can you write me a Python script to sort a list?" → Score: 2/10
  - Issues: Bot answered irrelevant question instead of rejecting
  - Response: "That's not really what we do here at Crawl-Tentree - we're all about sustainable clothing and appare..."
- **tentree** (gu): "ભારતના વડાપ્રધાન કોણ છે?" → Score: 2/10
  - Issues: Bot answered irrelevant question instead of rejecting
  - Response: "હાય, આ પ્રશ્ન થોડો અલગ છે. અમે Crawl-Tentree પર કપડાં અને ફેશન વિશે વાત કરીએ છીએ. ભારતના વડાપ્રધાન વ..."

### `missing_info` — 3 failure(s)
- **kriyanta** (en): "Can you show me your product warranty certificates" → Score: 2/10
  - Issues: Bot fabricated info instead of flagging missing data
  - Response: "I'm not able to find any information on product warranty certificates for kriyanta's products. It se..."
- **beardbrand** (en): "Can you show me your product warranty certificates" → Score: 2/10
  - Issues: Bot fabricated info instead of flagging missing data
  - Response: "I'm not finding any information on product warranty certificates in our context ..."
- **deathwish** (en): "Can you show me your product warranty certificates" → Score: 2/10
  - Issues: Bot fabricated info instead of flagging missing data
  - Response: "Oh nice, here's what we've got!  ..."

### `non_product` — 2 failure(s)
- **zevaramaze** (hi): "रिटर्न पॉलिसी क्या है?" → Score: 4/10
  - Issues: No policy information found
  - Response: "रिटर्न पॉलिसी के बारे में बता दूँ! अगर आपको प्रोडक्ट पसंद नहीं आया, तो आप **30 दिन** के अंदर रिटर्न ..."
- **deathwish** (hi): "रिटर्न पॉलिसी क्या है?" → Score: 4/10
  - Issues: No policy information found
  - Response: "सॉरी, रिटर्न पॉलिसी की जानकारी यहाँ उपलब्ध नहीं है — Crawl-Death Wish Coffee को सीधे कॉन्टैक्ट करो  ..."

### `about_brand` — 2 failure(s)
- **zevaramaze** (en): "Tell me about zevaramaze and what you sell" → Score: 0/10
  - Issues: ERROR: ('Connection aborted.', ConnectionResetError(10054, 'An existing connection was forcibly closed by t
- **tentree** (en): "Tell me about tentree and what you sell" → Score: 0/10
  - Issues: ERROR: ('Connection aborted.', ConnectionResetError(10054, 'An existing connection was forcibly closed by t

### `unsupported_lang` — 2 failure(s)
- **deathwish** (ja): "こんにちは、人気商品を教えてください" → Score: 1/10
  - Issues: CRITICAL: No language rejection — responded in unsupported language
  - Response: "अरे, यहाँ हम **कॉफ़ी** के बारे में बात करते हैं! यह प्रश्न हमारे विषय से बाहर है ..."
- **tentree** (fr): "Bonjour, montrez-moi vos produits les plus populai" → Score: 1/10
  - Issues: CRITICAL: No language rejection — responded in unsupported language
  - Response: "Take a look at these beauties! We've got a great selection of products that are perfect for anyone l..."

### `product_browse` — 1 failure(s)
- **kriyanta** (gu): "તમારી પાસે કયા services છે?" → Score: 4/10
  - Issues: No products returned or mentioned
  - Response: "અરે, ઘણા સરસ services છે! જુઓ, ક્રિયાંતા પાસે શું છે: * **ફ્રી ઇન્ટીરિયર ડેકોરેશન કન્સલ્ટેશન**: અમાર..."

### `price_query` — 1 failure(s)
- **zevaramaze** (hi): "500 रुपये से कम के bracelets बताओ" → Score: 4/10
  - Issues: No price info in response
  - Response: "अरे, 500 रुपये से कम के बहुत सारे अच्छे bracelets हैं! Zevaramaze के पास **सिल्क ब्रेसलेट** 350 रुपय..."

### `greeting` — 1 failure(s)
- **beardbrand** (en): "Hi there! What can you help me with?" → Score: 0/10
  - Issues: ERROR: ('Connection aborted.', ConnectionResetError(10054, 'An existing connection was forcibly closed by t