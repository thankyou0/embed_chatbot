# V5 Chatbot Test Report

**Generated**: 2026-02-22 17:02:23

## Test Summary

| Metric | Value |
|--------|-------|
| Total Attempted | 290 |
| Successful | 261 |
| Rate-Limited | 29 |
| Duration | 4202.3s |

## Per-Bot Results

### Crawl-Tentree

| Dimension | Pass | Total | Rate |
|-----------|------|-------|------|
| Response Received | 83 | 85 | 98% |
| Language Compliance | 66 | 85 | 78% |
| Product Retrieval | 29 | 31 | 94% |
| Greeting Quality | 7 | 7 | 100% |
| Blocked Lang Handled | 7 | 9 | 78% |
| Irrelevant Deflection | 4 | 5 | 80% |
| Missing Info Honesty | 4 | 6 | 67% |
| No Hallucination | 6 | 6 | 100% |
| Edge Case Handled | 5 | 5 | 100% |
| Fast Response (<15s) | 85 | 85 | 100% |
| Sources Provided | 30 | 31 | 97% |
| **Avg Response Time** | | | **10.9s** |

### kriyanta

| Dimension | Pass | Total | Rate |
|-----------|------|-------|------|
| Response Received | 90 | 90 | 100% |
| Language Compliance | 83 | 90 | 92% |
| Product Retrieval | 41 | 44 | 93% |
| Greeting Quality | 6 | 6 | 100% |
| Blocked Lang Handled | 5 | 5 | 100% |
| Irrelevant Deflection | 3 | 4 | 75% |
| Missing Info Honesty | 4 | 6 | 67% |
| No Hallucination | 6 | 6 | 100% |
| Edge Case Handled | 3 | 3 | 100% |
| Fast Response (<15s) | 86 | 90 | 96% |
| Sources Provided | 44 | 44 | 100% |
| **Avg Response Time** | | | **12.4s** |

### zevaramaze

| Dimension | Pass | Total | Rate |
|-----------|------|-------|------|
| Response Received | 86 | 86 | 100% |
| Language Compliance | 80 | 86 | 93% |
| Product Retrieval | 41 | 41 | 100% |
| Greeting Quality | 6 | 6 | 100% |
| Blocked Lang Handled | 4 | 4 | 100% |
| Irrelevant Deflection | 3 | 5 | 60% |
| Missing Info Honesty | 2 | 6 | 33% |
| No Hallucination | 6 | 6 | 100% |
| Edge Case Handled | 2 | 2 | 100% |
| Fast Response (<15s) | 81 | 86 | 94% |
| Sources Provided | 41 | 41 | 100% |
| **Avg Response Time** | | | **12.8s** |


## Per Query-Type Results

| Type | Count | Avg Time |
|------|-------|----------|
| blocked_lang_english | 4 (100% ok) | 10.9s |
| blocked_lang_gujarati | 2 (100% ok) | 4.8s |
| blocked_lang_hindi | 2 (100% ok) | 5.1s |
| blocked_lang_outsider | 10 (100% ok) | 4.7s |
| category_browse | 23 (100% ok) | 13.1s |
| complex | 17 (100% ok) | 13.3s |
| continuation | 18 (100% ok) | 13.6s |
| edge_case | 10 (100% ok) | 9.5s |
| greeting | 19 (100% ok) | 9.8s |
| irrelevant_intelligent | 14 (100% ok) | 11.9s |
| missing_info_order | 4 (100% ok) | 12.9s |
| missing_info_policy | 8 (100% ok) | 11.6s |
| missing_info_product | 6 (100% ok) | 11.2s |
| mixed_lang | 5 (100% ok) | 12.7s |
| multi_turn_summary | 4 (100% ok) | 12.7s |
| non_product_info | 22 (100% ok) | 12.7s |
| price_query | 19 (100% ok) | 12.8s |
| product_browse | 29 (100% ok) | 12.8s |
| product_comparison | 11 (100% ok) | 13.4s |
| product_specific | 34 (94% ok) | 12.9s |

## Weakpoints & Issues

