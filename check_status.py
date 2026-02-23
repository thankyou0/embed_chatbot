"""
Quick test to check if GROQ API keys have reset their rate limits.
Also checks actual pages crawled for all chatbots.
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def login():
    r = requests.post(f"{BASE_URL}/auth/login", json={"email": "max@gmail.com", "password": "12345678"}, timeout=15)
    r.raise_for_status()
    return r.json()["access_token"]

def test_chat(token, chatbot_id, message="Hello, what products do you have?"):
    """Test a single chat message to see if GROQ keys work"""
    import sseclient
    headers = {"Authorization": f"Bearer {token}", "Accept": "text/event-stream"}
    try:
        r = requests.post(
            f"{BASE_URL}/chat/{chatbot_id}/message/stream",
            headers=headers,
            json={"message": message, "session_id": "groq-test-001"},
            stream=True,
            timeout=30
        )
        full_response = ""
        for line in r.iter_lines(decode_unicode=True):
            if line and line.startswith("data: "):
                data = line[6:]
                if data == "[DONE]":
                    break
                try:
                    parsed = json.loads(data)
                    if "content" in parsed:
                        full_response += parsed["content"]
                    elif "error" in parsed:
                        return f"ERROR: {parsed['error']}"
                except:
                    full_response += data
        return full_response[:200] if full_response else "EMPTY RESPONSE"
    except Exception as e:
        return f"EXCEPTION: {str(e)[:200]}"

def get_knowledge_sources(token, chatbot_id):
    """Get knowledge sources for a chatbot"""
    try:
        r = requests.get(f"{BASE_URL}/chatbots/{chatbot_id}/knowledge-sources",
            headers={"Authorization": f"Bearer {token}"}, timeout=15)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return []

def main():
    token = login()
    print("Logged in\n")
    
    # Get all chatbots
    r = requests.get(f"{BASE_URL}/chatbots/", headers={"Authorization": f"Bearer {token}"}, timeout=15)
    chatbots = r.json().get("chatbots", r.json()) if isinstance(r.json(), dict) else r.json()
    
    print("=" * 70)
    print("ALL CHATBOTS & KNOWLEDGE STATUS")
    print("=" * 70)
    
    for bot in chatbots:
        bot_id = bot["id"]
        name = bot["name"]
        sources = get_knowledge_sources(token, bot_id)
        total_pages = sum(s.get("pages_found", 0) for s in sources)
        source_status = ", ".join([f"{s.get('source_url', '?')[:30]}={s.get('status','?')}({s.get('pages_found',0)}p)" for s in sources[:3]])
        print(f"\n{name} ({bot_id}):")
        print(f"  Pages total: {total_pages}")
        print(f"  Sources: {source_status or 'none'}")
    
    # Test GROQ with the bot that has most pages (ramraj)
    print("\n" + "=" * 70)
    print("GROQ API KEY TEST")
    print("=" * 70)
    
    # Test with ramraj which has data
    test_bot = "182f88cd-02d8-4c94-824d-b41432847400"  # ramraj
    result = test_chat(token, test_bot, "What products do you sell?")
    print(f"\nChat test result: {result}")
    
    if "rate" in result.lower() or "limit" in result.lower() or "429" in result.lower():
        print("\n>>> GROQ keys still rate limited!")
    elif "error" in result.lower() or "exception" in result.lower():
        print(f"\n>>> Chat error - may need different key")
    else:
        print("\n>>> GROQ keys working! Ready for testing.")

if __name__ == "__main__":
    main()
