# Context Enrichment & Follow-Up Test Report

**Date:** 2026-02-24 09:18:12

## Overview
Tests whether previous messages properly enrich follow-up queries across languages.
Each pair: Query 1 (product) → Query 2 (follow-up needing Q1 context).

## Summary
| Metric | Value |
|--------|-------|
| Total pairs | 12 |
| Valid results | 12 |
| Rate limited | 0 |
| Q1/Q2 errors | 0/0 |
| **Context-aware** | **12/12 (100%)** |
| No context | 0/12 (0%) |
| Unclear | 0/12 (0%) |
| Scope gated | 0 |
| Q1 lang match | 12/12 |
| Q2 lang match | 12/12 |

## Detailed Results


### TENTREE

**tentree#1** | en | ✅ CONTEXT_AWARE
> Follow-up about color availability for previously discussed product

- **Q1:** What materials are your t-shirts made from?
- **A1:** We use sustainable materials for our t-shirts. Our tees are made from eco-friendly materials that are good for the planet....
- **Q2:** Are they available in black?
- **A2:** Oh nice, here's what we've got! We don't have a black shirt right now, but check out this **Dark Navy Henley** which might work!...
- **Matched keywords:** shirt, black
- **Keyword score:** 33%

**tentree#2** | hi | ✅ CONTEXT_AWARE
> Hindi follow-up asking price of previously discussed products

- **Q1:** आपके पास कौन से पेड़ लगाने वाले प्रोडक्ट्स हैं?
- **A1:** यहाँ कुछ बढ़िया ऑप्शन हैं! हमारे पास कई पेड़ लगाने वाले प्रोडक्ट्स हैं, जिनमें से प्रत्येक प्रोडक्ट 10 पेड़ लगाने में मदद करता है।...
- **Q2:** इनकी कीमत क्या है?
- **A2:** इन प्रोडक्ट्स की कीमतें अलग-अलग हैं, लेकिन हमारे पास **25.0 USD** से लेकर **100.0 USD** तक की कीमतों वाले प्रोडक्ट्स हैं।...
- **Matched keywords:** कीमत, प्रोडक्ट
- **Keyword score:** 29%

**tentree#3** | gu | ✅ CONTEXT_AWARE
> Gujarati follow-up about delivery of previously discussed clothing

- **Q1:** તમારા સસ્ટેનેબલ કપડાં વિશે જણાવો
- **A1:** અરે, તમને સસ્ટેનેબલ કપડાં વિશે જાણવામાં રસ છે! અમે Crawl-Tentree પાસે ઘણાં સસ્ટેનેબલ કપડાંના વિકલ્પો છે. અમારી પાસે પુરુષો અને મહિલાઓ માટેના કપડાં ઉપલબ્ધ છે, જેમાં **ટી-શર્ટ**, **સ્વેટર**, **હૂડિ**, *...
- **Q2:** તેની ડિલિવરી કેટલા દિવસમાં થાય છે?
- **A2:** અરે, ડિલિવરી વિશે જાણવા માટે તમે ઉત્સુક છો! અમારી પાસે ડિલિવરીની માહિતી અહીં નથી, પરંતુ તમે Crawl-Tentree ની સત્તાવાર વેબસાઇટ પરથી માહિતી મેળવી શકો છો. ત્યાં તમને ડિલિવરીની વિગતો મળશે....
- **Matched keywords:** ડિલિવરી
- **Keyword score:** 20%


### DEATHWISH

**deathwish#1** | en | ✅ CONTEXT_AWARE
> Follow-up about brewing the previously discussed blend

- **Q1:** What is your strongest coffee blend?
- **A1:** Oh nice, here's what we've got! Our strongest coffee blend is the **Dark Roast Coffee**, which is certified Fair Trade and Organic, and it's available for **$19.99**....
- **Q2:** How should I brew it for the best taste?
- **A2:** To get the best taste out of our **Dark Roast Coffee**, we recommend using a method that brings out its bold and rich flavors. You can try using a French press, pour-over, or even a drip brewer. For a...
- **Matched keywords:** brew, coffee, strong, taste, cup
- **Keyword score:** 83%

