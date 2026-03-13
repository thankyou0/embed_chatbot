"""Replace 5 failed crawl chatbots with crawl-friendly sites."""
import httpx

BASE = "http://localhost:8000/api/v1"
r = httpx.post(f"{BASE}/auth/login", json={"email": "max@gmail.com", "password": "12345678"})
token = r.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Failed bot IDs to delete
FAILED = [
    "f6505241-8a78-4fe6-a35f-878bba7ebe1d",  # TataCliq
    "85e382d8-15b7-4d76-99ec-e5b0974aca9c",  # Amul
    "b321db31-9cd3-4eef-8c8f-9da22ca67805",  # IRCTC
    "449ece04-b195-4fce-a9ab-e5ae2002bb30",  # Zomato
    "937acc36-794b-476f-b338-5a153cb98585",  # PolicyBazaar
]

for bid in FAILED:
    r = httpx.delete(f"{BASE}/chatbots/{bid}", headers=headers, timeout=30)
    print(f"Delete {bid}: {r.status_code}")

# Replacement crawl-friendly sites
REPLACEMENTS = [
    {
        "name": "TheManCompany",
        "url": "https://www.themancompany.com",
        "languages": ["en", "hi"],
        "personality": "professional",
    },
    {
        "name": "Vahdam Teas",
        "url": "https://www.vahdamindia.com",
        "languages": ["en", "hi", "gu"],
        "personality": "friendly",
    },
    {
        "name": "Plum Goodness",
        "url": "https://plumgoodness.com",
        "languages": ["en"],
        "personality": "friendly",
    },
    {
        "name": "Mokobara",
        "url": "https://www.mokobara.com",
        "languages": ["en", "hi"],
        "personality": "casual",
    },
    {
        "name": "SlurrpFarm",
        "url": "https://slurrpfarm.com",
        "languages": ["en", "hi", "gu"],
        "personality": "friendly",
    },
]

for bot in REPLACEMENTS:
    print(f"\n--- Creating {bot['name']} ---")
    r = httpx.post(f"{BASE}/chatbots", json={"name": bot["name"]}, headers=headers, timeout=30)
    if r.status_code not in (200, 201):
        print(f"  FAILED: {r.status_code} {r.text[:200]}")
        continue
    data = r.json()
    bot_id = data["id"]
    print(f"  Created: {bot_id}")

    r2 = httpx.patch(
        f"{BASE}/chatbots/{bot_id}/appearance",
        json={
            "languages": bot["languages"],
            "personality_tone": bot["personality"],
            "header_text": f"Chat with {bot['name']}",
        },
        headers=headers, timeout=30,
    )
    print(f"  Appearance: {r2.status_code}, languages={bot['languages']}")

    r3 = httpx.post(
        f"{BASE}/chatbots/{bot_id}/crawl",
        json={"base_url": bot["url"]},
        headers=headers, timeout=60,
    )
    if r3.status_code in (200, 201, 202):
        src = r3.json()
        print(f"  Crawl started: source={src['id']}")
    else:
        print(f"  Crawl FAILED: {r3.status_code} {r3.text[:200]}")
