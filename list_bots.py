import requests

r = requests.post('http://localhost:8000/api/v1/auth/login', json={'email':'max@gmail.com','password':'12345678'})
token = r.json()['access_token']
bots = requests.get('http://localhost:8000/api/v1/chatbots/', headers={'Authorization': f'Bearer {token}'})
print(f"Status: {bots.status_code}")
import json
data = bots.json()
print(json.dumps(data, indent=2, default=str)[:3000])
