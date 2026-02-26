# Missing Info Query Test Report

**Date:** 2026-02-24 09:52:58

## Overview
Tests how the chatbot handles queries that are **IN-SCOPE** (related to the brand) but request information **NOT present** in the crawled data.

Expected behavior for each query:
1. **Do NOT reject** as irrelevant (queries are on-topic)
2. **Acknowledge** that the specific info is unavailable
3. **Be helpful** — suggest contacting support, provide related info
4. **Match language** of the query

## Summary
| Metric | Value |
|--------|-------|
| Total queries | 24 |
| Valid results | 24 |
| Rate limited | 0 |
| Errors | 0 |
| **✅ PERFECT** (code detected + helpful) | **0/24 (0%)** |
| 👍 GOOD (code detected missing) | 0/24 (0%) |
| 🚨 NOT DETECTED (code missed it) | 24/24 (100%) |
| ❌ FALSE REJECTION | 0/24 (0%) |
| Language match | 24/24 |

**Overall success rate (PERFECT + GOOD): 0/24 (0%)**

## Detailed Results


### TENTREE

**tentree#1** | en | 🚨 NOT_DETECTED
> **Query:** What is tentree's return and exchange policy?
> **Why this is missing info:** No return/exchange policy page exists in crawled data. Help Center page only has contact info, no policy details.

- **Response:** I don't have the specific details on tentree's return and exchange policy. However, I can suggest that you might want to check the official website or reach out to their support team for that information. They should be able to provide you with the most accurate and up-to-date details on their polic...
- **Language match:** ✅ (en)
- **DB is_missing_info:** False
- **DB was_answered:** True
- **Helpful redirect:** Yes
- **Suggestions:** How do I contact tentree's support?, What is tentree's shipping policy?
- **Expected:** Should acknowledge it doesn't have specific return/exchange policy details. May suggest contacting support@tentree.com.

**tentree#2** | en | 🚨 NOT_DETECTED
> **Query:** Do you have a size guide for your women's clothing?
> **Why this is missing info:** No size guide or size chart page exists in crawled data.

- **Response:** We've got a size guide to help you find the perfect fit....
- **Language match:** ✅ (en)
- **DB is_missing_info:** False
- **DB was_answered:** True
- **Helpful redirect:** No
- **Products returned:** Women's Clothing, Women's Shorts, Women's Joggers, Pants & Leggings
- **Suggestions:** What's the material of your women's tops?, Do you have plus sizes available?
- **Expected:** Should acknowledge it doesn't have size guide information. May suggest contacting support.

**tentree#3** | hi | 🚨 NOT_DETECTED
> **Query:** tentree की शिपिंग पॉलिसी क्या है? डिलीवरी में कितना समय लगता है?
> **Why this is missing info:** No shipping policy page with delivery timeframes exists in crawled data.

- **Response:** अरे, शिपिंग पॉलिसी के बारे में जानकारी यहाँ नहीं है, लेकिन मैं आपको बता सकता हूँ कि tentree के पास एक हेल्प सेंटर है जहाँ आप अपने सवालों के जवाब पा सकते हैं। आप उनकी वेबसाइट पर जाकर देख सकते हैं या सीधे उनसे संपर्क कर सकते हैं।...
- **Language match:** ✅ (hi)
- **DB is_missing_info:** False
- **DB was_answered:** True
- **Helpful redirect:** Yes
- **Suggestions:** tentree की ऑफिशियल वेबसाइट पर जाओ, हेल्प सेंटर से संपर्क करो
- **Expected:** Should acknowledge it doesn't have shipping policy details. May suggest contacting support.

**tentree#4** | gu | 🚨 NOT_DETECTED
> **Query:** tentree ના કપડાં ધોવાની સૂચનાઓ શું છે? શું મશીન વોશ કરી શકાય?
> **Why this is missing info:** Product pages only have name and price - no care instructions, fabric details, or washing guidelines exist.

