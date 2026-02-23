"""Check price format in products"""
import requests, json, uuid

login_resp = requests.post('http://localhost:8000/api/v1/auth/login',
    json={'email': 'max@gmail.com', 'password': '12345678'})
token = login_resp.json()['access_token']
sid = str(uuid.uuid4())
resp = requests.post(
    'http://localhost:8000/api/v1/chat/182f88cd-02d8-4c94-824d-b41432847400/message/stream',
    headers={'Authorization': f'Bearer {token}'},
    data={'message': 'show me shirts', 'session_id': sid, 'is_preview': 'true'},
    stream=True, timeout=30
)
for line in resp.iter_lines():
    if line:
        text = line.decode('utf-8')
        if text.startswith('data: '):
            data = json.loads(text[6:])
            dtype = data.get('type')
            if dtype == 'done':
                prods = data.get('products', [])
                print(f"Products in 'done': {len(prods)}")
                for p in prods[:5]:
                    name = p.get("name", "?")[:40]
                    price = p.get("price")
                    curr = p.get("currency")
                    print(f"  {name} | price={price} | currency={curr}")
            elif dtype == 'products':
                prods2 = data.get('products', [])
                print(f"Products event: {len(prods2)}")
                for p in prods2[:5]:
                    name = p.get("name", "?")[:40]
                    price = p.get("price")
                    curr = p.get("currency")
                    print(f"  {name} | price={price} | currency={curr}")