**deathwish#2** | hi | ✅ CONTEXT_AWARE
> Hindi follow-up about ordering the previously discussed coffee

- **Q1:** आपकी सबसे पॉपुलर कॉफी कौन सी है?
- **A1:** अरे, बहुत सारे options हैं! देखो Crawl-Death Wish Coffee के पास क्या है। यहाँ कुछ बढ़िया ऑप्शन हैं!...
- **Q2:** क्या मैं इसे ऑनलाइन ऑर्डर कर सकता हूँ?
- **A2:** बिल्कुल! आप हमारी वेबसाइट पर जाकर आसानी से ऑनलाइन ऑर्डर कर सकते हैं। हमारी वेबसाइट पर सभी प्रोडक्ट्स अवेलेबल हैं और आप अपनी पसंद का प्रोडक्ट चुनकर ऑर्डर कर सकते हैं।...
- **Matched keywords:** ऑर्डर, ऑनलाइन
- **Keyword score:** 33%


### BEARDBRAND

**beardbrand#1** | en | ✅ CONTEXT_AWARE
> Follow-up about specific oil recommendation from previous context

- **Q1:** What beard oils do you sell?
- **A1:** Oh nice, here's what we've got! We've got a range of beard oils, including **Bold Fortune Beard Oil** and **Old Money Beard Oil**, that can help prevent beard itch, soothe dry skin, and stop beard dan...
- **Q2:** Which one is best for sensitive skin?
- **A2:** For sensitive skin, I'd recommend checking out our **Beard Oil**, which is formulated with natural ingredients like abyssinian, jojoba, castor, and babassu oils, and is non-comedogenic, making it safe...
- **Matched keywords:** oil, beard, sensitive, skin, recommend
- **Keyword score:** 100%

**beardbrand#2** | gu | ✅ CONTEXT_AWARE
> Gujarati follow-up about best-selling beard product

- **Q1:** તમારા બિયર્ડ પ્રોડક્ટ્સ વિશે જણાવો
- **A1:** અરે, ઘણા સરસ ઓપ્શન છે! જુઓ Crawl-Beardbrand પાસે શું છે....
- **Q2:** કયું સૌથી વધુ વેચાય છે?
- **A2:** ઓહ, સૌથી વધુ વેચાતું પ્રોડક્ટ એ છે **Beard Oil**, જે તમારા બિયર્ડને સોફ્ટ અને સ્વચ્છ રાખવામાં મદદ કરે છે!...
- **Matched keywords:** beard, પ્રોડક્ટ
- **Keyword score:** 33%


### RAMRAJ

**ramraj#1** | en | ✅ CONTEXT_AWARE
> Follow-up about fabric for previously discussed dhotis

- **Q1:** What types of dhotis do you have?
- **A1:** We've got a variety of dhotis to choose from. Check these out!...
- **Q2:** Which fabric is most comfortable in summer?
- **A2:** For summer, I'd say **cotton** is the way to go - it's breathable, lightweight, and absorbent, making it perfect for hot weather....
- **Matched keywords:** cotton, summer
- **Keyword score:** 40%

**ramraj#2** | hi | ✅ CONTEXT_AWARE
> Hindi follow-up asking price of silk dhoti

- **Q1:** क्या आपके पास सिल्क धोती है?
- **A1:** यहाँ कुछ बढ़िया ऑप्शन हैं! हमारे पास सिल्क धोती के कई विकल्प उपलब्ध हैं।...
- **Q2:** इसकी कीमत कितनी है?
- **A2:** यहाँ कीमतें बहुत अच्छी हैं! **Ramraj** की सिल्क धोती की कीमतें **₹1,390.00** से शुरू होती हैं और **₹43,300.00** तक जाती हैं।...
- **Matched keywords:** सिल्क, धोती, कीमत, ₹
- **Keyword score:** 67%


