# Comprehensive Chatbot Test Report V2

**Date:** 2025-07-14  
**Total Queries:** 80 across 10 chatbots  
**Test Method:** SSE streaming via `POST /api/v1/chat/{chatbot_id}/message/stream` with `is_preview=true`

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Total queries | 80 |
| Success (HTTP 200) | 80/80 (100%) |
| Usable responses (not rate-limited) | **72/80 (90%)** |
| Rate-limited responses | **8/80 (10%)** |
| False deflections (scope gate errors) | **6/80 (7.5%)** |
| Avg response time | 9.7s |
| Irrelevant deflection accuracy | **10/10 (100%)** |
| Missing-info admission accuracy | **10/10 (100%)** |
| Hindi language accuracy | **7/7 (100%)** excl. rate-limited |
| Gujarati language accuracy | **3/3 (100%)** excl. rate-limited |

**Overall Quality Score: 82.5%** (66 fully correct out of 80)

---

## 1. Results by Query Type

### 1.1 Product Queries (15 queries)

| # | Bot | Query | Status | Content | Sources | Products | Time |
|---|-----|-------|--------|---------|---------|----------|------|
| 1 | zevaramaze | What silver rings do you have for men? | ✅ Good | 252 chars, named 5 rings | 12 | 10 | 27.2s |
| 9 | BigBasket | What ayurveda products are available? | ✅ Good | 191 chars, named 3 products | 12 | 2 | 16.9s |
| 17 | BoAt | What are the best boAt ANC earbuds? | ✅ Good | 521 chars, detailed | 12 | 0 | 14.7s |
| 19 | BoAt | Portable speakers under 8000 rupees? | ✅ Good | 355 chars | 12 | 0 | 13.0s |
| 20 | BoAt | What smartwatches did boAt launch? | ✅ Good | 436 chars, named 4 | 12 | 0 | 11.7s |
| 25 | Byju's | NCERT notes for UPSC prep? | ❌ **FALSE DEFLECT** | "outside my expertise" | 0 | 0 | 1.7s |
| 33 | Mamaearth | Baby care products? | ✅ Good | 119 chars | 12 | 3 | 18.3s |
| 35 | Mamaearth | Best shampoo for hair treatment? | ✅ Good | 153 chars | 12 | 1 | 10.8s |
| 36 | Mamaearth | Charcoal-based makeup products? | ✅ Good | 89 chars | 12 | 1 | 10.0s |
| 41 | Mokobara | Luggage sets available? | ✅ Good | 50 chars (short) | 12 | 1 | 10.5s |
| 49 | Nicobar | What kurta sets? | ✅ Good | 180 chars, named 3 sets | 12 | 10 | 10.9s |
| 57 | PlumGoodness | Dandruff control products? | ✅ Good | 483 chars, detailed | 12 | 0 | 10.8s |
| 63 | PlumGoodness | Tips for faster hair growth? | ❌ **FALSE DEFLECT** | "outside my expertise" | 0 | 0 | 1.7s |
| 65 | SlurrpFarm | When ready for solid foods? | ❌ **FALSE DEFLECT** | "outside my expertise" | 0 | 0 | 1.5s |
| 73 | TheManCompany | What grooming products? | ✅ Good | 499 chars, listed many | 12 | 0 | 11.1s |

**Score: 12/15 (80%)** — 3 false deflections

### 1.2 General Queries (10 queries)

