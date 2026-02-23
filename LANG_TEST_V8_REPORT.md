# Language Test V8 — Missing Info & Irrelevant Query Report

**Date:** 2026-02-23 11:34

## Purpose
Test how the chatbot handles:
1. **Missing Info** — domain-relevant questions but info not in the knowledge base
2. **Irrelevant** — completely off-topic queries

Expected behaviour:
- **Missing info**: Bot admits it doesn't have the specific info, does NOT hallucinate, suggests contacting support/checking official site.
- **Irrelevant**: Bot politely declines or redirects to its domain, returns 0 products.

## Detailed Results

### Crawl-Tentree
**Domain:** sustainable outdoor/eco clothing (tentree.com)  
**Allowed Languages:** en, hi, gu

| Lang | Type | Query | Response (first 200 chars) | Products | Admits/Declines | Time |
|------|------|-------|----------------------------|----------|--------------------|------|
| en | missing_info | Do you offer custom embroidery or personalisation  | We've got some great options for customization. Check these out! | 3 | ✗ no admission | 5.06s |
| en | irrelevant | Can you recommend the best gaming laptop under $10 | I can only help with Crawl-Tentree products. What are you looking for? | 8 | ✓ declines | 15.3s |
| hi | missing_info | क्या टेंट्री की products पर wholesale discount मिल | Are yaar, wholesale discount ke bare mein toh maine information nahi dhoondhi! Yahan wholesale discount ke bare mein koi details available nahi hai | 10 | ✗ no admission | 10.37s |
| hi | irrelevant | भारत में Bitcoin में invest करने का सबसे अच्छा तरी | अरे, यहाँ बहुत सारे विकल्प हैं! लेकिन मैं आपको बता दूं, मेरे पास इसके बारे में जानकारी नहीं है क्योंकि यह Crawl-Tentree के प्रोडक्ट से संबंधित नहीं है। | 0 | ✓ declines | 4.03s |
| gu | missing_info | ટેન્ટ્રી ઑfline store ભારતમां ક્યા ક્યa city maa c | અરે, ટેન્ટ્રી ની ઑફલાઈન સ્ટોર્સ ભારતમાં ઘણા શહેરોમાં છે! પણ હું તમને ખરી જાણકારી આપી શકતો નથી કે કયા શહેરમાં છે | 0 | ✗ no admission | 3.47s |
| gu | irrelevant | ફૂટboll World Cup 2026 ક્યારe shru thase? | Are, yaar! FIFA World Cup 2026 ni information ahiya nathi — Crawl-Tentree pase su chhe. | 0 | ✗ did not decline | 10.63s |

**Follow-up Suggestions:**

- [en] *Do you offer custom embroidery or personalisation * → ['Can I get a name embroidered on a jacket?', 'Do you offer custom logos for businesses?']
- [en] *Can you recommend the best gaming laptop under $10* → ['What products do you carry?', 'Tell me about Crawl-Tentree']
- [hi] *क्या टेंट्री की products पर wholesale discount मिल* → ['Wholesale ke liye kya process hai?', 'Bulk order par kitna discount milta hai?']
- [hi] *भारत में Bitcoin में invest करने का सबसे अच्छा तरी* → ['Crawl-Tentree के प्रोडक्ट्स देखो', 'क्या आपके पास कोई प्रोडक्ट है जो मुझे पसंद हो?']
- [gu] *ટેન્ટ્રી ઑfline store ભારતમां ક્યા ક્યa city maa c* → ['ટેન્ટ્રી ની ઓફિસિયલ વેબસાઈટ પર શોધો', 'ગૂગલ મેપ્સ પર ટેન્ટ્રી સ્ટોર્સ શોધો']
- [gu] *ફૂટboll World Cup 2026 ક્યારe shru thase?* → ['FIFA World Cup 2026 ni dates shu chhe?', 'Ane World Cup 2026 ma ke team khelase?']

### Crawl-Death Wish Coffee
**Domain:** strong/specialty coffee brand (deathwishcoffee.com)  
**Allowed Languages:** en, hi

