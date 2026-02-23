import requests, json

# Quick test - send a greeting to Crawl-Beardbrand
url = 'http://localhost:8000/api/v1/chat/e23fcc6f-7a02-4b09-8d49-95c00a57d852/message/stream'
r = requests.post(url, data={'message': 'Hi', 'is_preview': 'true'})
print('Beardbrand:', r.status_code, r.text[:300])
print()

# Quick test - send a greeting to Crawl-Death Wish
url2 = 'http://localhost:8000/api/v1/chat/99fc3604-99e7-4cd0-a2a6-509ac08d9fd0/message/stream'
r2 = requests.post(url2, data={'message': 'Hi', 'is_preview': 'true'})
print('Death Wish:', r2.status_code, r2.text[:300])
print()

# Check config for these
test_ids = [
    'e23fcc6f-7a02-4b09-8d49-95c00a57d852',
    '99fc3604-99e7-4cd0-a2a6-509ac08d9fd0',
    '799637f9-391b-4b9d-84cb-5fdd17cdf109'
]
for bid in test_ids:
    r3 = requests.get(f'http://localhost:8000/api/v1/chat/{bid}/config')
    cfg = r3.json() if r3.status_code == 200 else {}
    langs = cfg.get('languages')
    name = cfg.get('name')
    print(f'{bid[:8]}: langs={langs}, name={name}')
