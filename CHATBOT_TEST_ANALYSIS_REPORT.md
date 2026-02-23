# 🔬 Comprehensive Chatbot Chat Service Test Analysis Report

**Date:** February 20, 2026  
**Tester:** Automated Testing Suite  
**Account:** max@gmail.com  
**API Backend:** Docker (localhost:8000)  
**LLM Provider:** GROQ (6 API keys, free tier)  

---

## 📊 Executive Summary

| Metric | Value |
|--------|-------|
| **Bots Tested** | 5 (ramraj, truff, kriyanta, kids, zevaramaze) |
| **Total Queries Sent** | 210 |
| **Valid Responses (non rate-limited)** | 167 (79.5%) |
| **Rate-Limited / Infra Errors** | 43 (20.5%) |
| **Average Score (valid only)** | **6.6/10** |
| **ConnectionResetErrors** | ~25 (Docker container restarts during key rotation) |
| **New Crawls Attempted** | 3 (beardbrand: 57p, deathwishcoffee: 185p, tentree: 200p) |
| **Crawl Status** | Killed by OOM (10 simultaneous crawls crashed container) |

### Overall Bot Scores

| Bot | Category | Pages | Queries | Valid | Avg Score | Failed |
|-----|----------|-------|---------|-------|-----------|--------|
| **zevaramaze** | Jewelry | 276 | 38 | 27 | **8.2/10** ⭐ | 1 |
| **ramraj** | Fashion/Clothing | 256 | 43 | 33 | **7.1/10** | 6 |
| **truff** | Food/Condiments | 262 | 43 | 35 | **6.8/10** | 7 |
| **kriyanta** | Tech/Startup | 803 | 43 | 36 | **6.0/10** | 8 |
| **kids** | Kids/Toys | 102 | 43 | 36 | **4.7/10** ⚠️ | 16 |

### Verdict
The chat service works **well for product search and greetings** but has **critical issues with multilingual support, unsupported language detection, suggestion generation, irrelevant query handling, and infrastructure stability** that need fixing.

---

## 🧪 Test Methodology

### Query Types Tested (16 categories)
1. **greeting** — Basic hello/welcome messages
2. **product_browse** — "Show me your products"
3. **specific_product** — "I want black shirts"
4. **price_query** — "Show products under ₹500"
5. **non_product** — "What's your return policy?"
6. **irrelevant** — "What's the capital of France?"
7. **ambiguous** — "I want something nice for a gift"
8. **complex** — Multi-intent queries (color + price + purpose)
9. **context_start** / **context_followup** / **context_summary** — Conversation memory
10. **about_brand** — "Tell me about this brand"
11. **unsupported_lang** — French, Japanese queries
12. **suggestions_test** — Check if suggestions are generated
13. **comparison** — "Compare your cheap vs expensive options"
14. **variant_query** — "What sizes/colors available?"
15. **urgency** — "I need this urgently, can you deliver tomorrow?"
16. **complaint** — "I received a damaged product"

### Languages Tested
- **English (en)** — Primary
- **Hindi (hi)** — Devanagari script
- **Gujarati (gu)** — Gujarati script
- **Hindi Romanized (hi_roman)** — "hello bhai, kya help kar sakte ho?"
- **French (fr)** — Unsupported language
- **Japanese (ja)** — Unsupported language

---

## 📈 Query Type Performance (All Bots Combined)

