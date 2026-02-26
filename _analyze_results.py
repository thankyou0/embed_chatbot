"""Analyze query results and generate report"""
import json, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

d = json.load(open('_query_results_final.json', 'r', encoding='utf-8'))

print("="*80)
print("FULL ANALYSIS OF QUERY RESULTS")
print("="*80)

for bot_name, bot_data in d.items():
    info = bot_data['info']
    queries = bot_data['queries']
    print(f"\n{'='*70}")
    print(f"BOT: {bot_name} | {info['desc']} | {info['pages']} pages")
    print(f"{'='*70}")
    
    for q in queries:
        qtype = q.get('type', '?')
        ok = q.get('ok', False)
        text = q.get('text', '')
        prods = q.get('product_count', 0)
        tags = q.get('tags', [])
        sugs = q.get('suggestions', [])
        err = q.get('error', '')
        products = q.get('products', [])
        
        status = "OK" if ok and not err else f"FAIL({err})" if err else "FAIL"
        
        print(f"\n  [{qtype:25s}] status={status}")
        print(f"    Query: {q.get('query', '?')}")
        if text:
            print(f"    Response ({len(text)}ch): {text[:200]}{'...' if len(text)>200 else ''}")
        elif ok and not err:
            print(f"    Response: (text not captured in first run but query processed)")
        if prods > 0:
            print(f"    Products ({prods}): {products}")
        if sugs:
            print(f"    Suggestions: {sugs}")
        if tags:
            print(f"    Tags: {tags}")
