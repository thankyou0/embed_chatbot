# CRAWL & TEST QUERIES — 10 Chatbots
**Date:** March 2, 2026  
**Account:** max@gmail.com | **Plan:** Enterprise

---

## CRAWL SUMMARY

| # | Bot Name | Site URL | Pages | Languages | Personality | Category |
|---|----------|----------|-------|-----------|-------------|----------|
| 1 | zevaramaze | zevaramaze.com | 184 | en, gu | friendly | Silver jewelry (rings, earrings, pendants) |
| 2 | BigBasket | bigbasket.com | 143 | en, hi | friendly | Online grocery & medicine delivery |
| 3 | BoAt | boat-lifestyle.com | 152 | en | casual | Audio (earbuds, headphones, speakers, smartwatches) |
| 4 | Byju's | byjus.com | 161 | en, hi, gu | friendly | EdTech (online learning, exam prep, UPSC) |
| 5 | Mamaearth | mamaearth.in | 236 | en | friendly | Natural skincare, haircare, baby care |
| 6 | Mokobara | mokobara.com | 126 | en, hi | casual | Luggage, bags, travel accessories |
| 7 | Nicobar | nicobar.com | 102 | en, hi, gu | friendly | Premium Indian clothing, home decor |
| 8 | Plum Goodness | plumgoodness.com | 120 | en | friendly | Vegan beauty, skincare, haircare |
| 9 | SlurrpFarm | slurrpfarm.com | 135 | en, hi, gu | friendly | Organic baby & kids nutrition |
| 10 | TheManCompany | themancompany.com | 129 | en, hi | professional | Men's grooming products |

**Total pages crawled:** 1,488

---

## TEST QUERIES

Each chatbot has 8 queries across these categories:
- **product** — specific product/feature question the bot should answer from crawled content
- **general** — broad question about the brand/company
- **hindi** — query in Hindi (only for bots with `hi` language)
- **gujarati** — query in Gujarati (only for bots with `gu` language)
- **missing_info** — question about something the bot likely doesn't have info on
- **irrelevant** — completely off-topic query the bot should deflect
- **comparison** — asks to compare products/options
- **how_to** — asks for usage instructions or process

---

### 1. zevaramaze (en, gu) — Silver Jewelry

| # | Query | Language | Type | Expected Behavior |
|---|-------|----------|------|-------------------|
| 1 | What silver rings do you have for men? | en | product | Should list men's rings (Caius, Diamond Stud, etc.) |
| 2 | Tell me about Zevar Amaze — what kind of jewelry do you sell? | en | general | Should describe the brand, silver jewelry focus |
| 3 | મોઈસનાઈટ રિંગ્સ વિશે મને જણાવો | gu | gujarati | Should answer about moissanite rings in Gujarati |
| 4 | શું તમારી પાસે ગોલ્ડ જ્વેલરી છે? | gu | gujarati | Should say they focus on silver, not gold |
| 5 | What is your return and exchange policy? | en | missing_info | May not have policy pages — should admit limitation |
| 6 | Can you help me book a flight to Mumbai? | en | irrelevant | Should deflect — not related to jewelry |
| 7 | What's the difference between moissanite and CZ rings? | en | comparison | Should compare moissanite vs CZ from product descriptions |
| 8 | How do I take care of my silver jewelry? | en | how_to | May provide care tips if available, or suggest contacting support |

### 2. BigBasket (en, hi) — Online Grocery & Medicine

| # | Query | Language | Type | Expected Behavior |
|---|-------|----------|------|-------------------|
| 1 | What ayurveda products are available on BigBasket? | en | product | Should describe Ayurveda product range |
| 2 | What is BigBasket and what do they deliver? | en | general | Should describe online grocery/medicine store |
| 3 | क्या बिगबास्केट पर चॉकलेट गिफ्ट बॉक्स मिलते हैं? | hi | hindi | Should answer about chocolate gift boxes in Hindi |
| 4 | प्रोटीन सप्लीमेंट्स कौन कौन से हैं? | hi | hindi | Should list protein supplements in Hindi |
| 5 | Does BigBasket deliver to the US or Europe? | en | missing_info | Likely no info — should admit limitation |
| 6 | How do I invest in the stock market? | en | irrelevant | Should deflect — not related to groceries |
| 7 | Which is better — buying medicine online vs Ayurveda products on your site? | en | comparison | Should compare the two categories |
| 8 | How do I order medicines online from BigBasket? | en | how_to | Should describe the ordering process if available |

### 3. BoAt (en) — Audio & Smartwatches

