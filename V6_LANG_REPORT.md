# V6 Language Compliance Test Report

**Generated:** 2026-02-22 18:25:19  
**Scope:** Language / script matching across 3 chatbot(s)

## Overall Summary

| Metric | Value |
|--------|-------|
| Queries tested | 152 |
| PASS | 134 (88.2%) |
| FAIL | 18 |
| Rate-limited (skipped) | 0 |

## Per-Bot Breakdown

### Crawl-Tentree

- Tested: 52 &nbsp; Pass: 41 (78.8%) &nbsp; Fail: 11

| Expected Script | Tested | Pass | Fail | Pass% |
|----------------|--------|------|------|-------|
| `devanagari` | 15 | 7 | 8 | 46.7% |
| `gujarati` | 13 | 10 | 3 | 76.9% |
| `latin` | 24 | 24 | 0 | 100.0% |

| Query Type | Tested | Pass | Fail |
|-----------|--------|------|------|
| `continuation_native` | 2 | 1 | 1 |
| `continuation_romanized` | 2 | 2 | 0 |
| `emoji_with_native` | 2 | 2 | 0 |
| `emoji_with_romanized` | 2 | 2 | 0 |
| `english_rejection` | 3 | 0 | 3 |
| `mixed_lang_heavy_native` | 2 | 0 | 2 |
| `mixed_romanized_english` | 2 | 2 | 0 |
| `native_contact_query` | 1 | 0 | 1 |
| `native_irrelevant` | 2 | 1 | 1 |
| `native_missing_info` | 2 | 1 | 1 |
| `native_policy_query` | 2 | 2 | 0 |
| `native_price_query` | 2 | 2 | 0 |
| `native_product_query` | 2 | 1 | 1 |
| `native_script_greeting` | 2 | 2 | 0 |
| `question_native_complex` | 2 | 2 | 0 |
| `question_romanized_complex` | 2 | 2 | 0 |
| `romanized_greeting` | 2 | 2 | 0 |
| `romanized_irrelevant` | 2 | 2 | 0 |
| `romanized_missing_info` | 2 | 2 | 0 |
| `romanized_policy_query` | 2 | 2 | 0 |
| `romanized_price_query` | 2 | 2 | 0 |
| `romanized_product_query` | 2 | 2 | 0 |
| `short_followup_native` | 2 | 2 | 0 |
| `short_followup_romanized` | 2 | 2 | 0 |
| `single_word_native` | 2 | 1 | 1 |
| `single_word_romanized` | 2 | 2 | 0 |

### zevaramaze

- Tested: 50 &nbsp; Pass: 44 (88.0%) &nbsp; Fail: 6

| Expected Script | Tested | Pass | Fail | Pass% |
|----------------|--------|------|------|-------|
| `devanagari` | 18 | 12 | 6 | 66.7% |
| `latin` | 32 | 32 | 0 | 100.0% |

| Query Type | Tested | Pass | Fail |
|-----------|--------|------|------|
| `complex_english` | 1 | 1 | 0 |
| `complex_native` | 1 | 1 | 0 |
| `complex_romanized` | 1 | 1 | 0 |
| `continuation_en` | 1 | 1 | 0 |
| `continuation_hi` | 1 | 0 | 1 |
| `continuation_hi_latn` | 1 | 1 | 0 |
| `emoji_english` | 1 | 1 | 0 |
| `emoji_native` | 1 | 1 | 0 |
| `emoji_romanized` | 1 | 1 | 0 |
| `english_after_hindi` | 1 | 1 | 0 |
| `english_context` | 1 | 1 | 0 |
| `english_greeting` | 1 | 1 | 0 |
| `english_irrelevant` | 1 | 1 | 0 |
| `english_missing_info` | 1 | 1 | 0 |
| `english_policy` | 1 | 1 | 0 |
| `english_price` | 1 | 1 | 0 |
| `english_product` | 1 | 1 | 0 |
| `english_product_detailed` | 1 | 1 | 0 |
| `gujarati_rejection` | 1 | 1 | 0 |
| `hindi_context_word` | 1 | 1 | 0 |
| `hindi_sentiment_check` | 1 | 0 | 1 |
| `language_switch_en_to_hi` | 1 | 1 | 0 |
| `language_switch_hi_latin` | 1 | 1 | 0 |
| `mixed_hindi_english` | 1 | 1 | 0 |
| `mixed_romanized_english` | 1 | 1 | 0 |
| `native_greeting` | 1 | 1 | 0 |
| `native_irrelevant_hi` | 1 | 1 | 0 |
| `native_missing_info` | 1 | 1 | 0 |
| `native_policy_hi` | 1 | 0 | 1 |
| `native_price_hi` | 1 | 1 | 0 |
| `native_product_detailed` | 1 | 1 | 0 |
| `native_product_hi` | 1 | 1 | 0 |
| `number_in_native` | 1 | 1 | 0 |
| `number_in_romanized` | 1 | 1 | 0 |
| `pure_devanagari` | 1 | 0 | 1 |
| `romanized_context` | 1 | 1 | 0 |
| `romanized_greeting` | 1 | 1 | 0 |
| `romanized_irrelevant` | 1 | 1 | 0 |
| `romanized_missing_info` | 1 | 1 | 0 |
| `romanized_policy_hi` | 1 | 1 | 0 |
| `romanized_price_hi` | 1 | 1 | 0 |
| `romanized_product_detail` | 1 | 1 | 0 |
| `romanized_product_hi` | 1 | 1 | 0 |
| `romanized_sentiment` | 1 | 1 | 0 |
| `short_english` | 1 | 1 | 0 |
| `short_native` | 1 | 0 | 1 |
| `short_romanized` | 1 | 1 | 0 |
| `unsupported_lang_gu` | 1 | 0 | 1 |
| `unsupported_lang_native` | 1 | 1 | 0 |
| `whatsapp_style_hi` | 1 | 1 | 0 |