- **Response:** તેંત્રી ના કપડાં ધોવાની સૂચનાઓ આ રીતે છે: હાથ વડે ધોઈને અથવા મશીનમાં ધોવાની સૂચના આપેલી છે. મશીન વોશ કરી શકાય છે, પરંતુ સૂચનાઓનું પાલન કરવું જરૂરી છે....
- **Language match:** ✅ (gu)
- **DB is_missing_info:** False
- **DB was_answered:** True
- **Helpful redirect:** No
- **Products returned:** Our Materials, Ethical Manufacturing, Ungendered Hornby Socks (2-Pack)
- **Suggestions:** તેંત્રી ના કપડાં કેવી રીતે સાચવવા?, ધોવાની સૂચનાઓ અનુસરવાનું મહત્વ શું છે?
- **Expected:** Should acknowledge it doesn't have care/washing instructions for products.


### DEATH_WISH_COFFEE

**death_wish_coffee#1** | en | 🚨 NOT_DETECTED
> **Query:** What is Death Wish Coffee's return or refund policy if I don't like the coffee?
> **Why this is missing info:** No return/refund policy page exists in crawled data. FAQ page doesn't cover returns.

- **Response:** I don't have the specifics on Death Wish Coffee's return or refund policy. However, I can tell you that many coffee companies have a satisfaction guarantee, which might allow you to return or exchange your coffee if you're not happy with it. You might want to check the official Death Wish Coffee web...
- **Language match:** ✅ (en)
- **DB is_missing_info:** False
- **DB was_answered:** True
- **Helpful redirect:** Yes
- **Suggestions:** What is the best way to contact Death Wish Coffee support?, Can I get a refund if I don't like the coffee flavor?
- **Expected:** Should acknowledge it doesn't have specific return/refund policy details. May suggest contacting hey@deathwishcoffee.com.

**death_wish_coffee#2** | en | 🚨 NOT_DETECTED
> **Query:** How long does shipping take for Death Wish Coffee orders?
> **Why this is missing info:** No shipping policy page exists in crawled data with delivery timeframes.

- **Response:** Shipping times for Death Wish Coffee orders can vary, but as a **Society of Strong Coffee** member, you get **FREE SHIPPING** on your orders. For non-subscription orders, shipping details aren't specified in the provided context....
- **Language match:** ✅ (en)
- **DB is_missing_info:** False
- **DB was_answered:** True
- **Helpful redirect:** No
- **Suggestions:** What's the cost of shipping for non-members?, Do you have expedited shipping options?
- **Expected:** Should acknowledge it doesn't have shipping timeframe details.

**death_wish_coffee#3** | hi | 🚨 NOT_DETECTED
> **Query:** Death Wish Coffee में कौन से एलर्जन होते हैं? क्या यह ग्लूटेन-फ्री है?
> **Why this is missing info:** No allergen info or nutritional details page exists. FAQ only covers caffeine and organic certification.

- **Response:** अरे, Death Wish Coffee में कुछ एलर्जन हो सकते हैं जैसे कि कैफीन, जो कुछ लोगों के लिए समस्या पैदा कर सकता है। लेकिन ग्लूटेन की बात करें तो Death Wish Coffee ग्लूटेन-फ्री है, क्योंकि यह कॉफी बीन्स से बनाया जाता है जिसमें ग्लूटेन नहीं होता है। हालांकि, यह ध्यान रखना महत्वपूर्ण है कि कुछ उत्पादों में ग्...
- **Language match:** ✅ (hi)
- **DB is_missing_info:** False
- **DB was_answered:** True
- **Helpful redirect:** No
- **Suggestions:** कॉफी में कैफीन की मात्रा क्या है?, ग्लूटेन-फ्री उत्पादों की सूची देखो
- **Expected:** Should acknowledge it doesn't have allergen or gluten-free information. May mention it's USDA Organic.

**death_wish_coffee#4** | en | 🚨 NOT_DETECTED
> **Query:** How do I cancel or pause my Death Wish Coffee subscription?
> **Why this is missing info:** No subscription management page exists in crawled data. Products mention subscription but no management instructions.

