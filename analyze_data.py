import json, sys
sys.stdout.reconfigure(encoding='utf-8')

# Load both data sources
data1 = json.load(open('chatbot_test_raw_data.json', encoding='utf-8'))
data2 = json.load(open('test_results_v2_raw.json', encoding='utf-8'))

print("=" * 80)
print("COMPREHENSIVE TEST ANALYSIS")
print("=" * 80)

# Analyze chatbot_test_raw_data.json (main dataset - 210 queries)
all_results = []
bot_summaries = []

for bot in data1:
    valid = [q for q in bot['query_results'] if not q.get('is_rate_limited')]
    rate_limited = [q for q in bot['query_results'] if q.get('is_rate_limited')]
    scores = [q['evaluation']['score'] for q in valid if q['evaluation']['score'] >= 0]
    avg = sum(scores) / len(scores) if scores else 0
    failed = [q for q in valid if not q['evaluation']['passed']]
    
    by_type = {}
    for q in valid:
        t = q['type']
        if t not in by_type:
            by_type[t] = {'scores': [], 'count': 0, 'issues': [], 'queries': []}
        by_type[t]['count'] += 1
        if q['evaluation']['score'] >= 0:
            by_type[t]['scores'].append(q['evaluation']['score'])
        if q['evaluation'].get('issues'):
            by_type[t]['issues'].extend(q['evaluation']['issues'])
        by_type[t]['queries'].append(q)
    
    print(f"\n{'='*60}")
    print(f"BOT: {bot['name']} ({bot['category']})")
    print(f"URL: {bot.get('url', 'N/A')}")
    print(f"Pages Crawled: {bot['pages']}")
    print(f"Total Queries: {len(bot['query_results'])} | Valid: {len(valid)} | Rate-Limited: {len(rate_limited)}")
    print(f"Average Score: {avg:.1f}/10")
    print(f"Failed Queries: {len(failed)}")
    print(f"-" * 40)
    
    for t, d in by_type.items():
        tavg = sum(d['scores']) / len(d['scores']) if d['scores'] else 0
        print(f"  {t}: avg={tavg:.1f}/10 ({d['count']} queries)")
        if d['issues']:
            for iss in d['issues']:
                print(f"    ISSUE: {iss}")
    
    # Show all failed queries
    if failed:
        print(f"\n  FAILED QUERIES:")
        for q in failed:
            print(f"    [{q['type']}] [{q['lang']}] {q['query'][:60]}")
            print(f"      Score: {q['evaluation']['score']}")
            print(f"      Issues: {q['evaluation'].get('issues', [])}")
            print(f"      Response: {q['response_content'][:100]}...")
    
    # Show low-scoring queries (<7)
    low = [q for q in valid if 0 < q['evaluation']['score'] < 7]
    if low:
        print(f"\n  LOW-SCORING QUERIES (<7):")
        for q in low:
            print(f"    [{q['type']}] [{q['lang']}] Score={q['evaluation']['score']} - {q['query'][:60]}")
            print(f"      Response: {q['response_content'][:120]}...")
            if q['evaluation'].get('issues'):
                print(f"      Issues: {q['evaluation']['issues']}")
    
    bot_summaries.append({
        'name': bot['name'],
        'category': bot['category'],
        'pages': bot['pages'],
        'avg_score': avg,
        'valid': len(valid),
        'rate_limited': len(rate_limited),
        'failed': len(failed),
        'by_type': {t: sum(d['scores'])/len(d['scores']) if d['scores'] else 0 for t, d in by_type.items()}
    })

# Print product listing analysis
print("\n\n" + "=" * 80)
print("PRODUCT LISTING ANALYSIS")
print("=" * 80)