| # | Bot | Query | Status | Content | Sources | Time |
|---|-----|-------|--------|---------|---------|------|
| 2 | zevaramaze | What kind of jewelry? | ✅ Good | 205 chars | 12 | 16.2s |
| 10 | BigBasket | What do they deliver? | ✅ Good | 545 chars, comprehensive | 12 | 20.5s |
| 18 | BoAt | What products do they make? | ✅ Good | 473 chars | 12 | 10.8s |
| 26 | Byju's | What courses do they offer? | ✅ Good | 952 chars, detailed | 12 | 9.5s |
| 34 | Mamaearth | Are products toxin-free? | ✅ Good | 1168 chars, very detailed | 16 | 11.5s |
| 42 | Mokobara | What is Mokobara known for? | ✅ Good | 356 chars | 12 | 10.2s |
| 50 | Nicobar | What kind of products? | ✅ Good | 227 chars | 12 | 11.0s |
| 58 | PlumGoodness | Vegan and cruelty-free? | ⚠️ **RATE LIMITED** | "too many requests" | 0 | 9.5s |
| 66 | SlurrpFarm | What kind of food? | ✅ Good | 365 chars | 12 | 9.1s |
| 74 | TheManCompany | What is TMC all about? | ✅ Good | 367 chars | 16 | 11.4s |

**Score: 9/10 (90%)** — 1 rate-limited

### 1.3 Hindi Queries (9 queries)

| # | Bot | Query | Status | Hindi Response? | Sources | Products | Time |
|---|-----|-------|--------|----------------|---------|----------|------|
| 11 | BigBasket | चॉकलेट गिफ्ट बॉक्स? | ✅ Good | ✅ Yes | 12 | 1 | 10.1s |
| 12 | BigBasket | प्रोटीन सप्लीमेंट्स? | ✅ Good | ✅ Yes | 12 | 1 | 10.6s |
| 27 | Byju's | UPSC तैयारी कैसे? | ✅ Good | ✅ Yes, detailed (480 chars) | 16 | 0 | 10.8s |
| 43 | Mokobara | बैकपैक मिलते हैं? | ✅ Good | ✅ Yes | 12 | 1 | 9.9s |
| 44 | Mokobara | ब्रीफकेस बिज़नेस ट्रैवल? | ✅ Good | ✅ Yes | 16 | 1 | 11.1s |
| 51 | Nicobar | साड़ी मिलती है? | ✅ Good | ✅ Yes | 12 | 10 | 9.8s |
| 67 | SlurrpFarm | तेल और फैट्स? | ⚠️ **RATE LIMITED** | ❌ English msg | 0 | 0 | 9.7s |
| 75 | TheManCompany | राखी गिफ्ट? | ⚠️ **RATE LIMITED** | ❌ English msg | 0 | 0 | 9.4s |
| 76 | TheManCompany | 2020 में क्या कहा? | ✅ Good | ✅ Yes | 12 | 0 | 10.3s |

**Score: 7/9 (78%)** — 2 rate-limited (language itself is 100% when not rate-limited)

### 1.4 Gujarati Queries (5 queries)

| # | Bot | Query | Status | Gujarati Response? | Sources | Products | Time |
|---|-----|-------|--------|-------------------|---------|----------|------|
| 3 | zevaramaze | મોઈસનાઈટ રિંગ્સ? | ✅ Good | ✅ Yes | 12 | 10 | 16.5s |
| 4 | zevaramaze | ગોલ્ડ જ્વેલરી? | ✅ Good | ✅ Yes | 12 | 10 | 15.2s |
| 28 | Byju's | પરીક્ષાઓની તૈયારી? | ✅ Good | ✅ Yes | 12 | 0 | 10.8s |
| 52 | Nicobar | ઘર માટે પ્રોડક્ટ્સ? | ⚠️ **RATE LIMITED** | ❌ English msg | 0 | 0 | 9.7s |
| 68 | SlurrpFarm | ડેકેરમાં જમવાની આદત? | ⚠️ **RATE LIMITED** | ❌ English msg | 0 | 0 | 10.1s |

**Score: 3/5 (60%)** — 2 rate-limited (language itself is 100% when not rate-limited)

### 1.5 Missing Info Queries (10 queries)

