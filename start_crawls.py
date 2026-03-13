import httpx
import json

BASE = "http://localhost:8000/api/v1"

# Login
r = httpx.post(f"{BASE}/auth/login", json={"email": "max@gmail.com", "password": "12345678"})
token = r.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

bots = {
    "Nicobar": {"id": "9c34c714-073c-483a-945d-730a102092ab", "ks_id": "0ab5ef59-e1cd-47e7-9142-288dcd6a42c6"},
    "PlumGoodness": {"id": "4ef4ea06-eba5-4319-9b4c-c74ca7f7dc23", "ks_id": "f47b05b9-db76-4f7e-9756-859f3b52a2fa"},
    "SlurrpFarm": {"id": "ff936f98-ed66-4a03-b0c4-80b4b8e9c324", "ks_id": "70fc37f2-a364-4a24-a0fb-f04083aec902"},
    "TheManCompany": {"id": "35fdd3ff-c56c-4877-8452-94b9fa1dd492", "ks_id": "19a91c07-aad3-4348-9455-d63ec7ccaeba"},
}

for name, info in bots.items():
    r = httpx.post(
        f"{BASE}/chatbots/{info['id']}/knowledge-sources/{info['ks_id']}/crawl",
        headers=headers,
        json={"max_pages": 500},
        timeout=30
    )
    print(f"{name}: {r.status_code} - {r.text[:200]}")