for bot in data1:
    valid = [q for q in bot['query_results'] if not q.get('is_rate_limited')]
    product_queries = [q for q in valid if q.get('products_count', 0) > 0]
    non_product_with_products = [q for q in valid if q['type'] in ('non_product', 'irrelevant', 'greeting') and q.get('products_count', 0) > 0]
    product_type_no_products = [q for q in valid if q['type'] in ('product_browse', 'specific_product', 'price_query', 'comparison', 'complex') and q.get('products_count', 0) == 0 and not q.get('is_rate_limited')]
    
    print(f"\n--- {bot['name']} ---")
    print(f"  Queries with products: {len(product_queries)}/{len(valid)}")
    
    if product_type_no_products:
        print(f"  MISSING PRODUCTS (should have returned products):")
        for q in product_type_no_products:
            print(f"    [{q['type']}] [{q['lang']}] {q['query'][:60]}")
            print(f"      Products: {q.get('products_count', 0)}, Sources: {q.get('sources_count', 0)}")
    
    if non_product_with_products:
        print(f"  UNNECESSARY PRODUCTS (shouldn't have products):")
        for q in non_product_with_products:
            print(f"    [{q['type']}] [{q['lang']}] {q['query'][:60]} -> {q.get('products_count', 0)} products")
    
    # Check product data quality
    for q in product_queries:
        if q.get('products'):
            missing_price = sum(1 for p in q['products'] if not p.get('price'))
            missing_image = sum(1 for p in q['products'] if not p.get('image'))
            if missing_price > 0 or missing_image > 0:
                print(f"  DATA QUALITY: [{q['type']}] {q['query'][:40]} - {missing_price} missing prices, {missing_image} missing images")

# Suggestion analysis
print("\n\n" + "=" * 80)
print("SUGGESTION ANALYSIS")
print("=" * 80)

for bot in data1:
    valid = [q for q in bot['query_results'] if not q.get('is_rate_limited')]
    with_suggestions = [q for q in valid if q.get('suggestions') and len(q['suggestions']) > 0]
    without_suggestions = [q for q in valid if not q.get('suggestions') or len(q['suggestions']) == 0]
    
    print(f"\n--- {bot['name']} ---")
    print(f"  With suggestions: {len(with_suggestions)}/{len(valid)} ({100*len(with_suggestions)/len(valid):.0f}%)")
    
    if without_suggestions:
        print(f"  Missing suggestions for:")
        for q in without_suggestions[:5]:
            print(f"    [{q['type']}] [{q['lang']}] {q['query'][:60]}")

# Language analysis  
print("\n\n" + "=" * 80)
print("LANGUAGE PERFORMANCE ANALYSIS")
print("=" * 80)

lang_scores = {}
for bot in data1:
    for q in bot['query_results']:
        if q.get('is_rate_limited'):
            continue
        lang = q['lang']
        if lang not in lang_scores:
            lang_scores[lang] = []
        if q['evaluation']['score'] >= 0:
            lang_scores[lang].append(q['evaluation']['score'])

for lang, scores in sorted(lang_scores.items()):
    avg = sum(scores) / len(scores) if scores else 0
    print(f"  {lang}: avg={avg:.1f}/10 ({len(scores)} queries)")

# Language-specific issues
print("\n  LANGUAGE-SPECIFIC ISSUES:")
for bot in data1:
    for q in bot['query_results']:
        if q.get('is_rate_limited'):
            continue
        resp = q.get('response_content', '')
        # Check if Hindi query got Gujarati response
        if q['lang'] == 'hi' and any(c in resp for c in 'અઆઇઈઉઊ'):
            print(f"    WRONG SCRIPT: [{bot['name']}] Hindi query got Gujarati response: {q['query'][:40]}")
        # Check if Gujarati query got Hindi response
        if q['lang'] == 'gu' and any(c in resp for c in 'अआइईउऊ') and not any(c in resp for c in 'અઆઇ'):
            print(f"    WRONG SCRIPT: [{bot['name']}] Gujarati query got Hindi response: {q['query'][:40]}")

# Query type performance across all bots
print("\n\n" + "=" * 80)
print("QUERY TYPE PERFORMANCE (ALL BOTS)")  
print("=" * 80)

type_scores = {}
for bot in data1:
    for q in bot['query_results']:
        if q.get('is_rate_limited'):
            continue
        t = q['type']
        if t not in type_scores:
            type_scores[t] = []
        if q['evaluation']['score'] >= 0:
            type_scores[t].append(q['evaluation']['score'])

for t, scores in sorted(type_scores.items()):
    avg = sum(scores) / len(scores) if scores else 0
    low = sum(1 for s in scores if s < 7)
    print(f"  {t}: avg={avg:.1f}/10 ({len(scores)} queries, {low} below 7)")

print("\n\nDONE")