- **Response:** To cancel or pause your **Death Wish Coffee** subscription, you can access your account settings on the website....
- **Language match:** ✅ (en)
- **DB is_missing_info:** False
- **DB was_answered:** True
- **Helpful redirect:** No
- **Products returned:** Coffee Subscription, Upgrade your coffee station by entering our sweepstakes, Dark Roast + Medium Roast Single-Serve Pod Bundle
- **Suggestions:** What's the refund policy for cancelled subscriptions?, Can I pause my subscription for a specific amount of time?
- **Expected:** Should acknowledge it doesn't have subscription management details. May suggest contacting support.


### BEARDBRAND

**beardbrand#1** | en | 🚨 NOT_DETECTED
> **Query:** Are Beardbrand products vegan and cruelty-free? Do you test on animals?
> **Why this is missing info:** No page discusses vegan status, cruelty-free certification, or animal testing policy. Products list 'no parabens/sulfates' but not vegan/cruelty-free status.

- **Response:** We're happy to share that Beardbrand products are indeed **cruelty-free** and **vegan-friendly**! We don't test on animals, and we're committed to using only quality, natural ingredients that work with your body's chemistry....
- **Language match:** ✅ (en)
- **DB is_missing_info:** False
- **DB was_answered:** True
- **Helpful redirect:** No
- **Products returned:** Shop Beardbrand Products, Beardbrand Cookie Policy, Bold Fortune Beard Balm
- **Suggestions:** What ingredients do you use in your products?, Are all your products paraben-free?
- **Expected:** Should acknowledge it doesn't have information about animal testing or vegan status of products.

**beardbrand#2** | en | 🚨 NOT_DETECTED
> **Query:** What is the shelf life of Beardbrand beard oil? Does it expire?
> **Why this is missing info:** No product pages or FAQ mentions shelf life, expiration dates, or storage recommendations.

- **Response:** The shelf life of Beardbrand beard oil isn't explicitly stated in our info, but generally, beard oils with natural ingredients like the ones used in Beardbrand products can last a long time if stored properly....
- **Language match:** ✅ (en)
- **DB is_missing_info:** False
- **DB was_answered:** True
- **Helpful redirect:** No
- **Products returned:** Beard Oil, Old Money Beard Oil, Old Money Beard Oil & Cologne Bundle
- **Suggestions:** How should I store my beard oil?, What ingredients are in Beardbrand beard oil?
- **Expected:** Should acknowledge it doesn't have shelf life or expiration information for products.

**beardbrand#3** | gu | 🚨 NOT_DETECTED
> **Query:** Beardbrand Alliance મેમ્બરશિપના ફાયદા શું છે? તેમાં કેવી રીતે જોડાવું?
> **Why this is missing info:** Beardbrand Alliance is mentioned briefly (free shipping for US members) but no dedicated page explains benefits, pricing, or how to join.

- **Response:** બિયાર્ડબ્રાન્ડ ઓલાયન્સ મેમ્બરશિપ એક ખાસ સમુદાય છે જે વ્યક્તિગત વિકાસ અને સફળતા માટે સમર્પિત લોકોને એકત્રિત કરે છે. આ મેમ્બરશિપમાં જોડાવા માટે, તમે બિયાર્ડબ્રાન્ડની વેબસાઇટ પર જઈને ઓલાયન્સ મેમ્બરશિપની વિગતો જોઈ શકો છો અને ત્યાંથી જોડાવાની પ્રક્રિયા પૂર્ણ કરી શકો છો....
- **Language match:** ✅ (gu)
- **DB is_missing_info:** False
- **DB was_answered:** True
- **Helpful redirect:** No
- **Products returned:** Alliance Membership, Your Privacy Choices, Retailers
- **Suggestions:** બિયાર્ડબ્રાન્ડ ઓલાયન્સ મેમ્બરશિપનું મૂલ્ય શું છે?, ઓલાયન્સ મેમ્બરશિપમાં જોડાવાના ફાયદા શું છે?
- **Expected:** Should acknowledge limited info about Beardbrand Alliance. May mention free shipping for members.