| # | Bot | Query | Status | Admitted? | Content | Time |
|---|-----|-------|--------|-----------|---------|------|
| 5 | zevaramaze | Return/exchange policy? | ✅ Good | ✅ Admitted + redirected | 315 chars | 10.0s |
| 13 | BigBasket | Deliver to US/Europe? | ✅ Good | ✅ Admitted + redirected | 203 chars | 13.8s |
| 21 | BoAt | International warranty? | ✅ Good | ✅ Admitted + partial info (12-month warranty mentioned) | 523 chars | 11.4s |
| 29 | Byju's | MBA/CAT courses? | ✅ Good | ✅ Admitted | 164 chars | 10.1s |
| 37 | Mamaearth | Ship to Canada? | ✅ Good | ✅ Admitted + redirected | 281 chars | 10.4s |
| 45 | Mokobara | Lifetime warranty? | ✅ Good | ✅ Admitted + mentioned 30-day trial | 528 chars | 10.4s |
| 53 | Nicobar | Physical store in Delhi? | ✅ Good | ✅ Admitted + redirected | 194 chars | 10.0s |
| 61 | PlumGoodness | Anti-aging for mature skin? | ⚠️ **RATE LIMITED** | "too many requests" | 86 chars | 9.9s |
| 69 | SlurrpFarm | Deliver outside India? | ✅ Good | ✅ Admitted + redirected | 123 chars | 8.7s |
| 77 | TheManCompany | Subscription box? | ⚠️ **RATE LIMITED** | "too many requests" | 86 chars | 9.8s |

**Score: 8/10 (80%)** — 2 rate-limited (admission logic is 100% when working)

### 1.6 Irrelevant Queries (10 queries)

| # | Bot | Query | Status | Deflected? | Time |
|---|-----|-------|--------|-----------|------|
| 6 | zevaramaze | Book a flight to Mumbai? | ✅ DEFLECTED | "outside my expertise" | 1.6s |
| 14 | BigBasket | Invest in stock market? | ✅ DEFLECTED | "I specialize in BigBasket" | 1.7s |
| 22 | BoAt | Laptop for programming? | ✅ DEFLECTED | "outside my expertise" | 1.6s |
| 30 | Byju's | Recipe for butter chicken? | ✅ DEFLECTED | "beyond what I can help" | 1.4s |
| 38 | Mamaearth | Find a dentist? | ✅ DEFLECTED | "outside my expertise" | 1.7s |
| 46 | Mokobara | Capital of France? | ✅ DEFLECTED | "outside my expertise" | 1.6s |
| 54 | Nicobar | How to cook biryani? | ✅ DEFLECTED | "beyond what I can help" | 1.4s |
| 62 | PlumGoodness | Explain quantum physics? | ✅ DEFLECTED | "outside my expertise" | 1.8s |
| 70 | SlurrpFarm | Best smartphone 2026? | ✅ DEFLECTED | "I specialize in SlurrpFarm" | 1.6s |
| 78 | TheManCompany | Fix leaking faucet? | ✅ DEFLECTED | "beyond what I can help" | 1.5s |

**Score: 10/10 (100%)** — Perfect! Fast responses (~1.6s avg), no unnecessary searches.

### 1.7 Comparison Queries (10 queries)

| # | Bot | Query | Status | Content | Sources | Time |
|---|-----|-------|--------|---------|---------|------|
| 7 | zevaramaze | Moissanite vs CZ rings? | ✅ Good | 394 chars | 16 | 10.9s |
| 15 | BigBasket | Medicine vs Ayurveda? | ✅ Good | 761 chars | 16 | 13.5s |
| 23 | BoAt | TWS vs neckband vs headphones ANC? | ✅ Excellent | 1111 chars, very detailed | 16 | 15.9s |
| 31 | Byju's | Classes vs Learning App? | ✅ Excellent | 906 chars, clear distinction | 16 | 9.9s |
| 39 | Mamaearth | Aqua Glow vs regular face wash? | ✅ Good | 196 chars | 16 | 10.1s |
| 47 | Mokobara | Check-in medium vs large luggage? | ✅ Good | 148 chars | 16 | 10.2s |
| 55 | Nicobar | Gift sets vs individual items? | ✅ Good | 82 chars (brief) | 16 | 10.1s |
| 59 | PlumGoodness | Conditioner vs hair mask? | ✅ Excellent | 803 chars, educational | 16 | 11.0s |
| 71 | SlurrpFarm | Week 3 vs Week 4 meal plan? | ✅ Good | 360 chars, admitted partial info | 16 | 10.9s |
| 79 | TheManCompany | Summer vs winter grooming? | ✅ Excellent | 730 chars, seasonal breakdown | 16 | 11.1s |