- **Crawl-Tentree**: Language compliance 78% (19/85 failed) — bot sometimes responds in wrong language/script
-   - Query (hi): "Mobius 35L Backpack के बारे में बताओ" → Response snippet: "Ye raha..."
-   - Query (hi): "Lunenberg Sweater का price kitna hai?" → Response snippet: "Ye raha..."
-   - Query (gu): "SeaFleece Full Zip ની કિંમત કેટલી છે?" → Response snippet: "Are, SeaFleece Full Zip ni kimat **98.0 USD** chhe! 
..."
- **Crawl-Tentree**: Product retrieval 94% (2/31 queries returned no products)
-   - Query: "tamari best seller products batavo" → No products returned
-   - Query: "लड़कियों के लिए क्या है?" → No products returned
- **Crawl-Tentree**: Blocked language rejection 78% — bot answers in disallowed languages instead of refusing
-   - Query (en): "Show me your jackets" → "यहाँ कुछ बढ़िया ऑप्शन हैं! Crawl-Tentree ने आपके लिए कुछ शानदार जैकेट और बाहरी प..."
-   - Query (en): "Do you have any sale items?" → "यहाँ कुछ बढ़िया ऑप्शन हैं! हमारे पास विभिन्न प्रकार की बिक्री वाली वस्तुएं हैं, ..."
- **Crawl-Tentree**: Irrelevant query deflection 80% — bot engages with off-topic queries instead of redirecting
-   - Query: "ક્રિકેટ મેચ ક્યારે છે?" → "અરે, ક્રિકેટ મેચ વિશે તમે પૂછ્યું! પરંતુ આ માહિતી મારી પાસે નથી — Crawl-Tentree ..."
- **Crawl-Tentree**: Missing info honesty 67% — bot may fabricate answers for info it doesn't have
-   - Query: "તમારી પાસે sunglasses છે?" → "અરે, હા અમારી પાસે ઘણી સરસ sunglasses છે! અમે તમને કેટલાક સરસ ઓપ્શન બતાવીશું.
..."
-   - Query: "perfume collection બતાવો" → "Are, ghanu saras chhe! Juo Crawl-Tentree pase **perfume collection** su chhe, te ahiya batavu chu:
-..."
- **kriyanta**: Language compliance 92% (7/90 failed) — bot sometimes responds in wrong language/script
-   - Query (gu): "Neptune Wall Clock ની કિંમત કેટલી છે?" → Response snippet: "Ahiya, **NEPTUNE WALL CLOCK** ni kimmat **₹8750** chhe! 
..."
-   - Query (gu): "Doom Light Simmam વિશે જણાવો" → Response snippet: "Are! Doom Light Simmam ek mast product chhe. Aa ek handmade item chhe je 3584.0 ..."
-   - Query (gu): "Chromatic Peacock Elegance Wall Art ની price શું છે?" → Response snippet: "Are, Chromatic Peacock Elegance Wall Art ni price **2172.0 INR** chhe! 
..."
- **kriyanta**: Product retrieval 93% (3/44 queries returned no products)
-   - Query: "Tell me about the Doom Light Simmam" → No products returned
-   - Query: "Doom Light Simmam વિશે જણાવો" → No products returned
-   - Query: "5000 rupiya ni niche su malse?" → No products returned
- **kriyanta**: Irrelevant query deflection 75% — bot engages with off-topic queries instead of redirecting
-   - Query: "ક્રિકેટ મેચ ક્યારે છે?" → "ઓહો, ક્રિકેટ મેચ વિશે માહિતી મારી પાસે નથી — ક્રિયાંતા પાસે આ વિશે કંઈ જણાવ્યું ..."
- **kriyanta**: Missing info honesty 67% — bot may fabricate answers for info it doesn't have
-   - Query: "warranty ketla varsh ni chhe?" → "Are, warranty ni details ahiya nathi — kriyanta ne directly contact karo. ..."
-   - Query: "Show me your curtains collection" → "Oh nice, here's what we've got! We have a variety of curtain collections that can complement any roo..."
- **kriyanta**: 4/90 responses slower than 15s (avg slow: 19.2s)
- **zevaramaze**: Language compliance 93% (6/86 failed) — bot sometimes responds in wrong language/script
-   - Query (hi): "Moissanite Diamond Cocktail Ring का price batao" → Response snippet: "Ye raha aapka collection! Ye saare Moissanite Diamond Rings hain jo aapko pasand..."
-   - Query (hi): "क्या shipping free है?" → Response snippet: "Haan, zevaramaze mein **Free Domestic Shipping** hai! 😊