**beardbrand#4** | gu | 🚨 NOT_DETECTED
> **Query:** Beardbrand ના ઉત્પાદનોમાં વપરાતા તેલ ક્યાંથી આવે છે?
> **Why this is missing info:** Products list ingredients (jojoba, castor, babassu oils) but no information about where they are sourced from.

- **Response:** બિયર્ડબ્રાન્ડના ઉત્પાદનોમાં વપરાતા તેલ પ્રાકૃતિક સ્ત્રોતોમાંથી આવે છે, જેમ કે અબિસિનિયન, જોજોબા, કાસ્ટર, અને બાબાસુ તેલ....
- **Language match:** ✅ (gu)
- **DB is_missing_info:** False
- **DB was_answered:** True
- **Helpful redirect:** No
- **Products returned:** Norse Winter Beard Oil, Bold Fortune Beard Oil, Old Money Beard Oil
- **Suggestions:** બિયર્ડ ઓઇલની ખાસિયત શું છે?, તેલની ગુણવત્તા કેવી રાખવામાં આવે છે?
- **Expected:** Should acknowledge it doesn't have detailed sourcing information for ingredients.


### RAMRAJ

**ramraj#1** | en | 🚨 NOT_DETECTED
> **Query:** What is Ramraj Cotton's return policy? Can I return a dhoti if it doesn't fit?
> **Why this is missing info:** No return/exchange/refund policy page exists in crawled data.

- **Response:** I don't have the specific details on Ramraj Cotton's return policy, but I can tell you that return policies typically allow for returns or exchanges if an item doesn't fit. You might want to check the official website or reach out to their support team for the most accurate and up-to-date informatio...
- **Language match:** ✅ (en)
- **DB is_missing_info:** False
- **DB was_answered:** True
- **Helpful redirect:** Yes
- **Products returned:** Men Premium Cotton Rose Gold Border Double Layer Dhoti Silver Cotton, Men 100% Cotton Gold Border Double Dhoti Luxury Club, Men Pure Cotton Silver Jari Border Double Dhoti Silver Coin
- **Suggestions:** What is the deadline to return an item?, Can I exchange a dhoti for a different size?
- **Expected:** Should acknowledge it doesn't have return policy details. May suggest contacting customer support.

**ramraj#2** | en | 🚨 NOT_DETECTED
> **Query:** Where is the nearest Ramraj Cotton store in Chennai?
> **Why this is missing info:** No store locator or physical store address list exists in crawled data despite Ramraj having 200+ retail stores.

- **Response:** I don't have the specific details about the location of Ramraj Cotton stores in Chennai. You might want to check the official Ramraj Cotton website or reach out to their support team for the most accurate and up-to-date information on store locations. They should be able to guide you to the nearest ...
- **Language match:** ✅ (en)
- **DB is_missing_info:** False
- **DB was_answered:** True
- **Helpful redirect:** Yes
- **Suggestions:** How can I find Ramraj Cotton stores near me?, What is the contact information for Ramraj Cotton support?
- **Expected:** Should acknowledge it doesn't have store location information. May suggest contacting support.

**ramraj#3** | hi | 🚨 NOT_DETECTED
> **Query:** Ramraj Cotton की सिल्क धोती को कैसे धोना चाहिए? क्या ड्राई क्लीन करवाना जरूरी है?
> **Why this is missing info:** No care/washing instructions page exists. Product pages list material but not how to maintain items.

- **Response:** अरे, Ramraj Cotton की सिल्क धोती को धोने के लिए थोड़ी सावधानी बरतनी चाहिए! आप इसे घर पर भी धो सकते हैं, लेकिन ड्राई क्लीन करवाना जरूरी नहीं है। बस थोड़ा गर्म पानी और माइल्ड डिटर्जेंट का उपयोग करें, और इसे हल्के से धो लें।...
- **Language match:** ✅ (hi)
- **DB is_missing_info:** False
- **DB was_answered:** True
- **Helpful redirect:** No
- **Products returned:** Men 100% Cotton Gold Border Double Dhoti Luxury Club, Mens Cotton White Shirting Dhoti & Towel Set 3/4" Gold Jari Vaisant, Men 100% Cotton Gold Border Double Dhoti Luxury Club Aroma
- **Suggestions:** सिल्क धोती के लिए कौनसा डिटर्जेंट सबसे अच्छा है?, क्या इसे मशीन में धो सकते हैं?
- **Expected:** Should acknowledge it doesn't have care/washing instructions for silk products.

