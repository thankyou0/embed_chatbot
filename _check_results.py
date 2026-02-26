import json

d = json.load(open('_query_results_final.json', 'r', encoding='utf-8'))

for bot_name, bot_data in list(d.items())[:3]:
    print(f"\n=== {bot_name} ===")
    for q in bot_data['queries'][:4]:
        qtype = q.get('type', '?')
        text = q.get('text', '')
        prods = q.get('product_count', 0)
        tags = q.get('tags', [])
        sugs = q.get('suggestions', [])
        print(f"  {qtype:25s} | text({len(text)}ch): {text[:120]}...")
        if prods:
            print(f"    products: {q.get('products', [])}")
        if sugs:
            print(f"    suggestions: {sugs}")
