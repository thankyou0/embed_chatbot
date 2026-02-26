#!/usr/bin/env python3
"""Quick single-query debug test."""
import httpx, json, uuid, time, subprocess

BASE = "http://localhost:8000/api/v1"

# Login
with httpx.Client() as c:
    r = c.post(f"{BASE}/auth/login", json={"email": "max@gmail.com", "password": "12345678"})
    token = r.json()["access_token"]

# Send query
session_id = str(uuid.uuid4())
print(f"Client session_id: {session_id}")
full_text = ""
sse_session_id = None

with httpx.Client(timeout=httpx.Timeout(120.0, read=120.0)) as client:
    with client.stream(
        "POST",
        f"{BASE}/chat/799637f9-391b-4b9d-84cb-5fdd17cdf109/message/stream",
        headers={"Authorization": f"Bearer {token}"},
        data={"message": "What is tentree's return policy?", "session_id": session_id},
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
                    print(f"SSE session_id: {sse_session_id}")
            except json.JSONDecodeError:
                pass

print(f"\nResponse: {full_text[:200]}")

# Wait for DB commit
time.sleep(3)

# Query DB
sql = f"""
SELECT cm.metadata_json
FROM chat_messages cm
JOIN chat_sessions cs ON cm.session_id = cs.id
WHERE cs.id = '{sse_session_id}'
  AND cm.role = 'assistant'
ORDER BY cm.created_at DESC
LIMIT 1;
"""
result = subprocess.run(
    ["docker", "exec", "chatbot_postgres", "psql", "-U", "postgres",
     "-d", "embed_chatbot", "-t", "-A", "-c", sql],
    capture_output=True, text=True, timeout=10
)
print(f"\nDB stdout: [{result.stdout.strip()[:300]}]")
print(f"DB stderr: [{result.stderr.strip()[:200]}]")

if result.stdout.strip():
    meta = json.loads(result.stdout.strip())
    print(f"\nis_missing_info: {meta.get('is_missing_info')}")
    print(f"was_answered: {meta.get('was_answered')}")
    print(f"is_irrelevant: {meta.get('is_irrelevant')}")
else:
    print("\nNO DB RESULT FOUND!")
    print(f"Trying with original session_id...")
    sql2 = f"""
    SELECT cm.metadata_json
    FROM chat_messages cm
    JOIN chat_sessions cs ON cm.session_id = cs.id
    WHERE cs.id = '{session_id}'
      AND cm.role = 'assistant'
    ORDER BY cm.created_at DESC
    LIMIT 1;
    """
    result2 = subprocess.run(
        ["docker", "exec", "chatbot_postgres", "psql", "-U", "postgres",
         "-d", "embed_chatbot", "-t", "-A", "-c", sql2],
        capture_output=True, text=True, timeout=10
    )
    print(f"DB stdout with original: [{result2.stdout.strip()[:300]}]")