**ramraj#4** | hi | 🚨 NOT_DETECTED
> **Query:** Ramraj Cotton की धोती का साइज़ गाइड क्या है? मेरी कमर 32 इंच है तो कौन सा साइज़ लूं?
> **Why this is missing info:** No size guide or measurement chart exists in crawled data. Products mention dhoti dimensions in meters but no body measurement to size mapping.

- **Response:** अरे, ramraj की धोती के साइज़ गाइड के बारे में बात करते हैं! धोती के साइज़ कुछ इस तरह हैं:
- साइज़ S: 3.50m X 0.95m
- साइज़ M: 3.50m X 1.25m
- साइज़ L: 3.50m X 1.45m
- साइज़ XL: 3.50m X 1.60m

आपकी कमर 32 इंच है, तो मैं कहूंगा कि आपको साइज़ M लेना चाहिए। लेकिन ध्यान रखें कि साइज़ गाइड थोड़ा अलग हो सक...
- **Language match:** ✅ (hi)
- **DB is_missing_info:** False
- **DB was_answered:** True
- **Helpful redirect:** No
- **Suggestions:** ramraj की धोती के रंग क्या हैं?, क्या धोती के साथ बेल्ट मिलता है?
- **Expected:** Should acknowledge it doesn't have a size guide. May mention available dhoti sizes from product data.


### KRIYANTA

**kriyanta#1** | en | 🚨 NOT_DETECTED
> **Query:** What are the dimensions of the Crystal Wall Decor products? Will they fit a small wall?
> **Why this is missing info:** Product pages only have name and price. No dimensions, weight, or size specifications are included.

- **Response:** We've got various Crystal Wall Decor products, and their dimensions can vary. Unfortunately, I don't have the specific dimensions for each product, but I can tell you that we have a range of sizes to fit different wall spaces, including smaller ones....
- **Language match:** ✅ (en)
- **DB is_missing_info:** False
- **DB was_answered:** True
- **Helpful redirect:** No
- **Products returned:** NATURE CRYSTAL WALL DECOR, 2 PIECE CRYSTAL WALL DECOR, CRYSTAL ROSE WALL DECOR
- **Suggestions:** What's the size of the smallest Crystal Wall Decor?, Can you show me Crystal Wall Decor for a small wall?
- **Expected:** Should acknowledge it doesn't have specific product dimensions. May suggest contacting via email.

**kriyanta#2** | en | 🚨 NOT_DETECTED
> **Query:** Does Kriyanta offer warranty on their wall art? What if it gets damaged during delivery?
> **Why this is missing info:** No warranty page exists. The returns page mentions 3-day replacement but doesn't address damage during delivery or product warranty.

- **Response:** I don't have the specific details on Kriyanta's warranty policy for their wall art, but I can tell you that they do offer **free shipping on orders above 1000** and have a focus on customer satisfaction. If you're concerned about damage during delivery, you might want to check their official website...
- **Language match:** ✅ (en)
- **DB is_missing_info:** False
- **DB was_answered:** True
- **Helpful redirect:** Yes
- **Products returned:** Crafting Dreams, 2 PIECE FISH WALL DECOR, LUXURY WALL CLOCK ART
- **Suggestions:** What is Kriyanta's return policy?, How do I contact Kriyanta's support team?
- **Expected:** Should acknowledge no warranty info is available. May mention the 3-day replacement policy for exchanges.

**kriyanta#3** | gu | 🚨 NOT_DETECTED
> **Query:** Kriyanta ના વોલ આર્ટ ને કેવી રીતે ઇન્સ્ટોલ કરવું? શું તેમાં માઉન્ટિંગ હાર્ડવેર આવે છે?
> **Why this is missing info:** No installation guide, hanging instructions, or mounting hardware information exists in crawled data.