**Score: 10/10 (100%)** — Excellent! All comparison queries use 16 sources (dual search).

### 1.8 How-To Queries (11 queries)

| # | Bot | Query | Status | Content | Sources | Time |
|---|-----|-------|--------|---------|---------|------|
| 8 | zevaramaze | Care for silver jewelry? | ✅ Good | 471 chars, practical | 12 | 19.4s |
| 16 | BigBasket | Order medicines online? | ❌ **FALSE DEFLECT** | "outside my expertise" | 0 | 1.8s |
| 24 | BoAt | Set up soundbar for TV? | ✅ Excellent | 849 chars, step-by-step | 12 | 10.9s |
| 32 | Byju's | Book a free session? | ✅ Good | 143 chars | 12 | 9.8s |
| 40 | Mamaearth | Use Aloe Vera Gel? | ✅ Good | 237 chars | 12 | 10.6s |
| 48 | Mokobara | What's in the Pac Kit? | ✅ Good | 336 chars | 12 | 10.7s |
| 56 | Nicobar | Care for water hyacinth? | ⚠️ **RATE LIMITED** | "too many requests" | 0 | 9.9s |
| 60 | PlumGoodness | Green tea CTMP routine? | ✅ Excellent | 797 chars, step-by-step | 12 | 11.0s |
| 64 | PlumGoodness | Use Oat Nourishing Cream? | ✅ Good | 500 chars | 16 | 11.2s |
| 72 | SlurrpFarm | Make Sprouted Ragi Pongal? | ❌ **FALSE DEFLECT** | "outside my expertise" | 0 | 1.7s |
| 80 | TheManCompany | The Man Mag blog? | ❌ **FALSE DEFLECT** | "outside my expertise" | 0 | 2.8s |

**Score: 7/11 (64%)** — 3 false deflections, 1 rate-limited

---

## 2. Critical Issues Found

### 🔴 Issue #1: Rate Limiting (HIGH — 10% of queries)

**8 queries** received "I'm sorry, I'm getting a lot of requests right now. Please try again in a few minutes." instead of actual answers.

**Affected queries:** #52, #56, #58, #61, #67, #68, #75, #77