..."
-   - Query (hi): "दूसरे साइज़ में है?" → Response snippet: "Hmm, let me check. I don't have information about other sizes for these products..."
- **zevaramaze**: Irrelevant query deflection 60% — bot engages with off-topic queries instead of redirecting
-   - Query: "पिज़्ज़ा कैसे बनाते हैं?" → "ओह, पिज़्ज़ा बनाना एक मजेदार प्रक्रिया है! लेकिन मैं आपको बता दूं, zevaramaze के..."
-   - Query: "शेयर मार्केट में पैसा कैसे लगाएं?" → "अरे, यह सवाल तो zevaramaze से जुड़ा नहीं है! मैं केवल zevaramaze के प्रोडक्ट्स औ..."
- **zevaramaze**: Missing info honesty 33% — bot may fabricate answers for info it doesn't have
-   - Query: "COD available है क्या?" → "Are! COD option zaroor available hai, lekin mujhe uske details nahin mil rahe hain ..."
-   - Query: "international shipping available hai kya?" → "Arre, international shipping ke bare mein toh mujhe pata nahi hai ..."
-   - Query: "Show me diamond studded watches" → "Oh nice, here's what we've got! You can check out our collection of diamond studded watches in the c..."
- **zevaramaze**: 5/86 responses slower than 15s (avg slow: 16.3s)

## Recommended Fixes

1. [Crawl-Tentree] Strengthen language detection in Call1 prompt — enforce script matching for hi, gu languages
2. [Crawl-Tentree] Improve embedding search to handle non-English product queries — transliterate queries before vector search
3. [Crawl-Tentree] Add stricter language gate in system prompt — refuse with redirect when query language is not in allowed list
4. [Crawl-Tentree] Tighten Call1 is_product=false handling — always redirect off-topic queries to store catalog
5. [Crawl-Tentree] Add explicit guardrail: if no matching embeddings found for order/policy/out-of-catalog queries, respond with 'I don't have that information'
6. [kriyanta] Strengthen language detection in Call1 prompt — enforce script matching for en, gu languages
7. [kriyanta] Improve embedding search to handle non-English product queries — transliterate queries before vector search
8. [kriyanta] Tighten Call1 is_product=false handling — always redirect off-topic queries to store catalog
9. [kriyanta] Add explicit guardrail: if no matching embeddings found for order/policy/out-of-catalog queries, respond with 'I don't have that information'
10. [kriyanta] Optimize Call1+Call2 pipeline — consider caching common query patterns or reducing max_tokens
11. [zevaramaze] Strengthen language detection in Call1 prompt — enforce script matching for en, hi languages
12. [zevaramaze] Tighten Call1 is_product=false handling — always redirect off-topic queries to store catalog
13. [zevaramaze] Add explicit guardrail: if no matching embeddings found for order/policy/out-of-catalog queries, respond with 'I don't have that information'
14. [zevaramaze] Optimize Call1+Call2 pipeline — consider caching common query patterns or reducing max_tokens

## Sample Responses (by type)

### blocked_lang_english

**Query** (en): Show me your jackets

**Response**: यहाँ कुछ बढ़िया ऑप्शन हैं! Crawl-Tentree ने आपके लिए कुछ शानदार जैकेट और बाहरी परिधान तैयार किए हैं। \n 

Products: 6 | Sources: 12 | Time: 13.38s

### blocked_lang_gujarati

**Query** (gu): મને ચાંદીની વીંટી બતાવો

**Response**: I'm sorry, Gujarati (ગુજરાતી) is not supported for this chatbot. This chatbot is configured to support: English, Hindi (हिंदी). Please ask your question in one of the supported languages.

Products: 0 | Sources: 0 | Time: 4.76s

### blocked_lang_hindi

**Query** (hi): मुझे वॉल क्लॉक दिखाओ

**Response**: I'm sorry, Hindi (हिंदी) is not supported for this chatbot. This chatbot is configured to support: English, Gujarati (ગુજરાતી). Please ask your question in one of the supported languages.