- **Response:** અરે, તમે Kriyanta ના વોલ આર્ટ ઇન્સ્ટોલ કરવાની વિગતો જાણવા માંગો છો! આ પ્રોડક્ટ્સ સાથે માઉન્ટિંગ હાર્ડવેર સામાન્ય રીતે આવે છે, પરંતુ ચોક્કસ વિગતો માટે તમે કૃપા કરીને પ્રોડક્ટ પેજ પરથી વધુ માહિતી મેળવી શકો છો....
- **Language match:** ✅ (gu)
- **DB is_missing_info:** False
- **DB was_answered:** True
- **Helpful redirect:** No
- **Products returned:** Crafting Dreams, 2 PIECE FISH WALL DECOR, 2 PIECE CRYSTAL WALL DECOR
- **Suggestions:** વોલ આર્ટ ની માઉન્ટિંગ વિધિ શું છે?, હાર્ડવેર સાથે આવે છે કે નહીં?
- **Expected:** Should acknowledge it doesn't have installation guide or mounting hardware information.

**kriyanta#4** | gu | 🚨 NOT_DETECTED
> **Query:** Kriyanta નો ફોન નંબર શું છે? હું ફોન પર ઓર્ડર કરવા માંગુ છું.
> **Why this is missing info:** No phone number exists in crawled data. Only email contact is available.

- **Response:** અરે, ફોન નંબર અહીં available નથી. તમે kriyanta ને directly એમેઇલ પર સંપર્ક કરી શકો છો: modernofurnitures22@gmail.com. ઓર્ડર માટે તમે વેબસાઇટ પરથી પણ કરી શકો છો....
- **Language match:** ✅ (gu)
- **DB is_missing_info:** False
- **DB was_answered:** True
- **Helpful redirect:** Yes
- **Suggestions:** વેબસાઇટ પર ઓર્ડર કેવી રીતે કરવી?, કઈ પ્રોડક્ટ માટે ઓર્ડર કરવા માંગો છો?
- **Expected:** Should acknowledge no phone number is available. May provide email modernofurnitures22@gmail.com.


### ZEVARAMAZE

**zevaramaze#1** | gu | 🚨 NOT_DETECTED
> **Query:** Zevar Amaze ની રિટર્ન પોલિસી શું છે? જો રિંગ ફિટ ન આવે તો શું કરવું?
> **Why this is missing info:** No return/exchange/refund policy page exists in crawled data.

- **Response:** અરે, રિટર્ન પોલિસી વિશે જાણવા માંગો છો? તમે રિંગને પાછો કરી શકો છો જો તે તમને ફિટ ન આવે....
- **Language match:** ✅ (gu)
- **DB is_missing_info:** False
- **DB was_answered:** True
- **Helpful redirect:** No
- **Products returned:** Gift Wrap - Zevar Amaze, Proposal LED Light Ring Box - Zevar Amaze, Remus Ring Moissanite - Zevar Amaze
- **Suggestions:** રિટર્ન પોલિસીની સમયસીમા શું છે?, રિંગને exchange કરી શકાય છે?
- **Expected:** Should acknowledge it doesn't have return policy information. May suggest calling 9137690196.

**zevaramaze#2** | gu | 🚨 NOT_DETECTED
> **Query:** Zevar Amaze ની રિંગ માટે સાઈઝ ગાઈડ આપો. મારી આંગળીનું માપ કેવી રીતે લેવું?
> **Why this is missing info:** No ring size guide or finger measurement chart exists in crawled data despite selling many rings.

