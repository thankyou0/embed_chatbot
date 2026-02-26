"""Quick test of scope gate — send a few irrelevant queries and check response."""
import asyncio
import httpx
import json

API = "http://localhost:8000/api/v1"

async def login():
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.post(f"{API}/auth/login", json={"email":"max@gmail.com","password":"12345678"})
        return r.json()["access_token"]

async def send_message(chatbot_id: str, message: str, token: str):
    """Send message and collect full SSE response."""
    url = f"{API}/chat/{chatbot_id}/message/stream"
    headers = {"Authorization": f"Bearer {token}"}
    
    full_text = ""
    products = []
    
    async with httpx.AsyncClient(timeout=60) as client:
        async with client.stream(
            "POST", url,
            headers=headers,
            data={"message": message},
            files={"image": ("", b"", "application/octet-stream")},
        ) as resp:
            async for line in resp.aiter_lines():
                if not line.startswith("data: "):
                    continue
                data = json.loads(line[6:])
                if data.get("type") == "content":
                    full_text += data.get("content", "")
                elif data.get("type") == "done":
                    products = data.get("products", [])
    
    return full_text, products

async def main():
    token = await login()
    
    tests = [
        # (chatbot_id, message, expected: should be IRRELEVANT)
        ("799637f9-391b-4b9d-84cb-5fdd17cdf109", "Who is the prime minister of India?", True),
        ("799637f9-391b-4b9d-84cb-5fdd17cdf109", "How to make biryani at home?", True),
        ("799637f9-391b-4b9d-84cb-5fdd17cdf109", "Best laptops under $1000?", True),
        ("799637f9-391b-4b9d-84cb-5fdd17cdf109", "Show me your jackets", False),
        ("99fc3604-99e7-4cd0-a2a6-509ac08d9fd0", "What is machine learning?", True),
        ("99fc3604-99e7-4cd0-a2a6-509ac08d9fd0", "Tell me about your dark roast", False),
        ("1cb18dc0-4909-409d-ab03-0436524fcec4", "भारत के राष्ट्रपति कौन हैं?", True),
        ("e79b3754-006d-45d5-b21d-2391710e08ca", "ચંદ્ર પર કોણ ગયું છે?", True),
    ]
    
    print(f"{'='*70}")
    print("SCOPE GATE TEST")
    print(f"{'='*70}")
    
    passed = 0
    total = len(tests)
    
    for chatbot_id, msg, expect_irrelevant in tests:
        text, products = await send_message(chatbot_id, msg, token)
        is_irrelevant = (
            "[[IRRELEVANT]]" in text 
            or "I can only help with" in text 
            or "मैं केवल" in text 
            or "હું ફક્ત" in text
            or "main sirf" in text.lower()
            or "hu fakat" in text.lower()
        )
        
        # Check if it was scope-gated (short redirect with no products)
        is_scope_gated = len(text) < 200 and len(products) == 0 and is_irrelevant
        
        status = "✅" if (is_irrelevant == expect_irrelevant) else "❌"
        if is_irrelevant == expect_irrelevant:
            passed += 1
        
        tag = "SCOPE-GATE" if is_scope_gated else ("IRRELEVANT" if is_irrelevant else "ANSWERED")
        
        print(f"\n{status} [{tag}] {msg[:50]}")
        print(f"   Response: {text[:120].replace(chr(10), ' ')}")
        print(f"   Products: {len(products)}")
    
    print(f"\n{'='*70}")
    print(f"RESULTS: {passed}/{total} correct")
    print(f"{'='*70}")

asyncio.run(main())
