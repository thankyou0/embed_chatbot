# Missing Info V2 Test Report (Post-Fix)

**Date:** 2026-02-24 11:22:33

**Fixes applied:** Fix A (products guard), Fix B (contact verify), Fix C (server-side detect + prompt), Fix D (product count injection)

## Summary

### Missing Info Detection (EN only)

| Metric | Value |
|--------|-------|
| Valid queries | 1 |
| ✅ PERFECT (detected + helpful) | 1/1 (100% if mi_results else 'n/a') |
| 👍 GOOD (detected) | 0/1 |
| 🚨 NOT DETECTED | 0/1 |
| ❌ FALSE REJECTION | 0/1 |
| **Detection rate** | **1/1 (100%)**|

### Regression Tests

| Test Type | Result |
|-----------|--------|
| Irrelevant rejection | 3/3 (✅) |
| Greeting response | 0/0 (✅) |
| Product query answer | 0/0 (✅) |
| Rate limited | 15 |
| Errors | 0 |

## Detailed Results


### Missing Info Queries

**MISSING_INFO:tentree#1** | ✅ PERFECT
> **Q:** What is tentree's return and exchange policy?
- **A:** Tentree's return and exchange policy isn't explicitly stated in the information I have, but I can tell you that they do have a **Contact Us** page where you can reach out to their support team for help with returns or exchanges. They also have a **Help Centre** that might have some information on th...
- DB: missing_info=True, answered=False, irrelevant=False
- Expected: Should acknowledge it doesn't have specific return/exchange policy details. May suggest contacting support@tentree.com.

**MISSING_INFO:tentree#2** | ⚠️ RATE_LIMITED
> **Q:** Do you have a size guide for your women's clothing?
- **A:** I'm sorry, I'm getting a lot of requests right now. Please try again in a few minutes....
- DB: missing_info=False, answered=True, irrelevant=False
- Expected: Should acknowledge it doesn't have size guide information. May suggest contacting support.

**MISSING_INFO:death_wish_coffee#1** | ⚠️ RATE_LIMITED
> **Q:** What is Death Wish Coffee's return or refund policy if I don't like the coffee?
- **A:** I'm sorry, I'm getting a lot of requests right now. Please try again in a few minutes....
- DB: missing_info=False, answered=True, irrelevant=False
- Expected: Should acknowledge it doesn't have specific return/refund policy details. May suggest contacting hey@deathwishcoffee.com.

**MISSING_INFO:death_wish_coffee#2** | ⚠️ RATE_LIMITED
> **Q:** How long does shipping take for Death Wish Coffee orders?
- **A:** I'm sorry, I'm getting a lot of requests right now. Please try again in a few minutes....
- DB: missing_info=False, answered=True, irrelevant=False
- Expected: Should acknowledge it doesn't have shipping timeframe details.

**MISSING_INFO:death_wish_coffee#4** | ⚠️ RATE_LIMITED
> **Q:** How do I cancel or pause my Death Wish Coffee subscription?
- **A:** I'm sorry, I'm getting a lot of requests right now. Please try again in a few minutes....
- DB: missing_info=False, answered=True, irrelevant=False
- Expected: Should acknowledge it doesn't have subscription management details. May suggest contacting support.

**MISSING_INFO:beardbrand#1** | ⚠️ RATE_LIMITED
> **Q:** Are Beardbrand products vegan and cruelty-free? Do you test on animals?
- **A:** I'm sorry, I'm getting a lot of requests right now. Please try again in a few minutes....
- DB: missing_info=False, answered=True, irrelevant=False
- Expected: Should acknowledge it doesn't have information about animal testing or vegan status of products.

**MISSING_INFO:beardbrand#2** | ⚠️ RATE_LIMITED
> **Q:** What is the shelf life of Beardbrand beard oil? Does it expire?
- **A:** I'm sorry, I'm getting a lot of requests right now. Please try again in a few minutes....
- DB: missing_info=False, answered=True, irrelevant=False
- Expected: Should acknowledge it doesn't have shelf life or expiration information for products.

**MISSING_INFO:ramraj#1** | ⚠️ RATE_LIMITED
> **Q:** What is Ramraj Cotton's return policy? Can I return a dhoti if it doesn't fit?
- **A:** I'm sorry, I'm getting a lot of requests right now. Please try again in a few minutes....
- DB: missing_info=False, answered=True, irrelevant=False
- Expected: Should acknowledge it doesn't have return policy details. May suggest contacting customer support.

