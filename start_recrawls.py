import httpx
import json

BASE = "http://localhost:8000/api/v1"

# Login
r = httpx.post(f"{BASE}/auth/login", json={"email": "max@gmail.com", "password": "12345678"})
token = r.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Knowledge source IDs for underperforming bots
sources = {
    "Nicobar": "0ab5ef59-e1cd-47e7-9142-288dcd6a42c6",
    "PlumGoodness": "f47b05b9-db76-4f7e-9756-859f3b52a2fa",
    "SlurrpFarm": "70fc37f2-a364-4a24-a0fb-f04083aec902",
    "TheManCompany": "19a91c07-aad3-4348-9455-d63ec7ccaeba",
}

for name, ks_id in sources.items():
    r = httpx.post(
        f"{BASE}/chatbots/knowledge-sources/{ks_id}/crawl-now",
        headers=headers,
        timeout=30,
    )
    print(f"{name}: {r.status_code} - {r.text[:300]}")