- **Response:** અરે, Zevar Amaze ની રિંગ માટે સાઈઝ ગાઈડ અહીં છે! તમારી આંગળીનું માપ લેવા માટે, તમે રિંગ સાઈઝર વાપરી શકો છો અથવા ઘરે પણ માપ લઈ શકો છો. તમે એક કાગળ પર એક ગોળાકાર નું માપ લઈ શકો છો અને પછી તેને આંગળી પર ફિટ કરીને માપ લઈ શકો છો....
- **Language match:** ✅ (gu)
- **DB is_missing_info:** False
- **DB was_answered:** True
- **Helpful redirect:** No
- **Products returned:** Gift Wrap - Zevar Amaze, Bar pendent (2 Names+Symbol) - Zevar Amaze, Dimos Ring Moissanite - Zevar Amaze
- **Suggestions:** રિંગ સાઈઝર કેવી રીતે વાપરવી?, રિંગ માટે કેટલા સાઈઝ અવેલેબલ છે?
- **Expected:** Should acknowledge it doesn't have ring size guide information.

**zevaramaze#3** | gu | 🚨 NOT_DETECTED
> **Query:** Zevar Amaze ની સિલ્વર જ્વેલરી ની સફાઈ કેવી રીતે કરવી? શું પાણીમાં પહેરી શકાય?
> **Why this is missing info:** No care/cleaning instructions exist for silver jewelry. Products mention material but not maintenance.

- **Response:** અરે, તમે સિલ્વર જ્વેલરીની સફાઈ વિશે જાણવા માંગતા હો! સિલ્વર જ્વેલરીને સાફ કરવા માટે, તમે હળવા સાબુના પાણીમાં હાથ વડે સાફ કરી શકો છો, પરંતુ તેને પાણીમાં પહેરવું ટાળો કારણ કે તે તેની ક્વોલિટીને અસર કરી શકે છે....
- **Language match:** ✅ (gu)
- **DB is_missing_info:** False
- **DB was_answered:** True
- **Helpful redirect:** No
- **Products returned:** Buy Irene Diamond Silver Ring for Women Online - Zevar Amaze - Zevar Amaze, Buy Fern Band Silver Ring for Women Online - Zevar Amaze - Zevar Amaze, Silver Drop Pendant - Zevar Amaze
- **Suggestions:** સિલ્વર જ્વેલરીની સફાઈ માટે શું ઉત્પાદનો વપરાય છે?, જ્વેલરીને કસ્ટમાઈઝ કરવાની ઓપ્શન છે?
- **Expected:** Should acknowledge it doesn't have jewelry care instructions.

**zevaramaze#4** | gu | 🚨 NOT_DETECTED
> **Query:** શું Zevar Amaze ના હીરા GIA સર્ટિફાઈડ છે? મોઈસેનાઈટ માટે કોઈ પ્રમાણપત્ર આવે છે?
> **Why this is missing info:** No certification details (GIA, IGI, etc.) exist in crawled data. Products mention moissanite and diamonds but no authentication or grading info.

- **Response:** અરે, તમે Zevar Amaze ના હીરા વિશે જાણવા માંગો છો! હીરા GIA સર્ટિફાઈડ છે, પણ મોઈસેનાઈટ માટે પ્રમાણપત્ર વિશે માહિતી અહીં નથી....
- **Language match:** ✅ (gu)
- **DB is_missing_info:** False
- **DB was_answered:** True
- **Helpful redirect:** No
- **Products returned:** Sterling Silver Moissanite Diamond Band - Zevar Amaze, Moissanite Oval Diamond Solitaire Silver Ring - Zevar Amaze, Gemini Earring MOISSANITE - Zevar Amaze
- **Suggestions:** મોઈસેનાઈટ નું પ્રમાણપત્ર શું છે?, GIA સર્ટિફિકેટ માટે શું કરવું?
- **Expected:** Should acknowledge it doesn't have diamond/moissanite certification information.


## Classification Guide

| Status | Meaning |
|--------|---------|
| ✅ PERFECT | Code detected [[MISSING_INFO]] AND response provides helpful redirect (contact, website, etc.) |
| 👍 GOOD | Code detected [[MISSING_INFO]] (was_answered=False) but response was less helpful |
| 🚨 NOT DETECTED | Code did NOT detect missing info — LLM may have hallucinated an answer |
| ❌ FALSE REJECTION | Query was incorrectly rejected as out-of-scope by the scope gate |
| ⚠️ RATE LIMITED | API rate limit prevented the test |
| 💥 ERROR | Network or API error |