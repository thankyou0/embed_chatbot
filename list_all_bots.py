import requests, json

r = requests.post('http://localhost:8000/api/v1/auth/login', json={'email':'max@gmail.com','password':'12345678'})
token = r.json()['access_token']
bots = requests.get('http://localhost:8000/api/v1/chatbots/', headers={'Authorization': f'Bearer {token}'})
data = bots.json()
# Handle both list and dict response formats
if isinstance(data, dict):
    items = data.get('chatbots', data.get('items', []))
elif isinstance(data, list):
    items = data
else:
    items = []
    print(f"Unexpected format: {type(data)}")
for b in items:
    print(f"{b['name']}: {b['id']} status={b.get('status')}")

# Also check appearances/languages for key bots
key_bots = [
    "182f88cd-02d8-4c94-824d-b41432847400",  # ramraj
    "e79b3754-006d-45d5-b21d-2391710e08ca",  # zevaramaze
    "1cb18dc0-4909-409d-ab03-0436524fcec4",  # kriyanta
]
print("\n--- Language configs for key bots ---")
for bid in key_bots:
    r2 = requests.get(f'http://localhost:8000/api/v1/chat/{bid}/config')
    if r2.status_code == 200:
        cfg = r2.json()
        print(f"Bot {bid[:8]}: languages={cfg.get('languages')}, name={cfg.get('name')}")
    else:
        print(f"Bot {bid[:8]}: config fetch failed ({r2.status_code})")
