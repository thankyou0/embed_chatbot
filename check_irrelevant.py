"""Check irrelevant query rejection"""
import requests, json, uuid

login_resp = requests.post('http://localhost:8000/api/v1/auth/login',
    json={'email': 'max@gmail.com', 'password': '12345678'})
token = login_resp.json()['access_token']

for query in ['Write a Python script to sort a list', 'Who is the PM of India?', 'Tell me about machine learning']:
    sid = str(uuid.uuid4())
    resp = requests.post(
        'http://localhost:8000/api/v1/chat/182f88cd-02d8-4c94-824d-b41432847400/message/stream',
        headers={'Authorization': f'Bearer {token}'},
        data={'message': query, 'session_id': sid, 'is_preview': 'true'},
        stream=True, timeout=30
    )
    full = ''
    for line in resp.iter_lines():
        if line:
            text = line.decode('utf-8')
            if text.startswith('data: '):
                data = json.loads(text[6:])
                if data.get('type') == 'content':
                    full += data.get('content', '')
    has_irr = '[[IRRELEVANT]]' in full
    print(f"Query: '{query[:40]}' | IRRELEVANT={has_irr} | Response: {full[:100]}")