### KRIYANTA

**kriyanta#1** | en | ✅ CONTEXT_AWARE
> Follow-up about ingredients in previously discussed products

- **Q1:** What skincare products do you offer?
- **A1:** We don't have skincare products at kriyanta. We specialize in **handmade, eco-friendly, and customized home decor and gifting products**, like wall art, clocks, wooden temples, metal lamps, decorative...
- **Q2:** Do any of them contain aloe vera?
- **A2:** We don't have any products that contain aloe vera. As a home decor and gifting brand, our products are focused on items like **wall art**, **decorative items**, and **personalized gifts**, rather than...
- **Matched keywords:** skincare, skin, aloe, product
- **Keyword score:** 80%

**kriyanta#2** | gu | ✅ CONTEXT_AWARE
> Gujarati follow-up about dry skin product recommendation

- **Q1:** તમારા સ્કિનકેર પ્રોડક્ટ્સ વિશે જણાવો
- **A1:** અરે, તમને સ્કિનકેર પ્રોડક્ટ્સ વિશે જણાવવા માંગતા હો? દિલખુલાસ થાઓ, અમારી પાસે એવા પ્રોડક્ટ્સ નથી. અમે હોમ ડેકોર અને ગિફ્ટિંગ પ્રોડક્ટ્સ પર ધ્યાન આપીએ છીએ. 
જો તમને હોમ ડેકોર અથવા ગિફ્ટિંગ પ્રોડક્ટ્સ વ...
- **Q2:** કયું ડ્રાય સ્કિન માટે સારું છે?
- **A2:** અરે, ડ્રાય સ્કિન માટે સારું એવું કંઈ નથી જે હું તમને સૂચન કરી શકું. અમે હોમ ડેકોર અને ગિફ્ટિંગ પ્રોડક્ટ્સ પર ધ્યાન આપીએ છીએ, સ્કિનકેર પ્રોડક્ટ્સ પર નહીં. ડ્રાય સ્કિન માટે તમે કોઈ ડર્મેટોલોજિસ્ટ અથવા સ...
- **Matched keywords:** સ્કિન, પ્રોડક્ટ
- **Keyword score:** 40%


### ZEVARAMAZE

**zevaramaze#1** | gu | ✅ CONTEXT_AWARE
> Gujarati follow-up asking price of previously discussed products

- **Q1:** તમારા સૌથી લોકપ્રિય પ્રોડક્ટ્સ કયા છે?
- **A1:** અરે, ઘણા saras options છે! જુઓ zevaramaze પાસે **સ્ટર્લિંગ સિલ્વર જ્વેલરી** છે, જેમાં **પેન્ડન્ટ**, **ઈઅરરિંગ્સ**, **મંગલસૂત્ર**, **રિંગ્સ**, **બ્રેસલેટ્સ**, અને **હૂપ ઈઅરરિંગ્સ** છે. તમને કયો પ્રોડક્...
- **Q2:** તેની કિંમત શું છે?
- **A2:** ઓહ, **પ્રાઇસ** વિશે જાણવા માટે એક સરસ પ્રશ્ન! અમારા **સ્ટર્લિંગ સિલ્વર જ્વેલરી**ની કિંમત **₹2000**થી **₹5000** સુધી છે, પ્રોડક્ટ અને ડિઝાઈન પર આધારિત....
- **Matched keywords:** કિંમત, ₹, પ્રોડક્ટ
- **Keyword score:** 60%


## Interpretation

- **CONTEXT_AWARE**: Follow-up response correctly referenced the previous query's context
- **NO_CONTEXT**: Response showed confusion or asked for clarification (enrichment failed)
- **UNCLEAR**: Could not determine from keywords alone (manual review recommended)
- **RATE_LIMITED**: API rate limit prevented the test
- **SCOPE_GATED**: Query was incorrectly rejected as out-of-scope