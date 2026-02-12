"""
Script to list available Gemini models to debug 404
"""
import asyncio
import httpx
from app.core.config import settings

async def list_models():
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        print("❌ GEMINI_API_KEY not set")
        return
    
    # Try listing models
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    
    async with httpx.AsyncClient() as client:
        try:
            print(f"Listing models from: {url}")
            response = await client.get(url)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                models = response.json()
                print("Available models:")
                for m in models.get('models', []):
                    print(f" - {m.get('name')}")
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(list_models())