| Lang | Type | Query | Response (first 200 chars) | Products | Admits/Declines | Time |
|------|------|-------|----------------------------|----------|--------------------|------|
| en | missing_info | Do you have any decaffeinated coffee options, and  | We've got quite a range of coffee options, but I don't have specific information on decaffeinated coffee options and their prices | 7 | ✓ admits no info | 11.72s |
| en | irrelevant | Which smartphone has the best camera in 2026? | I can only help with Crawl-Death Wish Coffee products. What are you looking for? | 2 | ✓ declines | 9.87s |
| hi | missing_info | क्या आप अपनी coffee beans को bulk order में ship क | Are yaar, hum bulk order mein coffee beans ship karte hain! Lekin minimum quantity ke bare mein mujhe thodi information nahi hai — Crawl-Death Wish Coffee ki bulk order policy ke liye unka website che | 10 | ✗ no admission | 12.05s |
| hi | irrelevant | मुझे अपने बच्चे के लिए अच्छा स्कूल ढूंढना है, सुझा | अरे, यहाँ तो हम स्कूल के बारे में बात नहीं कर रहे हैं! मैं आपको Crawl-Death Wish Coffee के बारे में जानकारी दे सकता हूँ। अगर आपको कॉफी या गिफ्ट आइटम्स के बारे में जानना है, तो मुझे बताएं! | 0 | ✗ did not decline | 10.95s |

**Follow-up Suggestions:**

- [en] *Do you have any decaffeinated coffee options, and * → ['What types of coffee do you offer?', 'Can I see your full coffee collection?']
- [en] *Which smartphone has the best camera in 2026?* → ['What coffee products do you have?', 'Tell me about Crawl-Death Wish Coffee']
- [hi] *क्या आप अपनी coffee beans को bulk order में ship क* → ['Bulk order ke liye kya process hai?', 'Minimum quantity kitni hai?']
- [hi] *मुझे अपने बच्चे के लिए अच्छा स्कूल ढूंढना है, सुझा* → ['Crawl-Death Wish Coffee की कीमत क्या है?', 'कॉफी के प्रकार क्या हैं?']

### Crawl-Beardbrand
**Domain:** beard grooming & men's care (beardbrand.com)  
**Allowed Languages:** en, gu

| Lang | Type | Query | Response (first 200 chars) | Products | Admits/Declines | Time |
|------|------|-------|----------------------------|----------|--------------------|------|
| en | missing_info | Do you have a loyalty or rewards programme for rep | Oh nice! We don't have any info on a loyalty or rewards program for repeat customers in our current context, so I don't have that information | 0 | ✓ admits no info | 11.24s |
| en | irrelevant | What are the best stocks to invest in right now? | I can only help with Crawl-Beardbrand products. What are you looking for? | 0 | ✓ declines | 11.8s |
| gu | missing_info | શું beardbrand ની products India maa deliver thay  | Are, Crawl-Beardbrand ni products India ma deliver thase che! | 10 | ✗ no admission | 10.93s |
| gu | irrelevant | ક્રિકેટ World Cup 2026 ક્યા દેshma রাখবে? | અરે, આ વાત તો ક્રિકેટ વિશ્વની છે! પણ મારી પાસે તેની માહિતી નથી — Crawl-Beardbrand ને લગતી માહિતી જ મળશે. | 0 | ✗ did not decline | 3.47s |

**Follow-up Suggestions:**

- [en] *Do you have a loyalty or rewards programme for rep* → ['What are your best-selling items?', 'Do you offer any discounts for bulk orders?']
- [en] *What are the best stocks to invest in right now?* → ['What products do you carry?', 'Tell me about Crawl-Beardbrand']
- [gu] *શું beardbrand ની products India maa deliver thay * → ['India ma delivery charge shu chhe?', 'International shipping available chhe?']
- [gu] *ક્રિકેટ World Cup 2026 ક્યા દેshma রাখবে?* → ['Crawl-Beardbrand ની નવી પ્રોડક્ટ શું છે?', 'તમારી પાસે કેટલી બેસ્ટ સેલર છે?']

### ramraj
**Domain:** Indian cotton traditional wear (ramraj.in)  
**Allowed Languages:** hi, gu