Products: 0 | Sources: 0 | Time: 4.89s

### blocked_lang_outsider

**Query** (fr): Bonjour, montrez-moi vos vestes

**Response**: I'm sorry, this language is not supported for this chatbot. This chatbot is configured to support: Hindi (हिंदी), Gujarati (ગુજરાતી). Please ask your question in one of the supported languages.

Products: 0 | Sources: 0 | Time: 4.67s

### category_browse

**Query** (hi): लड़कियों के लिए क्या है?

**Response**: अरे! Crawl-Tentree के पास लड़कियों के लिए काफी बढ़िया कलेक्शन है। \n  \n यहाँ कुछ ऑप्शन्स हैं: \n  \n *   **Womens InMotion High Rise Legging**: **$68.0** में, यह हाई-राइज़ लेगिंग कंफर्ट और स्टाइल दोनों देती है। \n *   **Womens Weston Dress**: यह खूबसूरत ड्रेस **$108.0** में उपलब्ध है, जो किसी भी खास मौके के लिए प

Products: 0 | Sources: 12 | Time: 12.9s

### complex

**Query** (hi): मुझे ऐसा jacket चाहिए जो sustainable हो और 150 dollar से कम हो

**Response**: यहाँ कुछ बढ़िया ऑप्शन हैं! हमारे पास कुछ सस्टेनेबल जैकेट हैं जो आपके बजट में आते हैं। \n 

Products: 8 | Sources: 12 | Time: 12.99s

### continuation

**Query** (hi): और बताओ इसके बारे में

**Response**: Arre, tentree ki sustainability report dekhoge to pata chalega ki ye brand kitna dedicated hai environment ko protect karne mein! Unhone 110 million se zyada trees plant kiye hain aur climate, transparency, aur community ke liye kaam karte hain. Unke products bhi sustainable materials se bane hote h

Products: 0 | Sources: 12 | Time: 12.64s

### edge_case

**Query** (hi): 

**Response**: It looks like you've stumbled upon our Crawl-Tentree page. We've got a few different things going on here, but it seems like we're showcasing some products and initiatives. There's a **Give 20%, Get $20** referral program, and we're also highlighting our efforts to reduce emissions with a **Net Zero

Products: 0 | Sources: 7 | Time: 8.33s

### greeting

**Query** (hi): नमस्ते!

**Response**: नमस्ते! अरे, आपका स्वागत है! Crawl-Tentree के साथ क्या मदद कर सकते हैं?  \n 

Products: 0 | Sources: 0 | Time: 4.65s

### irrelevant_intelligent

**Query** (hi): आज मौसम कैसा है?

**Response**: अरे! मैं Crawl-Tentree के प्रोडक्ट्स के बारे में आपकी मदद कर सकती हूँ, लेकिन मौसम के बारे में जानकारी मेरे पास नहीं है। \n 

Products: 0 | Sources: 12 | Time: 12.23s

### missing_info_order

**Query** (hi): मैंने कल order किया था, delivery कब होगी?

**Response**: अरे, आपका ऑर्डर कल ही गया है, तो डिलीवरी की जानकारी मुझे नहीं है 

Products: 10 | Sources: 12 | Time: 12.36s

### missing_info_policy

**Query** (hi): international shipping India में available है?

**Response**: अरे, international shipping के बारे में जानकारी नहीं है — Crawl-Tentree को directly पूछो 

Products: 0 | Sources: 0 | Time: 3.36s

### missing_info_product

**Query** (gu): તમારી પાસે sunglasses છે?

**Response**: અરે, હા અમારી પાસે ઘણી સરસ sunglasses છે! અમે તમને કેટલાક સરસ ઓપ્શન બતાવીશું. \n 

Products: 9 | Sources: 12 | Time: 12.89s

### mixed_lang

**Query** (hi-en): mujhe ek accha jacket chahiye for winter

**Response**: Are, yahan kuch badhiya options hain! Maine ye aapke liye dhoondhe - Crawl-Tentree ke paas **Mens Nimbus Rain Jacket** aur **Mens Woodford Jacket** jaise sustainable jackets available hain. \n 

Products: 10 | Sources: 12 | Time: 12.73s

