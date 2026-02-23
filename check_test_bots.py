import requests

r = requests.post('http://localhost:8000/api/v1/auth/login', json={'email':'max@gmail.com','password':'12345678'})
token = r.json()['access_token']

test_bots = [
    ('Crawl-Beardbrand', 'e23fcc6f-7a02-4b09-8d49-95c00a57d852'),
    ('Crawl-Death Wish Coffee', '99fc3604-99e7-4cd0-a2a6-509ac08d9fd0'),
    ('Crawl-Tentree', '799637f9-391b-4b9d-84cb-5fdd17cdf109'),
    ('Test-Mokobara', '11530893-543e-4974-9036-86a92f9dc986'),
    ('Test-Sugar Cosmetics', 'eddf4f64-055d-478e-a6b4-f2de57d6a88c'),
    ('Test-Boat Lifestyle', 'b784a488-0d19-49fb-b670-9552a07c6dda'),
    ('Test-Bombas', '9a99fdd3-e34e-4c79-a226-12dc85c989ec'),
]

for name, bid in test_bots:
    r2 = requests.get(f'http://localhost:8000/api/v1/chatbots/{bid}', headers={'Authorization': f'Bearer {token}'})
    if r2.status_code == 200:
        d = r2.json()
        pages = d.get('crawled_pages', d.get('page_count', '?'))
        src = d.get('knowledge_sources', [])
        print(f'{name}: pages={pages}, sources={len(src)}')
    else:
        r3 = requests.get(f'http://localhost:8000/api/v1/chat/{bid}/config')
        cfg = r3.json() if r3.status_code == 200 else {}
        langs = cfg.get('languages', 'N/A')
        print(f'{name}: detail_err={r2.status_code}, config_langs={langs}')