| Lang | Type | Query | Response (first 200 chars) | Products | Admits/Declines | Time |
|------|------|-------|----------------------------|----------|--------------------|------|
| hi | missing_info | क्या रामराज की wedding collection पर custom tailor | Are yaar, ramraj ki wedding collection mein custom tailoring ka option hai, lekin yahan details nahi hain | 10 | ✗ no admission | 11.77s |
| hi | irrelevant | मुझे Python programming सीखनी है, कहाँ से शुरू करू | ओह, पाइथन प्रोग्रामिंग सीखने का फैसला बहुत अच्छा है! लेकिन मैं ramraj का एक शॉपिंग असिस्टेंट हूँ, प्रोग्रामिंग के बारे में जानकारी मेरे पास नहीं है। | 0 | ✗ did not decline | 11.76s |
| gu | missing_info | રામRaj Cotton ની products international delivery t | Ahiya, ramraj cotton ni products international delivery thay che, lekin ahiya details nathi — ramraj ne directly contact karo. | 10 | ✓ admits no info | 12.77s |
| gu | irrelevant | adsense se paisa kamava na tips apo. | Oh nice! Adsense se paisa kamane ke liye aapko traffic badhana hoga aur relevant ads lagane honge. | 1 | ✗ did not decline | 10.85s |

**Follow-up Suggestions:**

- [hi] *क्या रामराज की wedding collection पर custom tailor* → ['Custom tailoring ke liye kitna time lagta hai?', 'Kya custom tailoring ke liye extra charge hota hai?']
- [hi] *मुझे Python programming सीखनी है, कहाँ से शुरू करू* → ['आपके पास क्या products हैं?', 'ramraj की खासियत क्या है?']
- [gu] *રામRaj Cotton ની products international delivery t* → ['International shipping charges kayi chhe?', 'Aa product export thay che?']
- [gu] *adsense se paisa kamava na tips apo.* → ['Adsense ke liye website kaise banaye?', 'Traffic badhane ke liye kya kare?']

### kriyanta
**Domain:** handmade home décor & gifting (kriyanta.com)  
**Allowed Languages:** hi

| Lang | Type | Query | Response (first 200 chars) | Products | Admits/Declines | Time |
|------|------|-------|----------------------------|----------|--------------------|------|
| hi | missing_info | क्या आपके पास corporate bulk gifting के लिए specia | Are yaar, corporate bulk gifting ke liye special discount aur minimum order quantity ke baare mein mujhe information nahi hai | 9 | ✗ no admission | 10.8s |
| hi | irrelevant | मुझे अच्छा DSLR camera चाहिए under ₹30000, कौनसा ल | यहाँ कुछ बढ़िया ऑप्शन हैं! हमारे पास ₹30000 के अंदर कई अच्छे DSLR कैमरे हैं, जिनमें से आप अपनी जरूरत के हिसाब से चुन सकते हैं। | 10 | ✗ did not decline | 11.06s |

**Follow-up Suggestions:**

- [hi] *क्या आपके पास corporate bulk gifting के लिए specia* → ['Corporate gifting ke liye kya options hain?', 'Bulk order pe kitna discount milta hai?']
- [hi] *मुझे अच्छा DSLR camera चाहिए under ₹30000, कौनसा ल* → ['इनमें से सबसे अच्छा कौनसा है?', 'क्या इनमें से कोई वीडियो रिकॉर्डिंग के लिए अच्छा है?']

### zevaramaze
**Domain:** handmade silver jewellery (zevaramaze.com)  
**Allowed Languages:** gu

| Lang | Type | Query | Response (first 200 chars) | Products | Admits/Declines | Time |
|------|------|-------|----------------------------|----------|--------------------|------|
| gu | missing_info | ઝેવારામઝ ઘреणа international courier service thi m | Are, ahiya international courier service thi mangavu shay che, pan ahiya custom design banana ni details nathi. Custom design charge ahiya nathi, direct zevaramaze contact karo. | 10 | ✓ admits no info | 11.54s |
| gu | irrelevant | Weight ઘtaavaanu saukathi sarlu upay shu che? | Are, weight ghataavva nu saukathi sarlu upay to su chhe!  Tamaru diet ni saaf safai rakhvu, regular exercise karvu, aur pani khub piyu.  - Niyamit yoga aur walking karvu  - Junk food ni jagya fruits a | 0 | ✗ did not decline | 2.47s |

**Follow-up Suggestions:**

- [gu] *ઝેવારામઝ ઘреणа international courier service thi m* → ['Custom design kevi rite banavu?', 'International shipping charge shu chhe?']
- [gu] *Weight ઘtaavaanu saukathi sarlu upay shu che?* → ['Diet chart batavo', 'Exercise routine shu chhe?']

## Issues Found

**Total: 37 issues**

