"""
Create 9 test chatbots with diverse sites and language settings,
then start crawls for each. To be run inside the chatbot_api container.
"""
import httpx
import json
import time

BASE = "http://localhost:8000/api/v1"

# Login
r = httpx.post(f"{BASE}/auth/login", json={"email": "max@gmail.com", "password": "12345678"})
token = r.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 9 new chatbots with diverse sites & language mixes
BOTS = [
    {
        "name": "TataCliq",
        "description": "Indian premium e-commerce (fashion, electronics, luxury brands)",
        "url": "https://www.tatacliq.com",
        "languages": ["en", "hi"],
        "personality": "professional",
    },
    {
        "name": "Amul",
        "description": "India's leading dairy brand - milk products, ice cream, cheese, butter",
        "url": "https://amul.com",
        "languages": ["en", "hi", "gu"],
        "personality": "friendly",
    },
    {
        "name": "IRCTC",
        "description": "Indian Railways official site - train booking, tourism, catering",
        "url": "https://www.irctc.co.in",
        "languages": ["en", "hi"],
        "personality": "professional",
    },
    {
        "name": "BigBasket",
        "description": "Online grocery delivery - fresh produce, pantry, beverages, household",
        "url": "https://www.bigbasket.com",
        "languages": ["en", "hi"],
        "personality": "friendly",
    },
    {
        "name": "Mamaearth",
        "description": "Natural & toxin-free personal care, skincare, haircare products",
        "url": "https://mamaearth.in",
        "languages": ["en"],
        "personality": "friendly",
    },
    {
        "name": "BoAt",
        "description": "Indian audio brand - earbuds, headphones, speakers, smartwatches",
        "url": "https://www.boat-lifestyle.com",
        "languages": ["en"],
        "personality": "casual",
    },
    {
        "name": "Zomato",
        "description": "Food delivery & restaurant discovery platform in India",
        "url": "https://www.zomato.com",
        "languages": ["en", "hi"],
        "personality": "casual",
    },
    {
        "name": "PolicyBazaar",
        "description": "Insurance comparison - life, health, car, travel insurance in India",
        "url": "https://www.policybazaar.com",
        "languages": ["en", "hi"],
        "personality": "professional",
    },
    {
        "name": "Byju's",
        "description": "EdTech platform - online learning, exam prep, K-12 education",
        "url": "https://byjus.com",
        "languages": ["en", "hi", "gu"],
        "personality": "friendly",
    },
]

created = []
for bot in BOTS:
    print(f"\n--- Creating {bot['name']} ---")
    # Create chatbot
    r = httpx.post(f"{BASE}/chatbots", json={"name": bot["name"]}, headers=headers, timeout=30)
    if r.status_code not in (200, 201):
        print(f"  FAILED to create: {r.status_code} {r.text[:200]}")
        continue
    data = r.json()
    bot_id = data["id"]
    print(f"  Created: {bot_id}")

    # Update appearance (languages + personality)
    r2 = httpx.patch(
        f"{BASE}/chatbots/{bot_id}/appearance",
        json={
            "languages": bot["languages"],
            "personality_tone": bot["personality"],
            "header_text": f"Chat with {bot['name']}",
        },
        headers=headers,
        timeout=30,
    )
    if r2.status_code == 200:
        print(f"  Appearance set: languages={bot['languages']}, tone={bot['personality']}")
    else:
        print(f"  Appearance FAILED: {r2.status_code} {r2.text[:200]}")

    # Start crawl
    r3 = httpx.post(
        f"{BASE}/chatbots/{bot_id}/crawl",
        json={"base_url": bot["url"]},
        headers=headers,
        timeout=60,
    )
    if r3.status_code in (200, 201, 202):
        src = r3.json()
        print(f"  Crawl started: source={src['id']}, url={bot['url']}")
        created.append({"name": bot["name"], "id": bot_id, "source_id": src["id"], "url": bot["url"]})
    else:
        print(f"  Crawl FAILED: {r3.status_code} {r3.text[:200]}")
        created.append({"name": bot["name"], "id": bot_id, "source_id": None, "url": bot["url"]})

print("\n\n=== SUMMARY ===")
for c in created:
    print(f"  {c['name']}: bot={c['id']}, source={c['source_id']}, url={c['url']}")
print(f"\nTotal bots created: {len(created)}")