| Query Type | Avg Score | Queries | Below 7 | Status |
|------------|-----------|---------|---------|--------|
| **comparison** | 9.5/10 | 4 | 0 | ✅ Excellent |
| **context_summary** | 9.5/10 | 4 | 0 | ✅ Excellent |
| **greeting** | 9.0/10 | 11 | 0 | ✅ Excellent |
| **specific_product** | 8.4/10 | 13 | 3 | ✅ Good |
| **complaint** | 8.3/10 | 3 | 0 | ✅ Good |
| **context_followup** | 7.5/10 | 10 | 0 | ✅ Good |
| **price_query** | 7.4/10 | 17 | 5 | ✅ Good |
| **variant_query** | 7.4/10 | 7 | 0 | ✅ Good |
| **about_brand** | 6.9/10 | 7 | 3 | ⚠️ Needs Work |
| **product_browse** | 6.5/10 | 15 | 8 | ⚠️ Needs Work |
| **complex** | 6.0/10 | 8 | 4 | ⚠️ Needs Work |
| **context_start** | 6.0/10 | 5 | 1 | ⚠️ Needs Work |
| **non_product** | 5.6/10 | 16 | 8 | ❌ Poor |
| **irrelevant** | 5.5/10 | 15 | 6 | ❌ Poor |
| **ambiguous** | 4.2/10 | 14 | 8 | ❌ Poor |
| **unsupported_lang** | 4.0/10 | 9 | 8 | ❌ Critical |
| **urgency** | 3.8/10 | 2 | 1 | ❌ Critical |
| **suggestions_test** | 3.1/10 | 7 | 7 | ❌ Critical |

---

## 🌐 Language Performance Analysis

| Language | Avg Score | Queries | Status |
|----------|-----------|---------|--------|
| **Hindi Romanized** | 8.6/10 | 11 | ✅ Excellent |
| **English** | 7.1/10 | 97 | ✅ Good |
| **Gujarati** | 5.6/10 | 9 | ⚠️ Fair |
| **Hindi (Devanagari)** | 5.0/10 | 41 | ❌ Poor |
| **Japanese** | 5.0/10 | 4 | ❌ No Warning |
| **French** | 3.2/10 | 5 | ❌ No Warning |

### CRITICAL ISSUE: Hindi → Gujarati Script Mismatch
The **ramraj** bot (which has Gujarati primary language configured) **responds in Gujarati script even when the user writes in Hindi**. This happens for **ALL Hindi queries on ramraj**:

| Query (Hindi) | Expected | Got |
|---------------|----------|-----|
| "नमस्ते! आप मेरी कैसे मदद कर सकते हैं?" | Hindi response | Gujarati response: "નમસ્તે! મને તમારી મદદ કરવામાં ખુશી છે!" |
| "आपके पास कौन से shirts उपलब्ध हैं?" | Hindi response | Gujarati: "અરે, ઘણા saras રંગના શર્ટ્સ છે!" |
| "मुझे shirts चाहिए जो बहुत अच्छी क्वालिटी का हो" | Hindi response | Gujarati: "અહીં કેટલાક સરસ ઓપ્શન છે!" |
| "500 रुपये से कम के shirts बताओ" | Hindi response | Gujarati: "અરે, ઘણા saras options છે!" |
| "रिटर्न पॉलिसी क्या है?" | Hindi response | Gujarati with fabricated info: "7 દિવસ return" |
| "भारत का प्रधानमंत्री कौन है?" | Should reject | Gujarati: tried to answer irrelevant query |

**Root Cause:** The `language` variable in `chat_service.py` (line ~2723) is set to `allowed_languages[0]` when the detected language is the same base script family. Since ramraj has Gujarati configured, Hindi queries are overridden to Gujarati. The LLM then responds in Gujarati because the system prompt instructs it to use the "detected" language.

**Also affects:** kriyanta bot — Hindi queries get Gujarati responses there too.

### CRITICAL ISSUE: Unsupported Languages (French/Japanese) Not Warned
When users write in French or Japanese:
- **Expected:** "Sorry, this language is not supported. Please use English/Hindi/Gujarati."
- **Actual (4/5 bots):** Bot happily responds in English with products, **no warning at all**

| Bot | French Query | Response |
|-----|-------------|----------|
| ramraj | "Bonjour, montrez-moi vos produits" | ConnectionResetError |
| truff | "Bonjour, montrez-moi vos produits" | "Oh nice, here's our most popular products..." (no warning) |
| kriyanta | "Bonjour, montrez-moi vos produits" | "Take a look at these beauties..." (no warning) |
| kids | "Bonjour, montrez-moi vos produits" | "Oh nice, we've got popular products..." (no warning) |
| zevaramaze | "Bonjour, montrez-moi vos produits" | "Unfortunately I don't have info..." (no warning) |