1. **[Crawl-Tentree][en][missing_info]** `Do you offer custom embroidery or personalisation on jackets` — Bot responded confidently without admitting missing info. Response: «We've got some great options for customization. Check these out!»
2. **[Crawl-Tentree][en][missing_info]** `Do you offer custom embroidery or personalisation on jackets` — Missing-info query returned 3 product cards — may be hallucinating products for unanswerable query
3. **[Crawl-Tentree][en][irrelevant]** `Can you recommend the best gaming laptop under $1000?` — Irrelevant query returned 8 product cards — products should not appear for off-topic queries
4. **[Crawl-Tentree][hi][missing_info]** `क्या टेंट्री की products पर wholesale discount मिलती है?` — Language mismatch: query=hi, response detected as en
5. **[Crawl-Tentree][hi][missing_info]** `क्या टेंट्री की products पर wholesale discount मिलती है?` — Bot responded confidently without admitting missing info. Response: «Are yaar, wholesale discount ke bare mein toh maine information nahi dhoondhi! Yahan wholesale discount ke bare mein koi»
6. **[Crawl-Tentree][hi][missing_info]** `क्या टेंट्री की products पर wholesale discount मिलती है?` — Missing-info query returned 10 product cards — may be hallucinating products for unanswerable query
7. **[Crawl-Tentree][gu][missing_info]** `ટેન્ટ્રી ઑfline store ભારતમां ક્યા ક્યa city maa che?` — Bot responded confidently without admitting missing info. Response: «અરે, ટેન્ટ્રી ની ઑફલાઈન સ્ટોર્સ ભારતમાં ઘણા શહેરોમાં છે! પણ હું તમને ખરી જાણકારી આપી શકતો નથી કે કયા શહેરમાં છે»
8. **[Crawl-Tentree][gu][irrelevant]** `ફૂટboll World Cup 2026 ક્યારe shru thase?` — Language mismatch: query=gu, response detected as en
9. **[Crawl-Tentree][gu][irrelevant]** `ફૂટboll World Cup 2026 ક્યારe shru thase?` — Bot did NOT decline irrelevant query. Response: «Are, yaar! FIFA World Cup 2026 ni information ahiya nathi — Crawl-Tentree pase su chhe.»
10. **[Crawl-Death Wish Coffee][en][missing_info]** `Do you have any decaffeinated coffee options, and what are t` — Missing-info query returned 7 product cards — may be hallucinating products for unanswerable query
11. **[Crawl-Death Wish Coffee][en][irrelevant]** `Which smartphone has the best camera in 2026?` — Irrelevant query returned 2 product cards — products should not appear for off-topic queries
12. **[Crawl-Death Wish Coffee][hi][missing_info]** `क्या आप अपनी coffee beans को bulk order में ship करते हैं? m` — Language mismatch: query=hi, response detected as en
13. **[Crawl-Death Wish Coffee][hi][missing_info]** `क्या आप अपनी coffee beans को bulk order में ship करते हैं? m` — Bot responded confidently without admitting missing info. Response: «Are yaar, hum bulk order mein coffee beans ship karte hain! Lekin minimum quantity ke bare mein mujhe thodi information »
14. **[Crawl-Death Wish Coffee][hi][missing_info]** `क्या आप अपनी coffee beans को bulk order में ship करते हैं? m` — Missing-info query returned 10 product cards — may be hallucinating products for unanswerable query
15. **[Crawl-Death Wish Coffee][hi][irrelevant]** `मुझे अपने बच्चे के लिए अच्छा स्कूल ढूंढना है, सुझाव दो।` — Bot did NOT decline irrelevant query. Response: «अरे, यहाँ तो हम स्कूल के बारे में बात नहीं कर रहे हैं! मैं आपको Crawl-Death Wish Coffee के बारे में जानकारी दे सकता हूँ।»
16. **[Crawl-Beardbrand][gu][missing_info]** `શું beardbrand ની products India maa deliver thay che?` — Language mismatch: query=gu, response detected as en
17. **[Crawl-Beardbrand][gu][missing_info]** `શું beardbrand ની products India maa deliver thay che?` — Bot responded confidently without admitting missing info. Response: «Are, Crawl-Beardbrand ni products India ma deliver thase che!»
18. **[Crawl-Beardbrand][gu][missing_info]** `શું beardbrand ની products India maa deliver thay che?` — Missing-info query returned 10 product cards — may be hallucinating products for unanswerable query
19. **[Crawl-Beardbrand][gu][irrelevant]** `ક્રિકેટ World Cup 2026 ક્યા દેshma রাখবে?` — Bot did NOT decline irrelevant query. Response: «અરે, આ વાત તો ક્રિકેટ વિશ્વની છે! પણ મારી પાસે તેની માહિતી નથી — Crawl-Beardbrand ને લગતી માહિતી જ મળશે.»
20. **[ramraj][hi][missing_info]** `क्या रामराज की wedding collection पर custom tailoring का opt` — Language mismatch: query=hi, response detected as en
21. **[ramraj][hi][missing_info]** `क्या रामराज की wedding collection पर custom tailoring का opt` — Bot responded confidently without admitting missing info. Response: «Are yaar, ramraj ki wedding collection mein custom tailoring ka option hai, lekin yahan details nahi hain»
22. **[ramraj][hi][missing_info]** `क्या रामराज की wedding collection पर custom tailoring का opt` — Missing-info query returned 10 product cards — may be hallucinating products for unanswerable query
23. **[ramraj][hi][irrelevant]** `मुझे Python programming सीखनी है, कहाँ से शुरू करूँ?` — Bot did NOT decline irrelevant query. Response: «ओह, पाइथन प्रोग्रामिंग सीखने का फैसला बहुत अच्छा है! लेकिन मैं ramraj का एक शॉपिंग असिस्टेंट हूँ, प्रोग्रामिंग के बारे म»
24. **[ramraj][gu][missing_info]** `રામRaj Cotton ની products international delivery thay che?` — Language mismatch: query=gu, response detected as en
25. **[ramraj][gu][missing_info]** `રામRaj Cotton ની products international delivery thay che?` — Missing-info query returned 10 product cards — may be hallucinating products for unanswerable query
26. **[ramraj][gu][irrelevant]** `adsense se paisa kamava na tips apo.` — Language mismatch: query=gu, response detected as en
27. **[ramraj][gu][irrelevant]** `adsense se paisa kamava na tips apo.` — Bot did NOT decline irrelevant query. Response: «Oh nice! Adsense se paisa kamane ke liye aapko traffic badhana hoga aur relevant ads lagane honge.»
28. **[ramraj][gu][irrelevant]** `adsense se paisa kamava na tips apo.` — Irrelevant query returned 1 product cards — products should not appear for off-topic queries
29. **[kriyanta][hi][missing_info]** `क्या आपके पास corporate bulk gifting के लिए special discount` — Language mismatch: query=hi, response detected as en
30. **[kriyanta][hi][missing_info]** `क्या आपके पास corporate bulk gifting के लिए special discount` — Bot responded confidently without admitting missing info. Response: «Are yaar, corporate bulk gifting ke liye special discount aur minimum order quantity ke baare mein mujhe information nah»
31. **[kriyanta][hi][missing_info]** `क्या आपके पास corporate bulk gifting के लिए special discount` — Missing-info query returned 9 product cards — may be hallucinating products for unanswerable query
32. **[kriyanta][hi][irrelevant]** `मुझे अच्छा DSLR camera चाहिए under ₹30000, कौनसा लूं?` — Bot did NOT decline irrelevant query. Response: «यहाँ कुछ बढ़िया ऑप्शन हैं! हमारे पास ₹30000 के अंदर कई अच्छे DSLR कैमरे हैं, जिनमें से आप अपनी जरूरत के हिसाब से चुन सकत»
33. **[kriyanta][hi][irrelevant]** `मुझे अच्छा DSLR camera चाहिए under ₹30000, कौनसा लूं?` — Irrelevant query returned 10 product cards — products should not appear for off-topic queries
34. **[zevaramaze][gu][missing_info]** `ઝેવારામઝ ઘреणа international courier service thi mangavi sha` — Language mismatch: query=gu, response detected as en
35. **[zevaramaze][gu][missing_info]** `ઝેવારામઝ ઘреणа international courier service thi mangavi sha` — Missing-info query returned 10 product cards — may be hallucinating products for unanswerable query
36. **[zevaramaze][gu][irrelevant]** `Weight ઘtaavaanu saukathi sarlu upay shu che?` — Language mismatch: query=gu, response detected as en
37. **[zevaramaze][gu][irrelevant]** `Weight ઘtaavaanu saukathi sarlu upay shu che?` — Bot did NOT decline irrelevant query. Response: «Are, weight ghataavva nu saukathi sarlu upay to su chhe! 
Tamaru diet ni saaf safai rakhvu, regular exercise karvu, aur »