| # | Query | Language | Type | Expected Behavior |
|---|-------|----------|------|-------------------|
| 1 | What are the best boAt ANC earbuds? | en | product | Should list ANC earbuds models (Rockerz 512, 551 Pro) |
| 2 | What is boAt Lifestyle and what products do they make? | en | general | Should describe the brand and product range |
| 3 | Which portable speakers are good for a party under ₹8000? | en | product | Should recommend party speakers under ₹8000 |
| 4 | What smartwatches did boAt launch recently? | en | product | Should mention Lunar Discovery Neo / Lunar Series |
| 5 | Does boAt offer international warranty? | en | missing_info | Likely no info on warranty terms |
| 6 | Can you recommend a good laptop for programming? | en | irrelevant | Should deflect — boAt doesn't sell laptops |
| 7 | What's the difference between TWS earbuds, neckbands, and headphones for ANC? | en | comparison | Should explain differences from their comparison article |
| 8 | How do I set up a boAt soundbar for my TV? | en | how_to | Should describe soundbar setup if content available |

### 4. Byju's (en, hi, gu) — EdTech / Learning

| # | Query | Language | Type | Expected Behavior |
|---|-------|----------|------|-------------------|
| 1 | How important are NCERT notes for UPSC preparation? | en | product | Should describe NCERT importance from their article |
| 2 | What is BYJU'S and what courses do they offer? | en | general | Should describe the learning platform |
| 3 | UPSC की तैयारी के लिए BYJU'S कैसे मदद करता है? | hi | hindi | Should answer about UPSC prep help in Hindi |
| 4 | બાયજુસ પર કઈ કઈ પરીક્ષાઓની તૈયારી કરી શકાય? | gu | gujarati | Should answer about exam prep options in Gujarati |
| 5 | Does Byju's offer courses for MBA entrance exams like CAT? | en | missing_info | May not have CAT-specific info from crawled pages |
| 6 | What is the best recipe for butter chicken? | en | irrelevant | Should deflect — not related to education |
| 7 | What's the difference between Byju's Classes and the Learning App? | en | comparison | Should compare the two offerings |
| 8 | How do I book a free session on Byju's? | en | how_to | Should guide to booking from their "Book Free Session" page |

### 5. Mamaearth (en) — Natural Personal Care

| # | Query | Language | Type | Expected Behavior |
|---|-------|----------|------|-------------------|
| 1 | What baby care products does Mamaearth have? | en | product | Should list baby wash, shampoo, etc. |
| 2 | Tell me about Mamaearth as a brand — are products really toxin-free? | en | general | Should describe the brand philosophy |
| 3 | Which Mamaearth shampoo is best for hair treatment? | en | product | Should recommend BhringAmla shampoo from reviews |
| 4 | Do you have any charcoal-based makeup products? | en | product | Should mention Charcoal Black Kajal Kohl Pencil |
| 5 | Does Mamaearth ship to Canada? | en | missing_info | Likely no international shipping info |
| 6 | Can you help me find a good dentist near me? | en | irrelevant | Should deflect — not related to beauty products |
| 7 | What's the difference between Aqua Glow Face Wash and the regular one? | en | comparison | Should compare if product info available |
| 8 | How do I use the Aloe Vera Gel for skin and hair? | en | how_to | Should give usage instructions from their review pages |

### 6. Mokobara (en, hi) — Luggage & Bags

| # | Query | Language | Type | Expected Behavior |
|---|-------|----------|------|-------------------|
| 1 | What luggage sets are available on Mokobara? | en | product | Should describe Iconic Luggage Set of 2 and others |
| 2 | What is Mokobara known for? | en | general | Should describe the luggage/travel brand |
| 3 | क्या मोकोबारा पर बैकपैक मिलते हैं? | hi | hindi | Should answer about backpacks in Hindi (Bliss Backpack) |
| 4 | कौन सा ब्रीफकेस बिज़नेस ट्रैवल के लिए अच्छा है? | hi | hindi | Should recommend Bliss Briefcase in Hindi |
| 5 | Does Mokobara offer a lifetime warranty on luggage? | en | missing_info | Likely no warranty details in crawled content |
| 6 | What is the capital of France? | en | irrelevant | Should deflect — not related to bags |
| 7 | How does the check-in medium compare to the large luggage? | en | comparison | Should compare sizes from their set page |
| 8 | What's in the Pac Kit and how do I use it? | en | how_to | Should describe the Pac Kit contents |

### 7. Nicobar (en, hi, gu) — Premium Clothing & Home

| # | Query | Language | Type | Expected Behavior |
|---|-------|----------|------|-------------------|
| 1 | What kurta sets do you have? | en | product | Should list kurtas (Calicut Kurta Set etc.) |
| 2 | What is Nicobar and what kind of products do they sell? | en | general | Should describe Indian premium lifestyle brand |
| 3 | क्या निकोबार पर साड़ी मिलती है? | hi | hindi | Should answer about saris (Urooj Sari etc.) in Hindi |
| 4 | ઘર માટે કઈ પ્રોડક્ટ્સ છે? | gu | gujarati | Should describe home products (rugs, mirrors) in Gujarati |
| 5 | Does Nicobar have a physical store in Delhi? | en | missing_info | Likely no store locations in crawled data |
| 6 | How do I cook biryani? | en | irrelevant | Should deflect — not related to clothing |
| 7 | What gift sets do you have compared to individual items? | en | comparison | Should compare gift sets vs individual products |
| 8 | How do I care for my Nicobar water hyacinth home product? | en | how_to | May not have care instructions — should guide to support |