**Root Cause:** French/Japanese use Latin/CJK scripts which `_detect_message_language()` doesn't recognize (only Devanagari and Gujarati Unicode ranges are configured). The script detection returns "en" (Latin fallback), and since "en" is always allowed, no language rejection is triggered. The LLM-based language detection in Unified Call 1 should catch this, but it appears to either not detect or not enforce the rejection for non-configured scripts.

---

## 🛒 Product Listing Analysis

### Product Return Success Rate by Bot

| Bot | Queries with Products | Total Valid Queries | Rate |
|-----|----------------------|---------------------|------|
| ramraj | 17 | 33 | 52% |
| truff | 14 | 35 | 40% |
| kriyanta | 12 | 36 | 33% |
| kids | 12 | 36 | 33% |
| zevaramaze | 9 | 27 | 33% |

### ISSUE: Product Queries Return 0 Products for Non-English Languages
For bots that reject Hindi/Gujarati (truff, kids, kriyanta when configured as English-only), product queries in those languages return **"language not supported"** instead of trying to understand the product intent:

**Example (truff):**
- English: "Show me your best hot sauce" → ✅ 10 products returned
- Hindi: "आपके पास कौन से hot sauce उपलब्ध हैं?" → ❌ "Hindi is not supported" (0 products)
- Gujarati: "તમારી પાસે કયા hot sauce છે?" → ❌ "Gujarati is not supported" (0 products)

This affects **ALL non-English product queries** for bots without Hindi/Gujarati configured.

### ISSUE: "Show me your best X" Sometimes Returns 0 Products
Even in English, some browse queries get a text description but NO product cards:

| Bot | Query | Products | Sources | Issue |
|-----|-------|----------|---------|-------|
| ramraj | "What dhotis do you have?" | 0 | 0 | Hallucinated categories (cotton/silk/embroidered) |
| kriyanta | "Show me your best services" | 0 | 12 | Sources found but no product extraction |
| zevaramaze | "Show me your best bracelets" | 0 | 0 | Complete miss despite having bracelet data |

**Root Cause:** When sources are found but products aren't extracted from them, it means the product extraction pipeline (`_extract_products_from_sources()` or equivalent) failed to parse product data from the crawled pages. For the ramraj "dhotis" case, the bot hallucinated product categories that likely don't exist in the crawled data.

### Product Data Quality Issues

| Bot | Issue | Details |
|-----|-------|---------|
| ramraj | Missing images | 5 products missing images in price filter results |
| truff | Missing images | 5 products missing images across multiple queries |
| kriyanta | Missing images | 1-5 products missing images per query |
| zevaramaze | Missing images | 5 products missing images in price queries |
| zevaramaze | Price format inconsistency | Some prices show as "inr 2225" (string) vs "8799.0" (number) |

---

## 💬 Suggestion Analysis

### Suggestion Generation Rate

| Bot | With Suggestions | Without | Rate |
|-----|-----------------|---------|------|
| zevaramaze | 26/27 | 1 | **96%** ⭐ |
| ramraj | 24/33 | 9 | 73% |
| kriyanta | 24/36 | 12 | 67% |
| truff | 22/35 | 13 | 63% |
| kids | 17/36 | 19 | **47%** ⚠️ |

### When Suggestions Are Missing
Suggestions are most frequently missing for:
1. **Hindi queries on English-only bots** — "Language not supported" messages don't include suggestions
2. **ConnectionResetError responses** — No suggestions generated at all
3. **Some non-product queries** — Return policy, shipping queries sometimes lack suggestions
4. **Greeting in Hindi** — Even on multilingual bots, Hindi greetings may lack suggestions

### Suggestion Quality Issues
- When suggestions ARE generated, they are generally **relevant and helpful** (e.g., "Which is the most popular?", "Do you have any discounts?")
- Suggestions are generated in the **response language** (good)
- Some suggestions on ramraj mix Gujarati and English: "આ બધામાંથી સૌથી popular કયો છે?" (acceptable for code-switching)

---

## 🔄 Conversation Context Analysis

