"""
Simple test script to validate SSE streaming endpoint.
Run this after starting the API server to test the streaming functionality.
"""
import asyncio
import httpx
import json


async def test_streaming_endpoint():
    """Test the streaming chat endpoint."""
    
    # Configuration
    API_URL = "http://localhost:8000"
    CHATBOT_ID = "c24678ae-1d28-4917-b1b7-d23a165a4e68"  # Replace with actual chatbot ID
    
    print("🚀 Testing SSE Streaming Endpoint")
    print("=" * 50)
    
    # Prepare form data
    form_data = {
        "message": "Hello, what can you help me with?",
        "is_preview": "true"
    }
    
    print(f"📤 Sending message: {form_data['message']}")
    print()
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            # Make streaming request
            async with client.stream(
                "POST",
                f"{API_URL}/api/v1/chat/{CHATBOT_ID}/message/stream",
                data=form_data
            ) as response:
                if response.status_code != 200:
                    print(f"❌ Error: HTTP {response.status_code}")
                    error_text = await response.aread()
                    print(f"Response: {error_text.decode()}")
                    return
                
                print("✅ Connected to stream")
                print("📥 Receiving chunks:")
                print("-" * 50)
                
                session_id = None
                content = ""
                suggestions = []
                products = []
                
                # Process SSE stream
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        try:
                            chunk = json.loads(data)
                            
                            if chunk["type"] == "session":
                                session_id = chunk["session_id"]
                                print(f"🆔 Session ID: {session_id}")
                            
                            elif chunk["type"] == "content":
                                content += chunk["content"]
                                print(chunk["content"], end="", flush=True)
                            
                            elif chunk["type"] == "done":
                                print("\n" + "-" * 50)
                                print("✅ Stream completed")
                                suggestions = chunk.get("suggestions", [])
                                products = chunk.get("products", [])
                                
                                print(f"\n📊 Metadata:")
                                print(f"  - Sources: {len(chunk.get('sources', []))}")
                                print(f"  - Suggestions: {len(suggestions)}")
                                print(f"  - Products: {len(products)}")
                                
                                if suggestions:
                                    print(f"\n💡 Suggestions:")
                                    for i, sug in enumerate(suggestions, 1):
                                        print(f"  {i}. {sug}")
                                
                                if products:
                                    print(f"\n🛍️  Products:")
                                    for i, prod in enumerate(products[:3], 1):
                                        print(f"  {i}. {prod.get('name', 'N/A')} - {prod.get('price', 'N/A')}")
                            
                            elif chunk["type"] == "error":
                                print(f"\n❌ Error: {chunk.get('error', 'Unknown error')}")
                        
                        except json.JSONDecodeError as e:
                            print(f"\n⚠️  Failed to parse chunk: {e}")
                
                print("\n" + "=" * 50)
                print("✅ Test completed successfully!")
        
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            import traceback
            traceback.print_exc()


async def test_non_streaming_endpoint():
    """Test the original non-streaming endpoint for comparison."""
    
    API_URL = "http://localhost:8000"
    CHATBOT_ID = "c24678ae-1d28-4917-b1b7-d23a165a4e68"  # Replace with actual chatbot ID
    
    print("\n🚀 Testing Non-Streaming Endpoint (for comparison)")
    print("=" * 50)
    
    form_data = {
        "message": "Hello, what can you help me with?",
        "is_preview": "true"
    }
    
    print(f"📤 Sending message: {form_data['message']}")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            import time
            start_time = time.time()
            
            response = await client.post(
                f"{API_URL}/api/v1/chat/{CHATBOT_ID}/message",
                data=form_data
            )
            
            elapsed = time.time() - start_time
            
            if response.status_code != 200:
                print(f"❌ Error: HTTP {response.status_code}")
                return
            
            data = response.json()
            print(f"\n⏱️  Response time: {elapsed:.2f}s")
            print(f"📥 Message: {data['message'][:100]}...")
            print(f"📊 Suggestions: {len(data.get('suggestions', []))}")
            print(f"🛍️  Products: {len(data.get('products', []))}")
        
        except Exception as e:
            print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════╗
║          SSE Streaming Endpoint Test Script               ║
╚════════════════════════════════════════════════════════════╝

Before running this test:
1. Make sure the API server is running (http://localhost:8000)
2. Update CHATBOT_ID in the script with a valid chatbot ID
3. Ensure the chatbot has some knowledge base data

""")
    
    try:
        asyncio.run(test_streaming_endpoint())
        print("\n")
        asyncio.run(test_non_streaming_endpoint())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
