# Comprehensive Chatbot Testing Report (Round 2)

**Generated:** 2026-02-20 17:48:43
**Duration:** 653s (10m)
**Total Queries:** 21
**Valid Scored:** 20
**Rate Limited:** 1
**Errors:** 0
**Overall Average Score:** 8.2/10

## Key Findings Summary

### Per-Bot Performance

| Bot | Category | Pages | Queries | Avg Score | Best Type | Worst Type |
|-----|----------|-------|---------|-----------|-----------|------------|
| ramraj | Fashion/Clothing | 256 | 20 | 8.2 | specific_product (9) | non_product (7) |

### Per-Query-Type Performance

| Query Type | Count | Avg Score | Pass Rate | Common Issues |
|------------|-------|-----------|-----------|---------------|
| specific_product | 4 | 9.2 | 100% | None |
| irrelevant | 1 | 9.0 | 100% | None |
| greeting | 3 | 8.7 | 100% | None |
| product_browse | 4 | 8.2 | 75% | No products returned or mentioned |
| price_query | 4 | 7.5 | 100% | None |
| non_product | 4 | 7.2 | 100% | None |

### Per-Language Performance

| Language | Count | Avg Score | Pass Rate |
|----------|-------|-----------|-----------|
| hi_roman | 2 | 8.5 | 100% |
| gu | 2 | 8.5 | 100% |
| hi | 5 | 8.2 | 100% |
| en | 11 | 8.1 | 91% |


## Detailed Results by Bot


### ramraj (Fashion/Clothing) - https://ramrajcotton.in
- **Pages Crawled:** 256
- **Queries Tested:** 21
- **Average Score:** 8.2/10

| # | Type | Lang | Query | Score | Issues/Notes |
|---|------|------|-------|-------|--------------|
| 1 | greeting | en | Hi there! What can you help me with? | 9/10 |  |
| 2 | greeting | hi | नमस्ते! आप मेरी कैसे मदद कर सकते हैं? | 9/10 |  |
| 3 | greeting | hi_roman | hello bhai, kya help kar sakte ho? | 8/10 |  |
| 4 | product_browse | en | Show me your best shirts | 9/10 | 8 products returned |
| 5 | product_browse | en | What dhotis do you have available? | 4/10 | No products returned or mentioned |
| 6 | product_browse | hi | आपके पास कौन से shirts उपलब्ध हैं? | 10/10 | 8 products returned |
| 7 | product_browse | gu | તમારી પાસે કયા shirts છે? | 10/10 | 8 products returned |
| 8 | specific_product | en | I'm looking for a black shirts | 9/10 | 8 products returned |
| 9 | specific_product | en | Do you have any premium cotton shirts? | 9/10 | 10 products returned |
| 10 | specific_product | hi | मुझे shirts चाहिए जो बहुत अच्छी क्वालिटी का हो | 10/10 | 2 products returned |
| 11 | specific_product | hi_roman | best quality shirts dikhao | 9/10 | 5 products returned |
| 12 | price_query | en | Show me shirts under $30 | 8/10 |  |
| 13 | price_query | en | What's the price range for your dhotis? | 8/10 |  |
| 14 | price_query | hi | 500 रुपये से कम के shirts बताओ | 7/10 | Products shown (likely with prices) |
| 15 | price_query | gu | $50 થી ઓછા shirts બતાવો | 7/10 | Products shown (likely with prices) |
| 16 | non_product | en | What is your return policy? | 8/10 |  |
| 17 | non_product | en | How long does shipping take? | 8/10 |  |
| 18 | non_product | en | Do you offer cash on delivery? | 8/10 |  |
| 19 | non_product | hi | रिटर्न पॉलिसी क्या है? | 5/10 | Response given but unclear policy info |
| 20 | irrelevant | en | What is the capital of France? | 9/10 | Correctly rejected irrelevant query |
| 21 | irrelevant | en | Can you write me a Python script to sort a list? | RATE_LIMITED | RATE_LIMITED; Skipped - rate limit |


## Top Quality Issues

### Low-Scoring Queries (Score <= 4)

| Bot | Type | Lang | Query | Score | Issue |
|-----|------|------|-------|-------|-------|
| ramraj | product_browse | en | What dhotis do you have available?... | 4/10 | No products returned or mentioned |


## Recommendations


### General Recommendations
1. **Irrelevant Query Detection**: Bot should consistently reject off-topic queries
2. **Multilingual Support**: Hindi Devanagari and Gujarati need better handling
3. **Product Return**: More queries should return structured product cards
4. **Suggestion Generation**: Ensure follow-up suggestions are always provided
5. **Context Retention**: Conversation history should maintain context across turns
6. **Complaint Handling**: Bot should show empathy and provide clear resolution steps


## Crawling Analysis

### Crawl Success Rate
| Attempt | Site | Result | Reason |
|---------|------|--------|--------|
| Round 1 | Boat Lifestyle | FAILED (0 pages) | JS-heavy SPA - httpx cannot render JavaScript |
| Round 1 | Sugar Cosmetics | FAILED (0 pages) | JS-heavy SPA |
| Round 1 | Mokobara | FAILED (0 pages) | JS-heavy SPA |
| Round 2 | 10 Shopify stores | FAILED (0 pages) | 10 simultaneous crawls caused OOM crash |
| Round 3 | Beardbrand | SUCCESS (57 pages) | Sequential crawl, SSR content available |
| Round 3 | Death Wish Coffee | SUCCESS (185 pages) | Sequential crawl, rich content |
| Round 3 | Tentree | SUCCESS (200 pages) | Sequential crawl, hit page quota |

**Key Crawl Findings:**
- Crawler uses httpx (plain HTTP), NO headless browser - all JS-heavy sites fail silently
- Running 10+ crawls simultaneously crashes the API container (OOM)
- Sequential crawling of 1-2 sites at a time works reliably
- Sites with sitemaps get discovered and crawled even if main page is JS-heavy
- Background task pattern means container restarts kill active crawls