### kriyanta

- Tested: 50 &nbsp; Pass: 49 (98.0%) &nbsp; Fail: 1

| Expected Script | Tested | Pass | Fail | Pass% |
|----------------|--------|------|------|-------|
| `gujarati` | 17 | 16 | 1 | 94.1% |
| `latin` | 33 | 33 | 0 | 100.0% |

| Query Type | Tested | Pass | Fail |
|-----------|--------|------|------|
| `complex_english` | 1 | 1 | 0 |
| `complex_native_gu` | 1 | 1 | 0 |
| `complex_romanized_gu` | 1 | 1 | 0 |
| `continuation_en` | 1 | 1 | 0 |
| `continuation_gu` | 1 | 1 | 0 |
| `continuation_gu_latn` | 1 | 1 | 0 |
| `emoji_english` | 1 | 1 | 0 |
| `emoji_native_gu` | 1 | 1 | 0 |
| `emoji_romanized_gu` | 1 | 1 | 0 |
| `english_context` | 1 | 1 | 0 |
| `english_gift_idea` | 1 | 1 | 0 |
| `english_greeting` | 1 | 1 | 0 |
| `english_irrelevant` | 1 | 1 | 0 |
| `english_missing_info` | 1 | 1 | 0 |
| `english_policy` | 1 | 1 | 0 |
| `english_price` | 1 | 1 | 0 |
| `english_product` | 1 | 1 | 0 |
| `english_product_detail` | 1 | 1 | 0 |
| `gujarati_context` | 1 | 1 | 0 |
| `gujarati_gift_query` | 1 | 1 | 0 |
| `hindi_rejection` | 1 | 1 | 0 |
| `mixed_gu_english` | 1 | 1 | 0 |
| `mixed_romanized_english` | 1 | 1 | 0 |
| `native_greeting_gu` | 1 | 1 | 0 |
| `native_irrelevant_gu` | 1 | 1 | 0 |
| `native_missing_gu` | 1 | 0 | 1 |
| `native_policy_gu` | 1 | 1 | 0 |
| `native_price_gu` | 1 | 1 | 0 |
| `native_product_detail` | 1 | 1 | 0 |
| `native_product_gu` | 1 | 1 | 0 |
| `number_in_native_gu` | 1 | 1 | 0 |
| `number_in_romanized_gu` | 1 | 1 | 0 |
| `pure_gujarati` | 1 | 1 | 0 |
| `romanized_context` | 1 | 1 | 0 |
| `romanized_gift_query` | 1 | 1 | 0 |
| `romanized_greeting_gu` | 1 | 1 | 0 |
| `romanized_irrelevant_gu` | 1 | 1 | 0 |
| `romanized_missing_gu` | 1 | 1 | 0 |
| `romanized_policy_gu` | 1 | 1 | 0 |
| `romanized_price_gu` | 1 | 1 | 0 |
| `romanized_product_detail` | 1 | 1 | 0 |
| `romanized_product_gu` | 1 | 1 | 0 |
| `sentiment_native_gu` | 1 | 1 | 0 |
| `sentiment_romanized_gu` | 1 | 1 | 0 |
| `short_english` | 1 | 1 | 0 |
| `short_native_gu` | 1 | 1 | 0 |
| `short_romanized_gu` | 1 | 1 | 0 |
| `unsupported_french` | 1 | 1 | 0 |
| `unsupported_hindi_native` | 1 | 1 | 0 |
| `whatsapp_style_gu` | 1 | 1 | 0 |

## Failed Queries — Detail