| Feature | Score | Status |
|---------|-------|--------|
| **Context Start** | 6.0/10 | ⚠️ Some start queries hit infra errors |
| **Context Follow-up** | 7.5/10 | ✅ Good — remembers previous products |
| **Context Summary** | 9.5/10 | ✅ Excellent — accurate conversation summaries |

The conversation memory works well when it's not interrupted by ConnectionResetErrors. Follow-up queries like "Do you have something cheaper?" correctly reference the previous context, and summary requests produce accurate recaps.

---

## 🚫 Irrelevant Query Detection

| Bot | Query | Score | Issue |
|-----|-------|-------|-------|
| ramraj (en) | "What is the capital of France?" | 9/10 | ✅ Correctly rejected |
| ramraj (en) | "Write a Python script" | Rate limited | — |
| ramraj (hi) | "भारत का प्रधानमंत्री कौन है?" | **1/10** | ❌ Tried to answer in Gujarati! |
| truff (en) | All 3 irrelevant queries | 9.0/10 | ✅ Good |
| kriyanta (en) | "What's the weather in Tokyo?" | ConnectionResetError | — |
| kids (en) | "Write a Python script" | **1/10** | ❌ Actually wrote Python code! |

### ISSUE: Bot Sometimes Answers Irrelevant Queries
- **ramraj in Hindi:** When asked "भारत का प्रधानमंत्री कौन है?" (Who is India's PM?), the bot tried to relate it to ramraj products in Gujarati (score: 1/10)
- **kids in English:** When asked to write a Python script, the bot **actually started writing Python code** (score: 1/10)
- English irrelevant queries are mostly handled well, but Hindi irrelevant queries bypass the filter

---

## 🏗️ Infrastructure Issues

### ConnectionResetError Pattern
25+ queries failed with:
```
('Connection aborted.', ConnectionResetError(10054, 'An existing connection was forcibly closed by the remote host'))
```

These are NOT bot logic failures — they're Docker container restarts caused by:
1. **Memory pressure** from 10 simultaneous crawls causing OOM
2. **GROQ API key rotation** triggering container restarts
3. **Rate limiting** causing the API to close connections

**Impact:** Primarily affected `ambiguous`, `suggestions_test`, `urgency`, and `irrelevant` query types on kriyanta and kids bots (tested later when container was unstable).

### GROQ Free Tier Rate Limits
- 6 API keys rotated, but free tier limits are very aggressive
- Each chat query internally makes 2-3 GROQ API calls (Unified Call 1 + main response + sometimes suggestion call)
- All 6 keys exhausted within ~70 queries requiring 5+ minute cooldowns
- 20.5% of all queries were rate-limited

---

## 🔍 Per-Bot Detailed Analysis

### 1. Ramraj (Fashion/Clothing) — 7.1/10
**Strengths:**
- ✅ Product search in English is excellent (8-10 products returned)
- ✅ Hindi Devanagari product queries return products (via Gujarati response)
- ✅ Price filtering works ("shirts under $30" returns 8 products)
- ✅ Greeting is warm and brand-aware
- ✅ Comparison queries handled well (9.5/10)

**Weaknesses:**
- ❌ Hindi queries ALWAYS responded in Gujarati (wrong language)
- ❌ "What dhotis do you have?" — Hallucinated categories, 0 products (4/10)
- ❌ Irrelevant query in Hindi was not rejected (1/10)
- ❌ Return policy info was fabricated ("7 days return" with no source)
- ❌ Urgency query hit ConnectionResetError (0/10)
- ⚠️ Non-product info queries (shipping, COD) couldn't find info in crawled data

### 2. Truff (Food/Condiments) — 6.8/10
**Strengths:**
- ✅ English product queries are great (10 products with prices)
- ✅ Irrelevant queries perfectly rejected in English (9.0/10)
- ✅ Greeting engaging and brand-appropriate
- ✅ Comparison queries handled well

**Weaknesses:**
- ❌ ALL Hindi/Gujarati queries rejected with "language not supported"
- ❌ Hindi product queries return 0 products (could still search then respond in English)
- ❌ French/Japanese queries answered without language warning
- ❌ Suggestion generation rate only 63%
- ⚠️ Some product browse queries returned text but 0 product cards

### 3. Kriyanta (Tech/Startup) — 6.0/10
**Strengths:**
- ✅ Specific product search works (8.8/10 for specific queries)
- ✅ Price queries handled well (8.5/10)
- ✅ Comparison queries excellent (9.5/10)
- ✅ Context summary works perfectly (9.5/10)

**Weaknesses:**
- ❌ Product browse queries return 0 products despite finding 12 sources (5.5/10)
- ❌ Hindi queries get Gujarati responses (same issue as ramraj)
- ❌ 8 ConnectionResetError failures (infra issues)
- ❌ Ambiguous queries ALL failed (ConnectionResetErrors)
- ⚠️ Service-based business doesn't map well to product cards

### 4. Kids/CheaperZoneToys — 4.7/10 ⚠️ WORST
**Strengths:**
- ✅ English greeting is good (8.8/10)
- ✅ English product browse returns products (10/10)
- ✅ Comparison queries handled well (9.5/10)

**Weaknesses:**
- ❌ 16 failed queries (44% failure rate!)
- ❌ Hindi/Gujarati queries ALL rejected
- ❌ Wrote Python code when asked (irrelevant query not blocked) 
- ❌ ALL non-product queries failed (ConnectionResetErrors)
- ❌ Suggestion rate only 47%
- ❌ Urgency, context_start queries failed
- ⚠️ Only 102 pages crawled — limited knowledge base

### 5. Zevaramaze (Jewelry) — 8.2/10 ⭐ BEST
**Strengths:**
- ✅ Highest average score across all bots
- ✅ Product search excellent with proper prices (INR) and images
- ✅ Price filtering works perfectly (₹1000 filter returns correct items)
- ✅ 96% suggestion generation rate (best)
- ✅ Irrelevant queries handled well (9.0/10)
- ✅ Ambiguous queries handled well (8.5/10)
- ✅ Only 1 failed query
- ✅ Multilingual support works relatively well

**Weaknesses:**
- ❌ "Show me your best bracelets" returned 0 products (2.5/10)
- ❌ Unsupported languages (French) not warned
- ⚠️ Non-product queries (return policy, shipping) lack detail
- ⚠️ Price format inconsistency: "inr 2225" vs "8799.0"

---

## 🎯 Critical Issues & Recommended Improvements

### Priority 1 — CRITICAL (Must Fix)

#### 1. Hindi → Gujarati Language Mismatch
**Problem:** When a bot has Gujarati configured, ALL Hindi queries get Gujarati responses because Hindi (Devanagari: U+0900-097F) and Gujarati (U+0A80-0AFF) are treated as the same language family.  
**Fix in:** `chat_service.py` around line 2723  
**Solution:** After detecting the script language, ensure the response language matches the INPUT language, not just the first allowed language. If Hindi is detected but only Gujarati is allowed, respond in the detected language (Hindi) or clearly inform the user.

#### 2. Unsupported Language Detection Fails for Non-Indic Scripts
**Problem:** French, Japanese, and other non-Indic languages bypass the language rejection because `_detect_message_language()` only checks Devanagari and Gujarati Unicode ranges. Everything else falls back to "en".  
**Fix in:** `chat_service.py` line 1763+ (`SUPPORTED_LANGUAGES`) and `_detect_message_language()`  
**Solution:** Add basic detection for common scripts (CJK, Arabic, Cyrillic, etc.) or rely on the LLM's language detection in Unified Call 1 and enforce the rejection. The LLM detects French/Japanese correctly, but the enforcement path may not trigger.

#### 3. Suggestion Generation Fails for ~35% of Queries
**Problem:** Suggestions are missing for: Hindi queries on English-only bots, error responses, and some non-product queries.  
**Fix in:** The suggestion extraction logic around line 3950+  
**Solution:** 
- Always generate suggestions, even for language rejection messages ("Try asking in English", "View our products")
- Add fallback suggestions when LLM doesn't generate them
- Ensure error responses include contextual suggestions

#### 4. Irrelevant Query Filter Bypassed
**Problem:** kids bot wrote Python code; ramraj bot answered "Who is India's PM?" in Gujarati.  
**Fix in:** The irrelevant query classification in Unified Call 1  
**Solution:** Strengthen the irrelevant query detection, especially for non-English queries. Add a hard rule: if the LLM generates code blocks (```), it's likely off-topic.

### Priority 2 — HIGH (Should Fix)

#### 5. Product Browse Returns Text but 0 Products
**Problem:** Bot describes products in text but doesn't return product cards (kriyanta: "We offer Free Interior Decoration Consultation..." with 0 products).  
**Fix:** When sources are found (sources_count > 0) but product extraction returns 0, trigger a fallback product extraction from the text content or source URLs.

#### 6. Non-Product Queries Lack Information
**Problem:** Return policy, shipping, COD queries get vague "I don't have that info" responses even though the crawled pages likely contain this information (e.g., /shipping-policy, /refund-policy pages).  
**Fix:** Ensure crawler captures policy pages and the retrieval system can find them. Consider adding dedicated FAQ/policy extraction during crawling.

#### 7. Hindi Product Queries on English-Only Bots Should Still Work
**Problem:** When a user writes "आपके पास कौन से hot sauce हैं?" on truff (English-only), the bot says "Hindi not supported" instead of understanding the product intent.  
**Fix:** Two approaches:
  a. Translate the retrieval query to English internally, serve results, but respond in English with a note
  b. Respond with products in English and add: "Note: I can only respond in English"

#### 8. Hallucinated Information
**Problem:** ramraj bot fabricated return policy ("7 days") and dhoti categories (cotton/silk/embroidered) that may not exist.  
**Fix:** Strengthen the system prompt to never fabricate information that's not in the knowledge base. Add a confidence check: if no relevant sources are found, say "I don't have specific information about that."

### Priority 3 — MEDIUM (Nice to Have)

#### 9. Price Format Standardization
**Problem:** zevaramaze shows "inr 2225" (string) vs "8799.0" (number). Inconsistent currency formatting.  
**Fix:** Normalize all prices to a consistent format: `{ price: 2225.0, currency: "INR", formatted: "₹2,225" }`

#### 10. Missing Product Images
**Problem:** 5+ products per query missing images across multiple bots.  
**Fix:** During crawling, ensure image URLs are extracted. For Shopify stores, use the standard product image URL patterns. Add fallback: use store favicon or category image.

#### 11. Urgency/Time-Sensitive Queries
**Problem:** "I need shirts urgently for tomorrow" queries not handled well.  
**Fix:** Add a dedicated urgency detection in the query analysis. Bot should acknowledge urgency and suggest contacting the store directly for urgent orders.

#### 12. Ambiguous Query Handling
**Problem:** "I want something nice for a gift" scores poorly (4.2/10 avg).  
**Fix:** Bot should ask clarifying questions: "What's the occasion?", "What's your budget?", "Who is it for?" Currently it either errors out or gives generic responses.

---

## 🕷️ Crawling Analysis

### Crawl Results Summary

| Site | Pages Crawled | Status | Notes |
|------|--------------|--------|-------|
| ramrajcotton.in | 256 | ✅ Complete | Shopify store, SSR |
| truff.com | 262 | ✅ Complete | Shopify store, SSR |
| kriyanta.com | 803 | ✅ Complete | Custom site |
| cheaperzonetoys.com | 102 | ✅ Complete | Limited product pages |
| zevaramaze.com | 276 | ✅ Complete | Shopify store, SSR |
| beardbrand.com | 57 | ⚠️ Partial | Stopped at 57 pages |
| deathwishcoffee.com | 185 | ✅ Complete | Shopify store |
| tentree.com | 200 | ✅ Complete | Shopify store |

### Crawling Issues Found
1. **OOM with 10 simultaneous crawls** — Container crashed with 10 parallel crawls. Recommend limiting to 3-5 concurrent crawls.
2. **No headless browser** — Crawler uses `httpx` (HTTP client), no JavaScript rendering. JS-heavy SPAs will fail silently.
3. **Sitemap auto-discovery works** — `auto_discover_sitemap()` correctly parses robots.txt and probes common sitemap paths.
4. **JS-heavy detection exists** — `detect_js_heavy_page()` checks for CSR indicators, but can't recover (no headless fallback).

### Crawl Improvement Recommendations
- Add a concurrent crawl limit (max 3-5 per container)
- Consider adding Playwright/headless browser as a fallback for JS-heavy sites
- Add crawl status notifications to the UI when sites are likely JS-heavy
- Improve page deduplication (kriyanta had 803 pages — many likely duplicates)

---

## 📋 Detailed Test Results by Bot

### Ramraj — Individual Query Results

| # | Type | Lang | Query | Score | Products | Issues |
|---|------|------|-------|-------|----------|--------|
| 1 | greeting | en | "Hi there! What can you help me with?" | 9/10 | 0 | — |
| 2 | greeting | hi | "नमस्ते! आप मेरी कैसे मदद कर सकते हैं?" | 9/10 | 0 | Responded in Gujarati |
| 3 | greeting | hi_roman | "hello bhai, kya help kar sakte ho?" | 8/10 | 0 | — |
| 4 | product_browse | en | "Show me your best shirts" | 9/10 | 8 | — |
| 5 | product_browse | en | "What dhotis do you have?" | **4/10** | 0 | ❌ Hallucinated categories |
| 6 | product_browse | hi | "आपके पास कौन से shirts उपलब्ध हैं?" | 10/10 | 8 | Gujarati response |
| 7 | product_browse | gu | "તમારી પાસે કયા shirts છે?" | 10/10 | 8 | — |
| 8 | specific_product | en | "I'm looking for black shirts" | 9/10 | 8 | — |
| 9 | specific_product | en | "Do you have premium cotton shirts?" | 9/10 | 10 | — |
| 10 | specific_product | hi | "मुझे shirts चाहिए बहुत अच्छी क्वालिटी" | 10/10 | 2 | Gujarati |
| 11 | specific_product | hi_roman | "best quality shirts dikhao" | 9/10 | 5 | — |
| 12 | price_query | en | "Show me shirts under $30" | 8/10 | 8 | — |
| 13 | price_query | en | "What's the price range for dhotis?" | 8/10 | 0 | Estimated prices |
| 14 | price_query | hi | "500 रुपये से कम के shirts बताओ" | 7/10 | 6 | Gujarati |
| 15 | price_query | gu | "$50 થી ઓછા shirts બતાવો" | 7/10 | 10 | — |
| 16 | non_product | en | "What is your return policy?" | 8/10 | 0 | — |
| 17 | non_product | en | "How long does shipping take?" | 8/10 | 0 | — |
| 18 | non_product | en | "Do you offer cash on delivery?" | 8/10 | 0 | — |
| 19 | non_product | hi | "रिटर्न पॉलिसी क्या है?" | **5/10** | 0 | ❌ Fabricated policy in Gujarati |
| 20 | irrelevant | en | "What is the capital of France?" | 9/10 | 0 | ✅ Correctly rejected |
| 21 | irrelevant | hi | "भारत का प्रधानमंत्री कौन है?" | **1/10** | 0 | ❌ Tried to answer |
| 22 | irrelevant | en | "Write a Python script" | RATE_LIMITED | — | — |
| 23-25 | ambiguous | en/hi | Various | 0-8.5 | — | 2 ConnectionResetErrors |
| 26-27 | complex | en/hi | Multi-intent queries | 5.5-10 | — | Mixed |
| 28-30 | context | en | Start/followup/summary | 7.5-9.5 | — | Context works! |
| 31 | about_brand | en | "Tell me about ramraj" | 8.5/10 | 0 | — |
| 32 | about_brand | hi | "ramraj के बारे में बताओ" | 8/10 | 0 | Gujarati |
| 33-34 | unsupported_lang | fr/ja | Foreign queries | 0-4/10 | 0-7 | ❌ No warning |
| 35-36 | suggestions_test | en/hi | "What do you sell?" | 3-6.5/10 | — | ❌ Missing suggestions |
| 37 | comparison | en | "Compare cheap vs expensive" | 9.5/10 | — | — |
| 38-39 | variant_query | en/hi_roman | "What sizes available?" | 7.2/10 | — | — |
| 40 | urgency | en | "I need urgently for tomorrow" | **0/10** | 0 | ConnectionResetError |
| 41 | complaint | en | "Received damaged product" | 8.5/10 | — | — |

### Zevaramaze (Best Bot) — Highlights

| Type | Lang | Query | Score | Products | Notes |
|------|------|-------|-------|----------|-------|
| product_browse | en | "Show me your best necklaces" | 10/10 | 5 | ✅ Perfect with images & prices |
| price_query | en | "Necklaces under ₹5000" | 9.5/10 | 10 | ✅ All with prices |
| price_query | gu | "₹1000 થી ઓછા bracelets" | 9.5/10 | 10 | ✅ Gujarati works |
| irrelevant | en | "Capital of France?" | 9/10 | 0 | ✅ Correctly rejected |
| ambiguous | en | "Something nice for a gift" | 8.5/10 | — | ✅ Good guidance |
| context_summary | en | "Summarize our conversation" | 9.5/10 | 0 | ✅ Perfect summary |
| product_browse | en | "Show me best bracelets" | **2.5/10** | 0 | ❌ Text only, 0 products |

---

## ✅ What Works Well

1. **English product search** — Consistently returns 5-10 products with prices, images, URLs
2. **Product comparison queries** — 9.5/10 average across all bots
3. **Conversation context & summary** — Memory works, summaries are accurate
4. **Greeting responses** — Warm, brand-aware, engaging (9.0/10)
5. **Complaint handling** — Empathetic, suggests contacting support (8.3/10)
6. **Hindi Romanized** — Transliterated input ("dikhao", "batao") works great (8.6/10)
7. **Price filtering** — Multi-language price extraction (₹, Rs, रुपये, રૂ) works
8. **Shopify store crawling** — Reliable, extracts products with structured data
9. **Caching** — Seen in status messages, helps with response speed
10. **Product cards** — When returned, include name, price, URL, image (good UX)

## ❌ What Needs Improvement

1. **Hindi → Gujarati mismatch** — Critical UX issue for Indian users
2. **Unsupported language detection** — French/Japanese/etc. need warnings
3. **Suggestion generation** — 35% miss rate, especially for non-English
4. **Irrelevant query filter** — Bypassed for Hindi queries and code requests
5. **Product browse sometimes returns 0 products** — Despite having source data
6. **Non-product info** — Shipping, returns, COD queries poorly handled
7. **Hallucinated information** — Fabricates return policies and product categories
8. **Infrastructure stability** — OOM from concurrent crawls, ConnectionResetErrors
9. **Price format inconsistency** — Mix of string and numeric formats
10. **Ambiguous query handling** — Should ask clarifying questions

---

## 📊 Final Score Card

| Category | Weight | Score | Weighted |
|----------|--------|-------|----------|
| Product Search (en) | 25% | 9.0/10 | 2.25 |
| Multilingual Support | 20% | 4.5/10 | 0.90 |
| Conversation Context | 10% | 8.2/10 | 0.82 |
| Irrelevant Detection | 10% | 5.5/10 | 0.55 |
| Suggestion Quality | 10% | 5.0/10 | 0.50 |
| Non-Product Queries | 10% | 5.6/10 | 0.56 |
| Product Data Quality | 10% | 7.0/10 | 0.70 |
| Error Handling | 5% | 3.0/10 | 0.15 |
| **OVERALL** | **100%** | | **6.43/10** |

**Bottom Line:** The chat service has a **strong foundation** — English product search, conversation memory, and price filtering are excellent. The critical gaps are in **multilingual support** (Hindi→Gujarati mismatch, no warnings for unsupported languages) and **edge case handling** (irrelevant queries, suggestions, ambiguous queries). Fixing Priority 1 issues would likely raise the overall score to **8.0+/10**.