## Strengths

**Total: 23 strengths**

| Bot | Lang | Type | Query | Strength |
|-----|------|------|-------|----------|
| Crawl-Tentree | en | irrelevant | Can you recommend the best gaming laptop | Bot correctly declined / redirected off-topic query ✓ |
| Crawl-Tentree | hi | irrelevant | भारत में Bitcoin में invest करने का सबसे | Replied in correct language (hi) ✓ |
| Crawl-Tentree | hi | irrelevant | भारत में Bitcoin में invest करने का सबसे | Bot correctly declined / redirected off-topic query ✓ |
| Crawl-Tentree | hi | irrelevant | भारत में Bitcoin में invest करने का सबसे | No product cards for irrelevant query ✓ |
| Crawl-Tentree | gu | missing_info | ટેન્ટ્રી ઑfline store ભારતમां ક્યા ક્યa  | Replied in correct language (gu) ✓ |
| Crawl-Tentree | gu | missing_info | ટેન્ટ્રી ઑfline store ભારતમां ક્યા ક્યa  | No spurious product cards for missing-info query ✓ |
| Crawl-Tentree | gu | irrelevant | ફૂટboll World Cup 2026 ક્યારe shru thase | No product cards for irrelevant query ✓ |
| Crawl-Death Wish Coffee | en | missing_info | Do you have any decaffeinated coffee opt | Bot admitted limited info / suggested contacting support ✓ |
| Crawl-Death Wish Coffee | en | irrelevant | Which smartphone has the best camera in  | Bot correctly declined / redirected off-topic query ✓ |
| Crawl-Death Wish Coffee | hi | irrelevant | मुझे अपने बच्चे के लिए अच्छा स्कूल ढूंढन | Replied in correct language (hi) ✓ |
| Crawl-Death Wish Coffee | hi | irrelevant | मुझे अपने बच्चे के लिए अच्छा स्कूल ढूंढन | No product cards for irrelevant query ✓ |
| Crawl-Beardbrand | en | missing_info | Do you have a loyalty or rewards program | Bot admitted limited info / suggested contacting support ✓ |
| Crawl-Beardbrand | en | missing_info | Do you have a loyalty or rewards program | No spurious product cards for missing-info query ✓ |
| Crawl-Beardbrand | en | irrelevant | What are the best stocks to invest in ri | Bot correctly declined / redirected off-topic query ✓ |
| Crawl-Beardbrand | en | irrelevant | What are the best stocks to invest in ri | No product cards for irrelevant query ✓ |
| Crawl-Beardbrand | gu | irrelevant | ક્રિકેટ World Cup 2026 ક્યા દેshma রাখবে | Replied in correct language (gu) ✓ |
| Crawl-Beardbrand | gu | irrelevant | ક્રિકેટ World Cup 2026 ક્યા દેshma রাখবে | No product cards for irrelevant query ✓ |
| ramraj | hi | irrelevant | मुझे Python programming सीखनी है, कहाँ स | Replied in correct language (hi) ✓ |
| ramraj | hi | irrelevant | मुझे Python programming सीखनी है, कहाँ स | No product cards for irrelevant query ✓ |
| ramraj | gu | missing_info | રામRaj Cotton ની products international  | Bot admitted limited info / suggested contacting support ✓ |
| kriyanta | hi | irrelevant | मुझे अच्छा DSLR camera चाहिए under ₹3000 | Replied in correct language (hi) ✓ |
| zevaramaze | gu | missing_info | ઝેવારામઝ ઘреणа international courier ser | Bot admitted limited info / suggested contacting support ✓ |
| zevaramaze | gu | irrelevant | Weight ઘtaavaanu saukathi sarlu upay shu | No product cards for irrelevant query ✓ |

## Improvement Suggestions

### 3. Product Cards Returned for Non-Product Queries (affects: Crawl-Beardbrand, Crawl-Death Wish Coffee, Crawl-Tentree, kriyanta, ramraj, zevaramaze)
- **Problem:** Product cards appear for queries that should return no products.
- **Fix:** Tighter Call1 product classification (recently improved), and ensure blog/info pages are excluded from product extraction (recently fixed with `/blogs?/` pattern).

### 4. General Recommendations
- Add a section in the system prompt: "When you don't have the exact information, say so clearly and direct the user to the official website or customer support."
- For irrelevant queries, consider adding a hard-coded domain description check in the out-of-scope detection logic so it triggers for clearly unrelated topics even at higher confidence.
- Consider logging which queries triggered missing-info vs out-of-scope paths for analytics.

## Raw Results
See `lang_test_v8_raw.json` for complete response data.