### multi_turn_summary

**Query** (hi): पिछली बार मैंने क्या पूछा था?

**Response**: माफ़ कीजिये, यह हमारी पहली बातचीत है, तो मुझे नहीं पता कि आपने पिछली बार क्या पूछा था। लेकिन अगर आप कुछ पूछना चाहते हैं, तो मैं यहाँ हूँ आपकी मदद के लिए! \n 

Products: 0 | Sources: 12 | Time: 13.41s

### non_product_info

**Query** (hi): tentree किस चीज़ के लिए जाना जाता है?

**Response**: अरे! tentree अपनी sustainability के लिए जाना जाता है। वो हर खरीदे हुए प्रोडक्ट के लिए 10 पेड़ लगाते हैं, और अब तक 110 मिलियन से ज़्यादा पेड़ लगा चुके हैं। उनका मकसद है planet को restore करना। \n  \n 

Products: 0 | Sources: 12 | Time: 14.84s

### price_query

**Query** (hi): 5000 रुपये से कम में क्या मिलेगा?

**Response**: यहाँ कुछ बढ़िया ऑप्शन हैं! 5000 रुपये से कम में बहुत सारे प्रोडक्ट अवेलेबल हैं। \n 

Products: 10 | Sources: 12 | Time: 9.39s

### product_browse

**Query** (en): Show me your rings

**Response**: Oh nice, here's what we've got! We've got quite a range of beautiful rings from zevaramaze, and I'd be happy to show them to you. \n 

Products: 8 | Sources: 12 | Time: 12.11s

### product_comparison

**Query** (hi): Woodford Jacket और Dunes Shacket में क्या अंतर है?

**Response**: Ye dono jackets bahut acche hain, Woodford Jacket thoda heavier hai aur Dunes Shacket lighter. \n 

Products: 10 | Sources: 16 | Time: 12.12s

### product_specific

**Query** (hi): Woodford Jacket की कीमत क्या है?

**Response**: Are! **Woodford Jacket** की कीमत **USD 148.0** है। \n 

Products: 10 | Sources: 12 | Time: 13.0s


## Detailed Failures

**[Crawl-Tentree]** `product_browse` (gu-Latn)
- Query: tamari best seller products batavo
- Failed: has_products, has_sources
- Response: Are! Crawl-Tentree ke best sellers pooch rahe ho? Yahan kuch popular options hain:  *   **Crawl-Tentree T-Shirt:** Ye bahot hi comfortable aur stylish hai. Alag alag colors aur designs mein milta hai.

**[Crawl-Tentree]** `product_specific` (hi)
- Query: Mobius 35L Backpack के बारे में बताओ
- Failed: has_response, language_ok
- Response: Ye raha

**[Crawl-Tentree]** `product_specific` (hi)
- Query: Lunenberg Sweater का price kitna hai?
- Failed: has_response, language_ok
- Response: Ye raha

**[Crawl-Tentree]** `product_specific` (gu)
- Query: SeaFleece Full Zip ની કિંમત કેટલી છે?
- Failed: language_ok
- Response: Are, SeaFleece Full Zip ni kimat **98.0 USD** chhe!  

**[Crawl-Tentree]** `product_specific` (gu)
- Query: Bluffs Cropped Crew વિશે જણાવો
- Failed: language_ok
- Response: Aa par ek najar nakho! Crawl-Tentree tamari mate ketla saras options layu chhe. 

**[Crawl-Tentree]** `product_specific` (gu)
- Query: Dunes Shacket માં કયા colors available છે?
- Failed: language_ok
- Response: Ahiya ketlak saras options chhe! Dunes Shacket ma kayi colors available chhe, pan huni specific colors kevi chhe te info nathi - Crawl-Tentree pase su chhe. 

**[kriyanta]** `product_specific` (en)
- Query: Tell me about the Doom Light Simmam
- Failed: has_products
- Response: The **Doom Light Simmam** is a unique product we have. It's priced at **INR 3584.0**. We also offer free interior decoration consultation and have handmade treasures from over 350 Indian artists. Plus

