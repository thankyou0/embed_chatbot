"""
Generate scope descriptions for test chatbots.
Usage: python generate_scope_descriptions.py
"""

import asyncio
import httpx
import json
import sys

API_BASE = "http://localhost:8000/api/v1"

# Test chatbot IDs from previous testing
TEST_BOTS = {
    "799637f9-391b-4b9d-84cb-5fdd17cdf109": "Crawl-Tentree",
    "99fc3604-99e7-4cd0-a2a6-509ac08d9fd0": "Crawl-Death Wish Coffee",
    "e23fcc6f-7a02-4b09-8d49-95c00a57d852": "Crawl-Beardbrand",
    "182f88cd-02d8-4c94-824d-b41432847400": "ramraj",
    "1cb18dc0-4909-409d-ab03-0436524fcec4": "kriyanta",
    "e79b3754-006d-45d5-b21d-2391710e08ca": "zevaramaze",
}

# Login first
async def login():
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(f"{API_BASE}/auth/login", json={
            "email": "max@gmail.com",
            "password": "12345678"
        })
        if resp.status_code == 200:
            return resp.json().get("access_token")
        print(f"Login failed: {resp.status_code} {resp.text}")
        return None

# Generate scope description by calling the scope service directly via docker exec
async def generate_scope(chatbot_id: str, name: str):
    """Generate scope description by running python inside the docker container."""
    import subprocess
    
    python_code = f"""
import asyncio
from app.services.scope_service import generate_scope_description
from uuid import UUID

async def main():
    result = await generate_scope_description(UUID("{chatbot_id}"))
    if result:
        import json
        print("SUCCESS:" + json.dumps(result, indent=2))
    else:
        print("FAILED: No result")

asyncio.run(main())
"""
    
    result = subprocess.run(
        ["docker", "exec", "chatbot_api", "python", "-c", python_code],
        capture_output=True,
        text=True,
        timeout=60,
    )
    
    if result.returncode == 0:
        output = result.stdout.strip()
        if output.startswith("SUCCESS:"):
            desc = json.loads(output[8:])
            return desc
        else:
            print(f"  Output: {output}")
            if result.stderr:
                print(f"  Stderr: {result.stderr[:300]}")
            return None
    else:
        print(f"  Exit code: {result.returncode}")
        print(f"  Stderr: {result.stderr[:500]}")
        return None


async def main():
    print("=" * 60)
    print("SCOPE DESCRIPTION GENERATOR")
    print("=" * 60)
    
    for bot_id, name in TEST_BOTS.items():
        print(f"\n--- {name} ({bot_id[:8]}...) ---")
        try:
            result = await generate_scope(bot_id, name)
            if result:
                print(f"  Brand: {result.get('brand_name')}")
                print(f"  Business: {result.get('business_type')}")
                print(f"  Sells: {result.get('what_they_sell', '')[:100]}")
                print(f"  Topics: {result.get('topics_covered', [])}")
                print(f"  Not About: {result.get('not_about', '')[:100]}")
            else:
                print("  FAILED to generate")
        except Exception as e:
            print(f"  ERROR: {e}")
    
    # Verify in DB
    import subprocess
    result = subprocess.run(
        ["docker", "exec", "chatbot_postgres", "psql", "-U", "postgres", "-d", "embed_chatbot", "-c",
         "SELECT name, scope_description->>'brand_name' as brand FROM chatbots WHERE scope_description IS NOT NULL AND deleted_at IS NULL;"],
        capture_output=True, text=True
    )
    print(f"\n{'='*60}")
    print("DB VERIFICATION:")
    print(result.stdout)


if __name__ == "__main__":
    asyncio.run(main())