**MISSING_INFO:ramraj#2** | ⚠️ RATE_LIMITED
> **Q:** Where is the nearest Ramraj Cotton store in Chennai?
- **A:** I'm sorry, I'm getting a lot of requests right now. Please try again in a few minutes....
- DB: missing_info=False, answered=True, irrelevant=False
- Expected: Should acknowledge it doesn't have store location information. May suggest contacting support.

**MISSING_INFO:kriyanta#1** | ⚠️ RATE_LIMITED
> **Q:** What are the dimensions of the Crystal Wall Decor products? Will they fit a small wall?
- **A:** I'm sorry, I'm getting a lot of requests right now. Please try again in a few minutes....
- DB: missing_info=False, answered=True, irrelevant=False
- Expected: Should acknowledge it doesn't have specific product dimensions. May suggest contacting via email.

**MISSING_INFO:kriyanta#2** | ⚠️ RATE_LIMITED
> **Q:** Does Kriyanta offer warranty on their wall art? What if it gets damaged during delivery?
- **A:** I'm sorry, I'm getting a lot of requests right now. Please try again in a few minutes....
- DB: missing_info=False, answered=True, irrelevant=False
- Expected: Should acknowledge no warranty info is available. May mention the 3-day replacement policy for exchanges.


### Irrelevant Queries

**IRRELEVANT:tentree#1** | ✅ PASS
> **Q:** Who is the president of the United States?
- **A:** Oops, that's outside my expertise! 😅 I'm here to help with Crawl-Tentree's products, orders, and policies. What can I help you with?...
- DB: missing_info=False, answered=True, irrelevant=True
- Expected: Should be rejected as irrelevant with [[IRRELEVANT]]

**IRRELEVANT:deathwish#1** | ✅ PASS
> **Q:** Write a Python script to sort a list
- **A:** Hmm, I'm not sure about that one! 🤔 I specialize in Crawl-Death Wish Coffee — feel free to ask me anything about our products or services!...
- DB: missing_info=False, answered=True, irrelevant=True
- Expected: Should be rejected as irrelevant with [[IRRELEVANT]]

**IRRELEVANT:beardbrand#1** | ✅ PASS
> **Q:** What is the capital of France?
- **A:** That's a bit beyond what I can help with! 😊 But I'm great with anything related to Crawl-Beardbrand. Ask away!...
- DB: missing_info=False, answered=True, irrelevant=True
- Expected: Should be rejected as irrelevant with [[IRRELEVANT]]


### Greeting Queries

**GREETING:ramraj#1** | ⚠️ RATE_LIMITED
> **Q:** Hello! How are you?
- **A:** I'm sorry, I'm getting a lot of requests right now. Please try again in a few minutes....
- DB: missing_info=False, answered=True, irrelevant=False
- Expected: Should respond with a warm greeting, NOT mark as missing_info

**GREETING:kriyanta#1** | ⚠️ RATE_LIMITED
> **Q:** Hi there
- **A:** I'm sorry, I'm getting a lot of requests right now. Please try again in a few minutes....
- DB: missing_info=False, answered=True, irrelevant=False
- Expected: Should respond with a warm greeting, NOT mark as missing_info


### Product Queries

**PRODUCT:tentree#1** | ⚠️ RATE_LIMITED
> **Q:** Show me your best selling t-shirts
- **A:** I'm sorry, I'm getting a lot of requests right now. Please try again in a few minutes....
- DB: missing_info=False, answered=True, irrelevant=False
- Expected: Should show products from context, NOT mark as missing_info

**PRODUCT:deathwish#1** | ⚠️ RATE_LIMITED
> **Q:** What coffee blends do you have?
- **A:** I'm sorry, I'm getting a lot of requests right now. Please try again in a few minutes....
- DB: missing_info=False, answered=True, irrelevant=False
- Expected: Should list coffee products, NOT mark as missing_info

**PRODUCT:beardbrand#1** | ⚠️ RATE_LIMITED
> **Q:** What beard oils do you sell?
- **A:** I'm sorry, I'm getting a lot of requests right now. Please try again in a few minutes....
- DB: missing_info=False, answered=True, irrelevant=False
- Expected: Should list beard oil products, NOT mark as missing_info