**[Crawl-Tentree]** `product_comparison` (hi)
- Query: Woodford Jacket और Dunes Shacket में क्या अंतर है?
- Failed: language_ok
- Response: Ye dono jackets bahut acche hain, Woodford Jacket thoda heavier hai aur Dunes Shacket lighter. 

**[Crawl-Tentree]** `product_comparison` (gu)
- Query: SeaFleece અને TreeFleece માં શું ફરક છે?
- Failed: language_ok
- Response: Are,SeaFleece ane TreeFleece ma farak chhe, su chhe ke SeaFleece ma REPREVE Our Ocean polyester vapoorto chhe, ane TreeFleece ma 100% organic cotton, TENCEL vaporto chhe. 

**[zevaramaze]** `product_specific` (hi)
- Query: Moissanite Diamond Cocktail Ring का price batao
- Failed: language_ok
- Response: Ye raha aapka collection! Ye saare Moissanite Diamond Rings hain jo aapko pasand aa sakte hain. 

**[kriyanta]** `product_specific` (gu)
- Query: Neptune Wall Clock ની કિંમત કેટલી છે?
- Failed: language_ok
- Response: Ahiya, **NEPTUNE WALL CLOCK** ni kimmat **₹8750** chhe!  

**[kriyanta]** `product_specific` (gu)
- Query: Doom Light Simmam વિશે જણાવો
- Failed: language_ok, has_products
- Response: Are! Doom Light Simmam ek mast product chhe. Aa ek handmade item chhe je 3584.0 INR ma available chhe. Kaka, kriyanta unique ane customized products mate j che, jema 350 thi vadhare Indian artists ni 

**[kriyanta]** `product_specific` (gu)
- Query: Chromatic Peacock Elegance Wall Art ની price શું છે?
- Failed: language_ok
- Response: Are, Chromatic Peacock Elegance Wall Art ni price **2172.0 INR** chhe!  

**[Crawl-Tentree]** `category_browse` (hi)
- Query: लड़कियों के लिए क्या है?
- Failed: has_products
- Response: अरे! Crawl-Tentree के पास लड़कियों के लिए काफी बढ़िया कलेक्शन है।  यहाँ कुछ ऑप्शन्स हैं:  *   **Womens InMotion High Rise Legging**: **$68.0** में, यह हाई-राइज़ लेगिंग कंफर्ट और स्टाइल दोनों देती है। 

**[kriyanta]** `product_comparison` (gu)
- Query: Acrylic wall art અને Crystal wall art માં શું ફરક છે?
- Failed: language_ok
- Response: Aa par ek najar nakho! Kriyanta pase acrylic ane crystal wall art ma ketlak saras collection chhe. 

**[Crawl-Tentree]** `category_browse` (gu)
- Query: accessories collection બતાવો
- Failed: language_ok
- Response: Ahiya ketlak saras options chhe! Juo Crawl-Tentree pase su chhe, accessories collection ma hats, sustainable backpacks, socks, beanies, ane bags jeva chhe. 

**[kriyanta]** `price_query` (gu-Latn)
- Query: 5000 rupiya ni niche su malse?
- Failed: has_products
- Response: Arey! Tamare ₹5000 ni niche ketla saras options chhe! Kriyanta handmade products ma best chhe. Tey unique ane customized items offer kare chhe, je 350+ Indian artists dwara banaveli chhe.  Aapne ₹1000

**[Crawl-Tentree]** `continuation` (hi)
- Query: और बताओ इसके बारे में
- Failed: language_ok
- Response: Arre, tentree ki sustainability report dekhoge to pata chalega ki ye brand kitna dedicated hai environment ko protect karne mein! Unhone 110 million se zyada trees plant kiye hain aur climate, transpa

**[Crawl-Tentree]** `continuation` (hi)
- Query: दूसरे रंग में है क्या?
- Failed: language_ok
- Response: Oh, aapko dusre colors ke baare mein poochhna hai, right?  **"tentree's Nature-Inspired Color Palette for Fall & Winter"** product ka price **USD 100.0** hai. Ye palette nature se inspire hokar banaya

**[Crawl-Tentree]** `continuation` (gu)
- Query: એના વિશે વધુ જણાવો
- Failed: language_ok
- Response: Sure! "A Look Back at 2023" product ke baare mein aapko aur jaanna hai, right?  Is product ki **price USD 100.0** hai. Ye ek special review hai 2023 ka, jismein company ne: *   **3,000,000 tonnes se z