### 8. Plum Goodness (en) — Vegan Beauty

| # | Query | Language | Type | Expected Behavior |
|---|-------|----------|------|-------------------|
| 1 | What dandruff control products does Plum have? | en | product | Should mention tea tree dandruff control shampoo |
| 2 | Is Plum Goodness really vegan and cruelty-free? | en | general | Should describe the brand's vegan commitment |
| 3 | What's the difference between a hair conditioner and a hair mask? | en | comparison | Should explain differences from their article |
| 4 | How do I use the green tea CTMP routine? | en | how_to | Should describe the CTMP routine from their article |
| 5 | Does Plum have anti-aging products for mature skin? | en | missing_info | May not be in crawled content |
| 6 | Can you explain quantum physics? | en | irrelevant | Should deflect — not related to beauty |
| 7 | What are some tips for faster hair growth? | en | product | Should share tips from their hair growth article |
| 8 | How do I use the 1% Oat & Allantoin Nourishing Cream? | en | how_to | Should give usage instructions from their article |

### 9. SlurrpFarm (en, hi, gu) — Baby & Kids Nutrition

| # | Query | Language | Type | Expected Behavior |
|---|-------|----------|------|-------------------|
| 1 | When is my baby ready to start solid foods? | en | product | Should describe 4 signs of readiness from their article |
| 2 | What is SlurrpFarm and what kind of food do they make? | en | general | Should describe organic baby/kids food brand |
| 3 | बच्चों के खाने में कौन से तेल और फैट्स अच्छे हैं? | hi | hindi | Should answer about oils & fats for babies in Hindi |
| 4 | બાળકોને ડેકેરમાં જમવાની આદત કેવી રીતે પાડવી? | gu | gujarati | Should share daycare mealtime tips in Gujarati |
| 5 | Does SlurrpFarm deliver outside India? | en | missing_info | Likely no international shipping info |
| 6 | What is the best smartphone to buy in 2026? | en | irrelevant | Should deflect — not related to baby food |
| 7 | What's the difference between the Week 3 meal plan and Week 4? | en | comparison | Should compare meal plans if content available |
| 8 | How do I make Sprouted Ragi Pongal for my baby? | en | how_to | Should give the recipe from their article |

### 10. TheManCompany (en, hi) — Men's Grooming

| # | Query | Language | Type | Expected Behavior |
|---|-------|----------|------|-------------------|
| 1 | What grooming products does The Man Company sell? | en | product | Should describe beard, hair, skin products |
| 2 | What is The Man Company all about? | en | general | Should describe the men's grooming brand |
| 3 | राखी पर भाई के लिए क्या गिफ्ट दे सकते हैं? | hi | hindi | Should suggest unconventional Rakhi gifts from their article |
| 4 | 2020 में The Man Company ने क्या कहा था? | hi | hindi | Should reference their reflective 2020 blog post |
| 5 | Does The Man Company offer a subscription box? | en | missing_info | Likely no subscription info in crawled content |
| 6 | How do I fix a leaking kitchen faucet? | en | irrelevant | Should deflect — not related to grooming |
| 7 | What grooming products are best for summer vs winter? | en | comparison | Should compare seasonal grooming needs if available |
| 8 | What does The Man Mag blog cover? | en | how_to | Should describe their blog content |

---

## QUERY STATISTICS

| Metric | Count |
|--------|-------|
| Total Chatbots | 10 |
| Total Queries | 80 |
| English queries | 52 |
| Hindi queries | 12 |
| Gujarati queries | 8 |
| Product queries | 20 |
| General queries | 10 |
| Missing info queries | 10 |
| Irrelevant queries | 10 |
| Comparison queries | 10 |
| How-to queries | 10 |
| Multi-language bots (all 3) | 4 (Byju's, Nicobar, SlurrpFarm, zevaramaze*) |
| Two-language bots (en+hi) | 3 (BigBasket, Mokobara, TheManCompany) |
| English-only bots | 3 (BoAt, Mamaearth, Plum Goodness) |

*zevaramaze has en+gu (no hi)

---

## NOTES FOR EXECUTION

1. **Crawl overages:** Most bots slightly exceeded 100 pages due to batch processing (5-10 pages per batch). Actual counts range 102-236 pages.
2. **Nicobar page titles:** All show "Hurray!" as title — but URLs contain product info (kurtas, saris, rugs, gift sets). Content should still be indexed.
3. **Byju's content:** Many pages are "Archive Page" — limited unique content. NCERT/UPSC articles are the best indexed content.
4. **BigBasket:** Mostly medicine and Ayurveda product listing pages — limited unique prose content.
5. **Query language matching:** Hindi queries only sent to bots with `hi` in languages, Gujarati only to bots with `gu`.
6. **Expected failures:** Missing info and irrelevant queries test the bot's ability to gracefully handle unknowns.
