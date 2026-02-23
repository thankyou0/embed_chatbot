import json, sys
sys.stdout.reconfigure(encoding='utf-8')

BOTS_TO_TEST = [
    {'name': 'ramraj', 'set_languages': ['en', 'gu'], 'products': ['shirts', 'dhotis', 'cotton shirts', 'formal shirts', 'kurta']},
    {'name': 'kriyanta', 'set_languages': ['en', 'gu'], 'products': ['services', 'solutions', 'web development', 'app development']},
    {'name': 'zevaramaze', 'set_languages': ['en', 'hi', 'gu'], 'products': ['bracelets', 'necklaces', 'rings', 'earrings', 'pendants']},
    {'name': 'beardbrand', 'set_languages': ['en'], 'products': ['beard oil', 'beard balm', 'utility balm', 'grooming kit', 'wash']},
    {'name': 'deathwish', 'set_languages': ['en', 'hi'], 'products': ['coffee', 'ground coffee', 'K-cups', 'death cups', 'cold brew']},
    {'name': 'tentree', 'set_languages': ['en', 'gu'], 'products': ['t-shirts', 'hoodies', 'joggers', 'jackets', 'sweaters']},
]

def build_queries_for_bot(bot):
    langs = bot['set_languages']
    p = bot['products']
    name = bot['name']
    queries = []
    has_en = 'en' in langs
    has_hi = 'hi' in langs
    has_gu = 'gu' in langs

    # 1. GREETINGS
    if has_en:
        queries.append({'type': 'greeting', 'lang': 'en', 'query': 'Hi there!'})
        queries.append({'type': 'greeting', 'lang': 'en', 'query': "Hey, what's up?"})
        queries.append({'type': 'greeting', 'lang': 'en', 'query': 'Good morning! Can you help me?'})
    if has_hi:
        queries.append({'type': 'greeting', 'lang': 'hi', 'query': 'नमस्ते!'})
        queries.append({'type': 'greeting', 'lang': 'hi', 'query': 'हेलो, कैसे हो?'})
    if has_gu:
        queries.append({'type': 'greeting', 'lang': 'gu', 'query': 'નમસ્તે! કેમ છો?'})
        queries.append({'type': 'greeting', 'lang': 'gu', 'query': 'હેલો! મને હેલ્પ કરો'})

    # 2. PRODUCT BROWSING
    if has_en:
        queries.append({'type': 'product_browse', 'lang': 'en', 'query': f'Show me your {p[0]}'})
        queries.append({'type': 'product_browse', 'lang': 'en', 'query': f'What {p[1]} do you have?'})
        queries.append({'type': 'product_browse', 'lang': 'en', 'query': 'I want to browse your collection'})
        queries.append({'type': 'product_browse', 'lang': 'en', 'query': "What's popular right now?"})
        queries.append({'type': 'product_browse', 'lang': 'en', 'query': 'Show me your best sellers'})
    if has_hi:
        queries.append({'type': 'product_browse', 'lang': 'hi', 'query': f'आपके पास कौन से {p[0]} हैं?'})
        queries.append({'type': 'product_browse', 'lang': 'hi', 'query': f'मुझे {p[1]} दिखाओ'})
        queries.append({'type': 'product_browse', 'lang': 'hi', 'query': 'सबसे ज्यादा बिकने वाले products दिखाओ'})
    if has_gu:
        queries.append({'type': 'product_browse', 'lang': 'gu', 'query': f'તમારા {p[0]} બતાવો'})
        queries.append({'type': 'product_browse', 'lang': 'gu', 'query': f'શું {p[1]} available છે?'})
        queries.append({'type': 'product_browse', 'lang': 'gu', 'query': 'તમારા best selling products કયા છે?'})

    # 3. SPECIFIC PRODUCT
    if has_en:
        queries.append({'type': 'specific_product', 'lang': 'en', 'query': f'I need a premium {p[0]}'})
        queries.append({'type': 'specific_product', 'lang': 'en', 'query': f'Looking for {p[2]} for daily use'})
        queries.append({'type': 'specific_product', 'lang': 'en', 'query': f'Do you have {p[3]} in stock?'})
    if has_hi:
        queries.append({'type': 'specific_product', 'lang': 'hi', 'query': f'मुझे {p[0]} चाहिए जो comfortable हो'})
    if has_gu:
        queries.append({'type': 'specific_product', 'lang': 'gu', 'query': f'મને {p[0]} જોઈએ છે'})

    # 4. PRICE FILTERING
    if has_en:
        queries.append({'type': 'price_filter', 'lang': 'en', 'query': f'Show me {p[0]} under $50'})
        queries.append({'type': 'price_filter', 'lang': 'en', 'query': f'{p[0]} between $20 and $100'})
        queries.append({'type': 'price_filter', 'lang': 'en', 'query': f"What's the cheapest {p[1]}?"})
        queries.append({'type': 'price_filter', 'lang': 'en', 'query': f'Budget {p[0]} under 500'})
        queries.append({'type': 'price_filter', 'lang': 'en', 'query': f'Most expensive {p[0]} you have?'})
    if has_hi:
        queries.append({'type': 'price_filter', 'lang': 'hi', 'query': f'500 रुपये से कम के {p[0]} बताओ'})
        queries.append({'type': 'price_filter', 'lang': 'hi', 'query': f'1000 से 2000 रुपये वाले {p[0]}'})
    if has_gu:
        queries.append({'type': 'price_filter', 'lang': 'gu', 'query': f'₹500 થી ઓછા {p[0]} બતાવો'})
        queries.append({'type': 'price_filter', 'lang': 'gu', 'query': f'સસ્તા {p[0]} છે?'})

    # 5. COLOR/ATTRIBUTE
    if has_en:
        queries.append({'type': 'color_filter', 'lang': 'en', 'query': f'Show me {p[0]} in blue'})
        queries.append({'type': 'color_filter', 'lang': 'en', 'query': f'Do you have black {p[0]}?'})
        queries.append({'type': 'color_filter', 'lang': 'en', 'query': f'I want a red {p[1]}'})
    if has_hi:
        queries.append({'type': 'color_filter', 'lang': 'hi', 'query': f'काले रंग के {p[0]} दिखाओ'})
    if has_gu:
        queries.append({'type': 'color_filter', 'lang': 'gu', 'query': f'લાલ રંગના {p[0]} બતાવો'})

    # 6. NON-PRODUCT
    if has_en:
        queries.append({'type': 'non_product', 'lang': 'en', 'query': 'What is your return policy?'})
        queries.append({'type': 'non_product', 'lang': 'en', 'query': 'How long does shipping take?'})
        queries.append({'type': 'non_product', 'lang': 'en', 'query': 'Do you offer free delivery?'})
        queries.append({'type': 'non_product', 'lang': 'en', 'query': 'What payment methods do you accept?'})
        queries.append({'type': 'non_product', 'lang': 'en', 'query': 'Where are you located?'})
        queries.append({'type': 'non_product', 'lang': 'en', 'query': 'Do you have a physical store?'})
    if has_hi:
        queries.append({'type': 'non_product', 'lang': 'hi', 'query': 'रिटर्न पॉलिसी क्या है?'})
        queries.append({'type': 'non_product', 'lang': 'hi', 'query': 'delivery कितने दिन में होती है?'})
    if has_gu:
        queries.append({'type': 'non_product', 'lang': 'gu', 'query': 'રિટર્ન પોલિસી શું છે?'})
        queries.append({'type': 'non_product', 'lang': 'gu', 'query': 'ડિલિવરી કેટલા દિવસમાં થાય?'})

    # 7. IRRELEVANT
    irrelevant_en = [
        'Can you write me a Python script to sort a list?',
        'Who is the Prime Minister of India?',
        'What is the capital of France?',
        'Tell me a joke about programming',
        'Explain quantum physics to me',
        "What's the weather like today?",
        'Who won the FIFA World Cup 2022?',
        'How do I make pasta at home?',
        'What is blockchain technology?',
        'Solve this math: 25 x 48',
    ]
    irrelevant_hi = [
        'भारत का प्रधानमंत्री कौन है?',
        'पायथन स्क्रिप्ट लिखो',
        'चांद पर कौन गया था?',
    ]
    irrelevant_gu = [
        'ભારતના વડાપ્રધાન કોણ છે?',
        'મને એક જોક કહો',
    ]

    if has_en:
        for q in irrelevant_en:
            queries.append({'type': 'irrelevant', 'lang': 'en', 'query': q})
    if has_hi:
        for q in irrelevant_hi:
            queries.append({'type': 'irrelevant', 'lang': 'hi', 'query': q})
    elif has_gu:
        for q in irrelevant_gu:
            queries.append({'type': 'irrelevant', 'lang': 'gu', 'query': q})

    # 8. UNSUPPORTED LANGUAGE
    queries.append({'type': 'unsupported_lang', 'lang': 'fr', 'query': 'Bonjour, montrez-moi vos produits les plus populaires'})
    queries.append({'type': 'unsupported_lang', 'lang': 'ja', 'query': 'こんにちは、人気商品を教えてください'})
    queries.append({'type': 'unsupported_lang', 'lang': 'es', 'query': 'Hola, muéstrame tus productos más vendidos'})
    queries.append({'type': 'unsupported_lang', 'lang': 'zh', 'query': '你好，给我看看你们最好的产品'})

    if not has_hi:
        queries.append({'type': 'unsupported_lang_hindi', 'lang': 'hi', 'query': f'नमस्ते! आपके पास कौन से {p[0]} हैं?'})
        queries.append({'type': 'unsupported_lang_hindi', 'lang': 'hi', 'query': '500 रुपये से कम में क्या मिलेगा?'})
    if not has_gu:
        queries.append({'type': 'unsupported_lang_gujarati', 'lang': 'gu', 'query': f'તમારી પાસે કયા {p[0]} છે?'})

    # 9. MISSING INFO
    if has_en:
        queries.append({'type': 'missing_info', 'lang': 'en', 'query': 'Show me your product warranty certificates'})
        queries.append({'type': 'missing_info', 'lang': 'en', 'query': 'What is the GSM rating of your cotton fabric?'})
        queries.append({'type': 'missing_info', 'lang': 'en', 'query': "What are your CEO's contact details?"})
        queries.append({'type': 'missing_info', 'lang': 'en', 'query': 'What year was your company founded?'})
        queries.append({'type': 'missing_info', 'lang': 'en', 'query': 'Can you show your ISO certification?'})
        queries.append({'type': 'missing_info', 'lang': 'en', 'query': "What's the thread count of your premium fabric?"})
    if has_hi:
        queries.append({'type': 'missing_info', 'lang': 'hi', 'query': 'आपकी कंपनी का GSTIN नंबर क्या है?'})
    if has_gu:
        queries.append({'type': 'missing_info', 'lang': 'gu', 'query': 'તમારી company નો GST number શું છે?'})

    # 10. SUGGESTION QUALITY
    if has_en:
        queries.append({'type': 'suggestions_test', 'lang': 'en', 'query': f"I'm new here, what {p[0]} do you sell?"})
        queries.append({'type': 'suggestions_test', 'lang': 'en', 'query': 'What do you recommend for a gift?'})
    if has_hi:
        queries.append({'type': 'suggestions_test', 'lang': 'hi', 'query': 'यहां क्या-क्या मिलता है?'})
    if has_gu:
        queries.append({'type': 'suggestions_test', 'lang': 'gu', 'query': 'gift માટે શું recommend કરો?'})

    # 11. ROMANIZED
    if has_hi:
        queries.append({'type': 'romanized', 'lang': 'hi-Latn', 'query': f'mujhe {p[0]} dikhao'})
        queries.append({'type': 'romanized', 'lang': 'hi-Latn', 'query': 'saste wale products batao'})
        queries.append({'type': 'romanized', 'lang': 'hi-Latn', 'query': 'kya discount chal raha hai?'})
    if has_gu:
        queries.append({'type': 'romanized', 'lang': 'gu-Latn', 'query': f'mane {p[0]} batavo'})
        queries.append({'type': 'romanized', 'lang': 'gu-Latn', 'query': 'sasta wala shu chhe?'})
        queries.append({'type': 'romanized', 'lang': 'gu-Latn', 'query': 'tamari best products batavo'})

    # 12. MIXED LANGUAGE
    if has_en and has_hi:
        queries.append({'type': 'mixed_lang', 'lang': 'hi-mix', 'query': f'Mujhe {p[0]} chahiye blue color mein'})
        queries.append({'type': 'mixed_lang', 'lang': 'hi-mix', 'query': 'price range kya hai aapka?'})
    if has_en and has_gu:
        queries.append({'type': 'mixed_lang', 'lang': 'gu-mix', 'query': f'Mane {p[0]} joiye affordable wala'})
        queries.append({'type': 'mixed_lang', 'lang': 'gu-mix', 'query': 'tumhare best products shu chhe?'})

    # 13. AMBIGUOUS
    if has_en:
        queries.append({'type': 'ambiguous', 'lang': 'en', 'query': 'something nice'})
        queries.append({'type': 'ambiguous', 'lang': 'en', 'query': 'I need help'})
        queries.append({'type': 'ambiguous', 'lang': 'en', 'query': 'What do you have?'})
        queries.append({'type': 'ambiguous', 'lang': 'en', 'query': 'show me options'})
        queries.append({'type': 'ambiguous', 'lang': 'en', 'query': 'gift ideas'})

    # 14. COMPARISON
    if has_en:
        queries.append({'type': 'comparison', 'lang': 'en', 'query': f'Which {p[0]} is better quality?'})
        queries.append({'type': 'comparison', 'lang': 'en', 'query': f"What's the difference between your {p[0]} and {p[1]}?"})
        queries.append({'type': 'comparison', 'lang': 'en', 'query': f'Which {p[0]} would you recommend?'})

    # 15. EDGE CASES
    queries.append({'type': 'edge_case', 'lang': 'en', 'query': 'ok'})
    queries.append({'type': 'edge_case', 'lang': 'en', 'query': 'thanks'})
    queries.append({'type': 'edge_case', 'lang': 'en', 'query': 'yes'})
    queries.append({'type': 'edge_case', 'lang': 'en', 'query': 'no'})
    queries.append({'type': 'edge_case', 'lang': 'en', 'query': 'hmm'})
    queries.append({'type': 'edge_case', 'lang': 'en', 'query': '???'})
    queries.append({'type': 'edge_case', 'lang': 'en', 'query': 'lol'})
    queries.append({'type': 'edge_case', 'lang': 'en', 'query': f'{p[0]}'})

    # 16. ABOUT BRAND
    if has_en:
        queries.append({'type': 'about_brand', 'lang': 'en', 'query': f'Tell me about {name}'})
        queries.append({'type': 'about_brand', 'lang': 'en', 'query': 'Who are you and what do you sell?'})
    if has_hi:
        queries.append({'type': 'about_brand', 'lang': 'hi', 'query': f'{name} के बारे में बताओ'})

    # 17. COMPLAINT
    if has_en:
        queries.append({'type': 'complaint', 'lang': 'en', 'query': 'Your products are too expensive'})
        queries.append({'type': 'complaint', 'lang': 'en', 'query': 'I had a bad experience with my last order'})
        queries.append({'type': 'complaint', 'lang': 'en', 'query': 'Why is the quality so poor?'})

    # 18. PRICE FORMAT
    if has_en:
        queries.append({'type': 'price_format', 'lang': 'en', 'query': f'Show me {p[0]} with prices'})
        queries.append({'type': 'price_format', 'lang': 'en', 'query': "What's the price range of your products?"})
    if has_hi:
        queries.append({'type': 'price_format', 'lang': 'hi', 'query': f'{p[0]} का price क्या है?'})
    if has_gu:
        queries.append({'type': 'price_format', 'lang': 'gu', 'query': f'{p[0]} ની price શું છે?'})

    return queries

result = {}
for bot in BOTS_TO_TEST:
    qs = build_queries_for_bot(bot)
    result[bot['name']] = qs

# Save full JSON
with open('v4_all_queries.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

# Save per-bot JSON files
for bot_name, qs in result.items():
    with open(f'v4_queries_{bot_name}.json', 'w', encoding='utf-8') as f:
        json.dump({"bot": bot_name, "total_queries": len(qs), "queries": qs}, f, ensure_ascii=False, indent=2)

# Print summary
total = 0
for name, qs in result.items():
    types = {}
    for q in qs:
        types[q['type']] = types.get(q['type'], 0) + 1
    total += len(qs)
    print(f'\n=== {name} ({len(qs)} queries) ===')
    for t, c in sorted(types.items()):
        print(f'  {t}: {c}')
print(f'\nTOTAL: {total} queries across {len(result)} bots')
print(f'\nFiles created: v4_all_queries.json + v4_queries_<bot>.json per bot')