**[zevaramaze]** `non_product_info` (hi)
- Query: क्या shipping free है?
- Failed: language_ok
- Response: Haan, zevaramaze mein **Free Domestic Shipping** hai! 😊  

**[Crawl-Tentree]** `irrelevant_intelligent` (hi)
- Query: pizza kaise banate hai?
- Failed: language_ok
- Response: Are! Main sirf Crawl-Tentree ke products mein help kar sakta hoon. Aapko kya chahiye? 

**[Crawl-Tentree]** `irrelevant_intelligent` (gu)
- Query: ક્રિકેટ મેચ ક્યારે છે?
- Failed: irrelevant_handled
- Response: અરે, ક્રિકેટ મેચ વિશે તમે પૂછ્યું! પરંતુ આ માહિતી મારી પાસે નથી — Crawl-Tentree પાસે આવી માહિતી નથી 

**[zevaramaze]** `continuation` (hi)
- Query: दूसरे साइज़ में है?
- Failed: language_ok
- Response: Hmm, let me check. I don't have information about other sizes for these products right now. 

**[Crawl-Tentree]** `irrelevant_intelligent` (hi)
- Query: Python programming kaise seekhein?
- Failed: language_ok
- Response: Arre, Python programming seekhne ke liye bahut saari resources available hain! Lekin mujhe lagta hai yeh topic humare Crawl-Tentree products se related nahi hai.  

**[Crawl-Tentree]** `blocked_lang_english` (en)
- Query: Show me your jackets
- Failed: blocked_handled
- Response: यहाँ कुछ बढ़िया ऑप्शन हैं! Crawl-Tentree ने आपके लिए कुछ शानदार जैकेट और बाहरी परिधान तैयार किए हैं। 

**[kriyanta]** `continuation` (gu)
- Query: એના વિશે વધુ જણાવો
- Failed: language_ok, fast_response
- Response: Sure thing! I can help with that.  Are you asking about a specific product, or would you like to know more about our general product range? If you could let me know which item you're interested in, I 

**[Crawl-Tentree]** `blocked_lang_english` (en)
- Query: Do you have any sale items?
- Failed: language_ok, blocked_handled
- Response: यहाँ कुछ बढ़िया ऑप्शन हैं! हमारे पास विभिन्न प्रकार की बिक्री वाली वस्तुएं हैं, जिनमें से आप अपनी पसंद की चीज़ चुन सकते हैं। 

**[kriyanta]** `complex` (gu)
- Query: ઓફિસ માટે motivational wall art જોઈએ, premium look, 3000 ની અંદર
- Failed: language_ok
- Response: Ahiya ketlak saras options chhe! Tamne 3000 rupees ni andar premium look ni motivational wall art milishakay. 

**[zevaramaze]** `irrelevant_intelligent` (hi)
- Query: पिज़्ज़ा कैसे बनाते हैं?
- Failed: irrelevant_handled
- Response: ओह, पिज़्ज़ा बनाना एक मजेदार प्रक्रिया है! लेकिन मैं आपको बता दूं, zevaramaze के पास पिज़्ज़ा से जुड़ी कोई जानकारी नहीं है। हमारे पास ज्वेलरी और एक्सेसरीज़ की जानकारी है, लेकिन पिज़्ज़ा नहीं। 

**[Crawl-Tentree]** `edge_case` (hi)
- Query: 
- Failed: language_ok
- Response: It looks like you've stumbled upon our Crawl-Tentree page. We've got a few different things going on here, but it seems like we're showcasing some products and initiatives. There's a **Give 20%, Get $

**[zevaramaze]** `irrelevant_intelligent` (hi)
- Query: शेयर मार्केट में पैसा कैसे लगाएं?
- Failed: irrelevant_handled
- Response: अरे, यह सवाल तो zevaramaze से जुड़ा नहीं है! मैं केवल zevaramaze के प्रोडक्ट्स और सर्विसेज़ के बारे में जानकारी दे सकता हूं।  

