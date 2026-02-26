#!/usr/bin/env python3
import httpx, json, uuid, time, subprocess

BASE = "http://localhost:8000/api/v1"
with httpx.Client() as c:
    r = c.post(f"{BASE}/auth/login", json={"email": "max@gmail.com", "password": "12345678"})
    token = r.json()["access_token"]

session_id = str(uuid.uuid4())
full_text = ""
sse_session_id = None

with httpx.Client(timeout=httpx.Timeout(120.0, read=120.0)) as client:
    with client.stream(
        "POST",
        f"{BASE}/chat/182f88cd-02d8-4c94-824d-b41432847400/message/stream",
        headers={"Authorization": f"Bearer {token}"},
        data={"message": "Hello! How are you?", "session_id": session_id},
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
                elif chunk.get("type") == "session":
                    sse_session_id = chunk.get("session_id")
            except json.JSONDecodeError:
                pass

print(f"Response: {full_text[:200]}")

time.sleep(2)
sql = f"SELECT cm.metadata_json FROM chat_messages cm JOIN chat_sessions cs ON cm.session_id = cs.id WHERE cs.id = '{sse_session_id}' AND cm.role = 'assistant' ORDER BY cm.created_at DESC LIMIT 1;"
result = subprocess.run(
    ["docker", "exec", "chatbot_postgres", "psql", "-U", "postgres", "-d", "embed_chatbot", "-t", "-A", "-c", sql],
    capture_output=True, text=True, timeout=10
)
if result.stdout.strip():
    meta = json.loads(result.stdout.strip())
    print(f"is_irrelevant: {meta.get('is_irrelevant')}")
    print(f"is_missing_info: {meta.get('is_missing_info')}")
    print(f"scope_gated: {meta.get('scope_gated')}")
else:
    print("No DB record")
