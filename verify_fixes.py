"""Quick verification of suggestion extraction and language fixes."""
import requests, json, time

API = "http://localhost:8000"
EMAIL = "max@gmail.com"
PASSWORD = "12345678"

# DeathWish bot (en, hi)
BOT_ID = "99fc3604-99e7-4cd0-a2a6-509ac08d9fd0"

def login():
    r = requests.post(f"{API}/api/v1/auth/login", json={"email": EMAIL, "password": PASSWORD})
    return r.json()["access_token"]

def chat(token, msg, label):
    print(f"\n{'='*60}")
    print(f"TEST: {label}")
    print(f"QUERY: {msg}")
    print(f"{'='*60}")
    
    full = ""
    suggestions = []
    is_irrelevant = False
    is_missing = False
    
    r = requests.post(
        f"{API}/api/v1/chat/{BOT_ID}/message/stream",
        headers={"Authorization": f"Bearer {token}"},
        data={"message": msg, "session_id": f"verify_{label}_{int(time.time())}", "is_preview": "true"},
        stream=True,
        timeout=60
    )
    
    for line in r.iter_lines(decode_unicode=True):
        if line and line.startswith("data: "):
            try:
                evt = json.loads(line[6:])
                if evt.get("type") == "content":
                    full += evt.get("content", "")
                elif evt.get("type") == "done":
                    suggestions = evt.get("suggestions", [])
                    is_irrelevant = evt.get("is_irrelevant", False)
                    is_missing = evt.get("is_missing_info", False)
            except:
                pass
    
    print(f"RESPONSE: {full[:300]}")
    print(f"SUGGESTIONS: {suggestions}")
    print(f"IRRELEVANT: {is_irrelevant} | MISSING: {is_missing}")
    
    has_json_leak = "```json" in full or ('["' in full and '"]' in full)
    if has_json_leak:
        print("FAIL: JSON LEAK in response!")
    else:
        print("PASS: No JSON leak")
    
    if suggestions:
        print(f"PASS: {len(suggestions)} suggestions extracted")
    else:
        print("WARN: No suggestions")
    
    return full, suggestions

token = login()
print("Logged in")

chat(token, "500 रुपये से कम के coffee बताओ", "hindi_price")
time.sleep(3)
chat(token, "रिटर्न पॉलिसी क्या है?", "hindi_policy")
time.sleep(3)
chat(token, "चांद पर कौन गया था?", "hindi_irrelevant")
time.sleep(3)
chat(token, "What's the thread count of your premium fabric?", "en_missing")
time.sleep(3)
chat(token, "Tell me a joke", "en_joke")