**Pattern:** These occurred in clusters (Nicobar #52/#56, PlumGoodness #58/#61, SlurrpFarm #67/#68, TheManCompany #75/#77), suggesting the LLM API rate limiter was triggered by rapid sequential queries to the same bot or within a short time window.

**Impact:**
- Users get unhelpful error messages
- The error takes ~9.5s to return (same as a normal query) — very slow for an error
- Rate limit message is in English even for Hindi/Gujarati queries
- No retry mechanism

**Fix Recommendations:**
1. **Add exponential backoff retry** in the LLM call — retry 2-3 times before giving up
2. **Return rate limit errors faster** — don't wait the full 9.5s pipeline
3. **Localize rate limit messages** — respond in the detected language
4. **Queue requests** instead of rejecting — use Redis queue with rate smoothing
5. **Increase rate limits** for the LLM API key or add a secondary key

---

### 🔴 Issue #2: False Scope Deflections (HIGH — 7.5% of queries)

**6 queries** that were **directly relevant** to the chatbot's domain were wrongly rejected by the scope gate as "outside my expertise."

| # | Bot | Query | Why It Should Have Answered |
|---|-----|-------|---------------------------|
| 16 | BigBasket | "How do I order medicines online from BigBasket?" | Ordering is BigBasket's core function |
| 25 | Byju's | "How important are NCERT notes for UPSC?" | Byju's has NCERT/UPSC content |
| 63 | PlumGoodness | "Tips for faster hair growth?" | Plum has hair products; hair tips are in-scope |
| 65 | SlurrpFarm | "When is my baby ready for solid foods?" | SlurrpFarm literally sells baby food |
| 72 | SlurrpFarm | "How to make Sprouted Ragi Pongal for baby?" | SlurrpFarm has recipes for this |
| 80 | TheManCompany | "What does The Man Mag blog cover?" | The Man Mag is TMC's own blog |

**Root Cause:** The unified_query_analysis LLM call classifies these as "out of scope" because:
1. The query phrasing doesn't directly mention product names or the brand
2. The scope gate relies on the bot description and doesn't have access to full content index
3. Generic how-to queries ("how do I order", "when is my baby ready") get flagged as general knowledge

**Fix Recommendations:**
1. **Widen scope gate tolerance** — if the query mentions the brand name or domain keywords (e.g., "baby food", "grooming", "NCERT"), pass it through
2. **Add a retrieval-first fallback** — if scope gate rejects but a quick vector search returns high-confidence results (score > 0.6), override the deflection
3. **Enrich chatbot description** with domain keywords during setup — auto-extract top keywords from crawled pages
4. **Lower confidence threshold for scope rejection** — currently the scope gate may be too aggressive

---

### 🟡 Issue #3: Missing Product Cards (MEDIUM)

Several bots never return product cards even when discussing products:

| Bot | Queries with Products | Total Product Queries |
|-----|----------------------|----------------------|
| zevaramaze | 6/8 | ✅ Good |
| BigBasket | 3/8 | ⚠️ Moderate |
| BoAt | **0/8** | ❌ Never |
| Byju's | 3/8 | ⚠️ Moderate |
| Mamaearth | 5/8 | ✅ Good |
| Mokobara | 5/8 | ✅ Good |
| Nicobar | 5/8 | ✅ Good |
| PlumGoodness | **0/8** | ❌ Never |
| SlurrpFarm | **0/8** | ❌ Never |
| TheManCompany | **0/8** | ❌ Never |

**4 bots (BoAt, PlumGoodness, SlurrpFarm, TheManCompany)** never returned product cards.

**Root Cause:** Product extraction depends on structured data from crawled pages. These sites may not have structured product schema (JSON-LD, Open Graph) or the crawler couldn't extract price/image/URL data.

**Fix Recommendations:**
1. **Improve product extraction during crawl** — parse common ecommerce page patterns (price regex, image OG tags)
2. **Add manual product card support** — let users define product templates
3. **LLM-based product extraction** — use LLM to identify products from page text during ingestion

---

### 🟡 Issue #4: Thin Responses for Some Product Queries (MEDIUM)

Some product responses are very brief and lack substance:

| # | Bot | Content Length | Issue |
|---|-----|---------------|-------|
| 41 | Mokobara | 50 chars | "Oh nice, here's what we've got! Check these out!" — no actual content |
| 36 | Mamaearth | 89 chars | Minimal detail |
| 55 | Nicobar | 82 chars | "We've got a range..." with no specifics |

These responses rely entirely on the product cards below to carry information, but when product cards also fail, the user gets nothing useful.

**Fix Recommendation:** Set a minimum content threshold — if the LLM response is under 100 chars and mentions "check these out" without specifics, trigger a retry or expand the response.

---

### 🟢 Issue #5: Response Time Variance (LOW)

| Scenario | Avg Time | Range |
|----------|---------|-------|
| Irrelevant deflection | 1.6s | 1.4-2.8s |
| Rate limited | 9.7s | 9.4-10.1s |
| Normal queries | 11.0s | 8.7-20.5s |
| Cold start (first query) | 27.2s | — |

**Cold start** for the first query was 27.2s (loading models, caches). Subsequent queries averaged ~10s. This is acceptable but could be improved.

**Rate-limited responses taking 9.5s is bad** — the pipeline runs the full search + reranking before the LLM call fails.

---

## 3. Bot-Level Performance

| Bot | Score | Product | General | Lang | Missing | Irrelevant | Comparison | How-To | Issues |
|-----|-------|---------|---------|------|---------|------------|------------|--------|--------|
| zevaramaze | **8/8** | ✅ | ✅ | ✅ Gu | ✅ | ✅ | ✅ | ✅ | None |
| BigBasket | **7/8** | ✅ | ✅ | ✅ Hi | ✅ | ✅ | ✅ | ❌ Deflect | Scope gate |
| BoAt | **8/8** | ✅ | ✅ | — | ✅ | ✅ | ✅ | ✅ | No product cards |
| Byju's | **7/8** | ❌ Deflect | ✅ | ✅ Hi, Gu | ✅ | ✅ | ✅ | ✅ | Scope gate |
| Mamaearth | **8/8** | ✅ | ✅ | — | ✅ | ✅ | ✅ | ✅ | None |
| Mokobara | **8/8** | ✅ | ✅ | ✅ Hi | ✅ | ✅ | ✅ | ✅ | None |
| Nicobar | **6/8** | ✅ | ✅ | ✅ Hi, ⚠️ Gu | ✅ | ✅ | ✅ | ⚠️ Rate | Rate limiting |
| PlumGoodness | **5/8** | ⚠️ 1 deflect | ⚠️ Rate | — | ⚠️ Rate | ✅ | ✅ | ✅ | Rate limit + no products |
| SlurrpFarm | **4/8** | ❌ Deflect | ✅ | ⚠️ Hi rate | ✅ | ✅ | ✅ | ❌ Deflect | Scope gate + rate limit |
| TheManCompany | **5/8** | ✅ | ✅ | ⚠️ Hi rate | ⚠️ Rate | ✅ | ✅ | ❌ Deflect | Scope gate + rate limit |

**Top performers:** zevaramaze, Mamaearth, Mokobara, BoAt (8/8 each)  
**Worst performers:** SlurrpFarm (4/8), PlumGoodness & TheManCompany (5/8)

---

## 4. What's Working Well

1. **Irrelevant query deflection: 100%** — The scope gate perfectly rejects truly off-topic queries with fast (~1.6s) responses and friendly messages with emojis
2. **Missing info admission: 100%** — Bots honestly say "I don't have that info" and redirect to official support
3. **Language support: 100% (when not rate-limited)** — All Hindi and Gujarati responses used correct script (Devanagari/Gujarati) with natural phrasing
4. **Comparison queries: 100%** — All used 16 sources (dual search) and provided detailed, structured comparisons
5. **Personality tone** — Responses feel natural with personality ("Oh nice, here's what we've got!", "Oops, that's outside my expertise! 😅")
6. **Source attribution** — Most queries return 12-16 sources with follow-up suggestions

---

## 5. Priority Fixes

### P0 — Fix Immediately

| Issue | Impact | Fix |
|-------|--------|-----|
| Rate limiting hits 10% of queries | Users get useless "try again" messages | Add LLM retry with exponential backoff; add secondary API key |
| Rate limit takes 9.5s to return error | Terrible UX for an error | Detect rate limit early in pipeline, return immediately |

### P1 — Fix This Sprint

| Issue | Impact | Fix |
|-------|--------|-----|
| False scope deflections (7.5%) | In-scope queries wrongly rejected | Add retrieval-first fallback: if vector search returns >0.6 score, override scope gate |
| Scope gate too aggressive for how-to queries | 3/11 how-to queries deflected | Widen scope for "how do I" + brand-related queries |

### P2 — Fix Next Sprint

| Issue | Impact | Fix |
|-------|--------|-----|
| 4 bots have zero product cards | Product queries lack visual cards | Improve crawl-time product extraction |
| Thin responses (<100 chars) | Some answers are just "check these out" | Add minimum response length enforcement |
| Rate limit message not localized | Hindi/Gujarati users get English error | Localize rate limit response using detected language |

---

## 6. Detailed Failure Log

### False Deflections (6 queries)

**#16 — BigBasket: "How do I order medicines online from BigBasket?"**
- Response: "Oops, that's outside my expertise! 😅 I'm here to help with BigBasket's products, orders, and policies."
- Irony: The deflection message literally says "I'm here to help with orders" while rejecting an ordering question
- Fix: The scope gate should recognize "order" + brand name as in-scope

**#25 — Byju's: "How important are NCERT notes for UPSC preparation?"**
- Response: "Hmm, I'm not sure about that one! 🤔 I specialize in Byju's"
- Byju's entire website has NCERT/UPSC content (161 crawled pages)
- Fix: Educational queries about exam prep should be in-scope for education bots

**#63 — PlumGoodness: "What are some tips for faster hair growth?"**
- Response: "Hmm, I'm not sure about that one! I specialize in Plum Goodness"
- Plum has an entire hair care line
- Fix: Hair care tips are directly related to hair products

**#65 — SlurrpFarm: "When is my baby ready to start solid foods?"**
- Response: "That's a bit beyond what I can help with! 😊 But I'm great with anything related to SlurrpFarm."
- SlurrpFarm is literally a baby food company
- Fix: Baby food readiness is core to SlurrpFarm's domain

**#72 — SlurrpFarm: "How do I make Sprouted Ragi Pongal for my baby?"**
- Response: "Oops, that's outside my expertise! 😅"
- SlurrpFarm has baby recipes on their website
- Fix: Recipe queries for baby food should be in-scope

**#80 — TheManCompany: "What does The Man Mag blog cover?"**
- Response: "Oops, that's outside my expertise!"
- The Man Mag IS The Man Company's official blog
- Fix: Brand-owned content (blogs, magazine) should be in-scope

### Rate Limited (8 queries)

| # | Bot | Query | Response |
|---|-----|-------|----------|
| 52 | Nicobar | ઘર માટે કઈ પ્રોડક્ટ્સ છે? | "I'm sorry, I'm getting a lot of requests..." |
| 56 | Nicobar | How do I care for water hyacinth? | "I'm sorry, I'm getting a lot of requests..." |
| 58 | PlumGoodness | Is Plum vegan and cruelty-free? | "I'm sorry, I'm getting a lot of requests..." |
| 61 | PlumGoodness | Anti-aging for mature skin? | "I'm sorry, I'm getting a lot of requests..." |
| 67 | SlurrpFarm | बच्चों के खाने में तेल और फैट्स? | "I'm sorry, I'm getting a lot of requests..." |
| 68 | SlurrpFarm | બાળકોને ડેકેરમાં જમવાની આદત? | "I'm sorry, I'm getting a lot of requests..." |
| 75 | TheManCompany | राखी पर भाई के लिए गिफ्ट? | "I'm sorry, I'm getting a lot of requests..." |
| 77 | TheManCompany | Subscription box? | "I'm sorry, I'm getting a lot of requests..." |

---

## 7. Test Configuration

- **Pipeline:** greeting detection → language detection → unified query analysis → scope gate → cache → hybrid search (vector 0.7 + BM25 0.3) → reranking → LLM streaming → post-processing
- **Search:** pgvector + BM25 hybrid, top-k=12 (16 for comparison)
- **Reranker:** Cross-encoder
- **LLM:** Streaming via SSE
- **Rate limit:** 30 req/min per IP (internal)
- **Delay between queries:** 0.5s

---

*Report generated from automated test run of 80 queries across 10 chatbots.*
