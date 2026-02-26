import json

with open('missing_info_v2_results.json', 'r') as f:
    data = json.load(f)

for r in data['results'][:5]:
    status = r.get('status', '?')
    missing = r.get('is_missing_info_db', '?')
    irrelevant = r.get('is_irrelevant_db', '?')
    answered = r.get('was_answered_db', '?')
    query = r.get('query', '')[:60]
    resp = r.get('response', '')[:120]
    print(f"Status={status} | missing_db={missing} | irrelevant_db={irrelevant} | answered_db={answered}")
    print(f"  Q: {query}")
    print(f"  A: {resp}")
    print()
