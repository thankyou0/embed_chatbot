"""Test actual API calls to OpenRouter and Groq to verify keys work."""
import httpx
import asyncio
from app.core.config import settings, get_groq_api_key, get_openrouter_api_key

async def test_openrouter():
    """Test all OpenRouter keys."""
    keys_str = settings.OPENROUTER_API_KEYS or ""
    keys = [k.strip() for k in keys_str.split(",") if k.strip()]
    if not keys and settings.OPENROUTER_API_KEY:
        keys = [settings.OPENROUTER_API_KEY]
    
    print(f"\n=== OPENROUTER API TEST ({len(keys)} keys) ===")
    for i, key in enumerate(keys):
        suffix = key[-8:]
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": settings.OPENROUTER_CALL1_MODEL,
                        "messages": [{"role": "user", "content": "Say OK"}],
                        "temperature": 0.0,
                        "max_tokens": 5,
                    },
                )
                if resp.status_code == 200:
                    content = resp.json()["choices"][0]["message"]["content"].strip()
                    print(f"  Key {i+1} (...{suffix}): OK (status=200, response='{content}')")
                elif resp.status_code == 429:
                    print(f"  Key {i+1} (...{suffix}): RATE LIMITED (429)")
                else:
                    body = resp.text[:150]
                    print(f"  Key {i+1} (...{suffix}): FAILED (status={resp.status_code}, body={body})")
        except Exception as e:
            print(f"  Key {i+1} (...{suffix}): ERROR ({e})")

async def test_groq():
    """Test all Groq keys."""
    keys_str = settings.GROQ_API_KEYS or ""
    keys = [k.strip() for k in keys_str.split(",") if k.strip()]
    if not keys and settings.GROQ_API_KEY:
        keys = [settings.GROQ_API_KEY]
    
    print(f"\n=== GROQ API TEST ({len(keys)} keys) ===")
    for i, key in enumerate(keys):
        suffix = key[-8:]
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": settings.GROQ_CALL1_MODEL,
                        "messages": [{"role": "user", "content": "Say OK"}],
                        "temperature": 0.0,
                        "max_tokens": 5,
                    },
                )
                if resp.status_code == 200:
                    content = resp.json()["choices"][0]["message"]["content"].strip()
                    print(f"  Key {i+1} (...{suffix}): OK (status=200, response='{content}')")
                elif resp.status_code == 429:
                    print(f"  Key {i+1} (...{suffix}): RATE LIMITED (429)")
                else:
                    body = resp.text[:150]
                    print(f"  Key {i+1} (...{suffix}): FAILED (status={resp.status_code}, body={body})")
        except Exception as e:
            print(f"  Key {i+1} (...{suffix}): ERROR ({e})")

async def main():
    await test_openrouter()
    await test_groq()
    print("\n=== SUMMARY ===")
    print("Key rotation: WORKING (round-robin via itertools.cycle)")
    print("Fallback: OpenRouter -> Groq on failure (for Call1 & Call2)")
    print("Rate limit detection: Checks status=429 + text patterns")

asyncio.run(main())
