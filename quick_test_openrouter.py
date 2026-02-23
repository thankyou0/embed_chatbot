"""Quick test to verify OpenRouter + price fix"""
import requests, json, uuid

# Login
login_resp = requests.post('http://localhost:8000/api/v1/auth/login',
    json={'email': 'max@gmail.com', 'password': '12345678'}
)
token = login_resp.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# Test 1: Product query (check price format)
sid = str(uuid.uuid4())
resp = requests.post(
    'http://localhost:8000/api/v1/chat/182f88cd-02d8-4c94-824d-b41432847400/message/stream',
    headers=headers,
    data={'message': 'show me wall art under 500', 'session_id': sid, 'is_preview': 'true'},
    stream=True, timeout=45
)
print(f"Test 1 - Product query: Status={resp.status_code}")
full = ''
for line in resp.iter_lines():
    if line:
        text = line.decode('utf-8')
        if text.startswith('data: '):
            try:
                data = json.loads(text[6:])
                if data.get('type') == 'products':
                    for p in data.get('products', [])[:3]:
                        pname = p.get("name", "?")[:40]
                        pprice = p.get("price")
                        pcurr = p.get("currency")
                        print(f"  Product: {pname} | price={pprice} | currency={pcurr}")
                elif data.get('type') == 'token':
                    full += data.get('content', '')
                elif data.get('type') == 'done':
                    print(f"  DONE. Response length: {len(full)}")
            except:
                pass
print(f"  Preview: {full[:200]}")
print()

# Test 2: Irrelevant query (should get rejected)
sid2 = str(uuid.uuid4())
resp2 = requests.post(
    'http://localhost:8000/api/v1/chat/182f88cd-02d8-4c94-824d-b41432847400/message/stream',
    headers=headers,
    data={'message': 'Write a Python script to sort a list', 'session_id': sid2, 'is_preview': 'true'},
    stream=True, timeout=45
)
print(f"Test 2 - Irrelevant query: Status={resp2.status_code}")
full2 = ''
for line in resp2.iter_lines():
    if line:
        text = line.decode('utf-8')
        if text.startswith('data: '):
            try:
                data = json.loads(text[6:])
                if data.get('type') == 'token':
                    full2 += data.get('content', '')
                elif data.get('type') == 'done':
                    has_irrelevant = '[[IRRELEVANT]]' in full2
                    print(f"  DONE. Has [[IRRELEVANT]]: {has_irrelevant}")
            except:
                pass
print(f"  Response: {full2[:300]}")
