"""Quick test to see full SSE event format"""
import requests, json

API = "http://localhost:8000/api/v1"
s = requests.Session()
r = s.post(f"{API}/auth/login", json={"email":"max@gmail.com","password":"12345678"})
token = r.json()["access_token"]

bot_id = "cc90afbd-5839-45d5-a4aa-68f681f60e61"  # rawpressery
resp = s.post(
    f"{API}/chat/{bot_id}/message/stream",
    data={"message": "Show me juices"},
    headers={"Authorization": f"Bearer {token}"},
    stream=True, timeout=40
)

for i, line in enumerate(resp.iter_lines(decode_unicode=True)):
    if not line:
        continue
    print(f"[{i}] {line[:200]}")
    if "[DONE]" in line:
        break