| ID | Bot | Lang | Expected | Detected | Query | Response snippet |
|----|-----|------|----------|----------|-------|-----------------|
| T-L05 | Crawl-Tentree | `hi` | `devanagari` | `latin` | कोई टी-शर्ट दिखाओ | Are! Maine aapke liye kuch badhiya options khoje hain!   |
| T-L17 | Crawl-Tentree | `hi` | `devanagari` | `latin` | क्या आपके पास नीली जीन्स है? | Sorry, return policy ke baare mein yahan koi specific jaanka |
| T-L21 | Crawl-Tentree | `hi` | `devanagari` | `latin` | भारत के प्रधानमंत्री कौन हैं? | Main sirf Crawl-Tentree ke products ke baare mein help kar s |
| T-L25 | Crawl-Tentree | `en` | `devanagari` | `devanagari` | Show me your jackets | यहाँ कुछ बढ़िया ऑप्शन हैं! Crawl-Tentree के पास हर मौसम के ल |
| T-L26 | Crawl-Tentree | `en` | `devanagari` | `latin` | What is your return policy? | Hmm, I don't have that information in my current knowledge b |
| T-L27 | Crawl-Tentree | `en` | `gujarati` | `devanagari` | Do you have sustainable clothing? | मैंने ये आपके लिए खोजे! Crawl-Tentree के पास टिकाऊ और पृथ्वी |
| T-L29 | Crawl-Tentree | `gu` | `gujarati` | `devanagari` | jackets | यहाँ कुछ बढ़िया ऑप्शन हैं! Crawl-Tentree के पास पुरुषों और म |
| T-L32 | Crawl-Tentree | `hi` | `devanagari` | `latin` | मुझे eco-friendly jacket चाहिए | Yahan kuch badhiya options hain! Crawl-Tentree ke paas aapke |
| T-L33 | Crawl-Tentree | `gu` | `gujarati` | `latin` | મને eco-friendly jacket જોઈએ | Me tamara mate aa shodhya! Crawl-Tentree pase eco-friendly j |
| T-L36 | Crawl-Tentree | `hi` | `devanagari` | `latin` | इनमें से सबसे अच्छा कौन सा है? | Hmm, "sabse achha" toh aapki zaroorat par depend karta hai!  |
| T-L52 | Crawl-Tentree | `hi` | `devanagari` | `latin` | आपका फ़ोन नंबर क्या है? | Sorry, phone number ni mahiti aa samaye uplabdh nathi.  |
| Z-L15 | zevaramaze | `hi` | `devanagari` | `latin` | वापसी नीति क्या है? | Sorry, I don't have that information.  |
| Z-L28 | zevaramaze | `hi` | `devanagari` | `latin` | चांदी के गहने कितने महंगे हैं? | Are, silver jewelry ke price ke baare mein pooch rahe ho? Ya |
| Z-L29 | zevaramaze | `hi` | `devanagari` | `latin` | अंगूठी | Oh, aapko anguthi (ring) chahiye! Zevaramaze mein bahut hi k |
| Z-L32 | zevaramaze | `hi` | `devanagari` | `latin` | इनमें से सबसे पॉपुलर कौन सा है? | Hmm, sabse popular product ka pata karna mushkil hai, par ji |
| Z-L46 | zevaramaze | `hi` | `devanagari` | `latin` | बहुत अच्छा! और क्या है? | In par ek nazar daaliye!  |
| Z-L48 | zevaramaze | `gu` | `devanagari` | `latin` | oo chhe kya? | Oh, aapko lagta hai ki ye hai? Hmm, main check karti hoon. K |
| K-L18 | kriyanta | `gu` | `gujarati` | `latin` | કસ્ટમ ડિઝાઇન ઓર્ડર કરી શકાય? | Sure! You can definitely order custom designs.   |

## Root Cause Analysis

### Issues found

- **`english_rejection`** → 3 failures
- **`mixed_lang_heavy_native`** → 2 failures
- **`native_product_query`** → 1 failures
- **`native_missing_info`** → 1 failures
- **`native_irrelevant`** → 1 failures
- **`single_word_native`** → 1 failures
- **`continuation_native`** → 1 failures
- **`native_contact_query`** → 1 failures
- **`native_policy_hi`** → 1 failures
- **`pure_devanagari`** → 1 failures
- **`short_native`** → 1 failures
- **`continuation_hi`** → 1 failures
- **`hindi_sentiment_check`** → 1 failures
- **`unsupported_lang_gu`** → 1 failures
- **`native_missing_gu`** → 1 failures

### Native Script Issues

11 native-script queries failed to receive correct-script responses.
Possible causes:
- Call 1 misclassified the language
- System prompt language instruction was not followed

## Recommendations

1. **Reinforce language instruction** — Repeat the critical language rule in the last line of the system prompt (recency bias).
2. **Romanized detection accuracy** — Expand the Call 1 few-shot examples with clear romanized Hindi/Gujarati samples.
3. **Script detection logging** — Log detected vs expected script per response to monitor ongoing compliance.
4. **Temperature reduction for hi-Latn** — Use temperature=0 for romanized language generation to reduce hallucination of wrong script.
5. **Post-processing check** — After Call 2, verify response script matches request; if mismatch, trigger a re-generation with stricter prompt.
