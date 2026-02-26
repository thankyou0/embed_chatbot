#!/usr/bin/env python3
"""Quick debug: check if apostrophe encoding matches."""

# Test with ASCII apostrophe
content = "I don\u0027t have the specific details on tentree's return"
_resp_lower = content.lower()
patterns = ["i don\u0027t have that", "i don\u0027t have the", "i don\u0027t have specific"]
print("=== ASCII apostrophe test ===")
for p in patterns:
    found = p in _resp_lower
    print(f"  [{p}] -> {found}")

# Test with Unicode right single quote
content2 = "I don\u2019t have the specific details on tentree\u2019s return"
_resp_lower2 = content2.lower()
print("\n=== Unicode U+2019 apostrophe test ===")
for p in patterns:
    found = p in _resp_lower2
    print(f"  [{p}] -> {found}")

# Now test what actual LLM response looks like
# Let's check by making a real API call
import httpx, json, uuid

BASE = "http://localhost:8000/api/v1"
AUTH = {"email": "max@gmail.com", "password": "12345678"}

with httpx.Client() as c:
    r = c.post(f"{BASE}/auth/login", json=AUTH)
    token = r.json()["access_token"]

session_id = str(uuid.uuid4())
full_text = ""
with httpx.Client(timeout=httpx.Timeout(120.0, read=120.0)) as client:
    with client.stream(
        "POST",
        f"{BASE}/chat/799637f9-391b-4b9d-84cb-5fdd17cdf109/message/stream",
        headers={"Authorization": f"Bearer {token}"},
        data={"message": "What is your return policy?", "session_id": session_id},
    ) as resp:
        for line in resp.iter_lines():
            line = line.strip()
            if not line or not line.startswith("data: "):
                continue
            raw = line[6:]
            if raw == "[DONE]":
                break
            try:
                chunk = json.loads(raw)
                if chunk.get("type") == "content":
                    full_text += chunk.get("content", "")
            except json.JSONDecodeError:
                pass

print(f"\n=== Actual LLM response ===")
print(f"Text: {full_text[:200]}")
print(f"\n=== Character analysis of 'don't' in response ===")
lower = full_text.lower()
idx = lower.find("don")
if idx >= 0:
    snippet = lower[idx:idx+10]
    print(f"Snippet: {repr(snippet)}")
    for i, c in enumerate(snippet):
        print(f"  [{i}] char={repr(c)} ord={ord(c)} hex={hex(ord(c))}")
else:
    print("'don' not found in response")

# Test our patterns against actual response
print(f"\n=== Pattern matching against actual response ===")
all_patterns = [
    "i don't have that",
    "i don't have the",
    "i don't have specific",
    "i don't have information",
    "i do not have",
    "don't have that specific",
    "don't have specific details",
    "not available in our",
    "not mentioned in",
    "no information about",
    "couldn't find that",
    "could not find",
    "not in our data",
    "not in the available",
    "i'm not sure about that",
    "unfortunately, i don't",
    "unfortunately i don't",
    "this information is not available",
    "that information is not available",
    "i don't see that",
    "isn't available in",
    "is not available in",
    "not available right now",
    "we don't have that",
]
for p in all_patterns:
    if p in lower:
        print(f"  MATCH: [{p}]")
if not any(p in lower for p in all_patterns):
    print("  NO MATCHES!")
    print(f"\n  Full response lower: {lower[:500]}")