**[kriyanta]** `irrelevant_intelligent` (gu)
- Query: ક્રિકેટ મેચ ક્યારે છે?
- Failed: irrelevant_handled
- Response: ઓહો, ક્રિકેટ મેચ વિશે માહિતી મારી પાસે નથી — ક્રિયાંતા પાસે આ વિશે કંઈ જણાવ્યું નથી. 

**[Crawl-Tentree]** `edge_case` (hi)
- Query: ok
- Failed: language_ok
- Response: Hey, welcome to Crawl-Tentree! We've got quite a range of products here. What are you looking for today? 

**[Crawl-Tentree]** `mixed_lang` (hi-en)
- Query: mujhe ek accha jacket chahiye for winter
- Failed: language_ok
- Response: Are, yahan kuch badhiya options hain! Maine ye aapke liye dhoondhe - Crawl-Tentree ke paas **Mens Nimbus Rain Jacket** aur **Mens Woodford Jacket** jaise sustainable jackets available hain. 

**[Crawl-Tentree]** `mixed_lang` (gu-en)
- Query: tentree ના products eco-friendly છે ke nahi?
- Failed: language_ok
- Response: Are, tentree na products eco-friendly chhe! Te sustainability ni focus karine chhe, ane natural materials use karine chhe.  

**[zevaramaze]** `mixed_lang` (hi-en)
- Query: mujhe ek silver ring chahiye for daily wear
- Failed: language_ok
- Response: Yahan kuch badhiya options hain! Main aapke liye kuch silver rings dhoondh ke laya hoon jo daily wear ke liye perfect hain. 

**[zevaramaze]** `mixed_lang` (hi-en)
- Query: kya ye necklace genuine silver hai?
- Failed: language_ok
- Response: Are, ye sabhi necklaces 925 sterling silver se bani hui hain! Inme se koi bhi genuine silver ki quality ko match karta hai.  

**[kriyanta]** `mixed_lang` (gu-en)
- Query: tamari products handmade chhe ke factory-made?
- Failed: language_ok
- Response: Ahiya tamari products handmade chhe! Kriyanta ne over 350 Indian artists ne banavlu chhe.  

**[Crawl-Tentree]** `missing_info_product` (gu)
- Query: તમારી પાસે sunglasses છે?
- Failed: missing_info_honest
- Response: અરે, હા અમારી પાસે ઘણી સરસ sunglasses છે! અમે તમને કેટલાક સરસ ઓપ્શન બતાવીશું. 

**[Crawl-Tentree]** `missing_info_product` (gu)
- Query: perfume collection બતાવો
- Failed: language_ok, missing_info_honest
- Response: Are, ghanu saras chhe! Juo Crawl-Tentree pase **perfume collection** su chhe, te ahiya batavu chu: - **Deodorant**: suvon, lavender, rose - **Fragrances**: floral, citrus, woody - **Gift sets**: perfu

**[zevaramaze]** `missing_info_policy` (hi)
- Query: COD available है क्या?
- Failed: language_ok, missing_info_honest
- Response: Are! COD option zaroor available hai, lekin mujhe uske details nahin mil rahe hain 

**[zevaramaze]** `missing_info_policy` (hi-Latn)
- Query: international shipping available hai kya?
- Failed: missing_info_honest
- Response: Arre, international shipping ke bare mein toh mujhe pata nahi hai 

**[zevaramaze]** `missing_info_product` (en)
- Query: Show me diamond studded watches
- Failed: missing_info_honest
- Response: Oh nice, here's what we've got! You can check out our collection of diamond studded watches in the carousel. 

**[zevaramaze]** `missing_info_product` (hi)
- Query: सोने के हार दिखाओ
- Failed: missing_info_honest
- Response: यहाँ कुछ बढ़िया ऑप्शन हैं! देखो zevaramaze के पास क्या है। 

**[kriyanta]** `missing_info_policy` (gu-Latn)
- Query: warranty ketla varsh ni chhe?
- Failed: missing_info_honest
- Response: Are, warranty ni details ahiya nathi — kriyanta ne directly contact karo. 

**[kriyanta]** `missing_info_product` (en)
- Query: Show me your curtains collection
- Failed: missing_info_honest
- Response: Oh nice, here's what we've got! We have a variety of curtain collections that can complement any room's decor.  
