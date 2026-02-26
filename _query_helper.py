
import requests, json, sys

API = "http://localhost:8000/api/v1"
bot_id = sys.argv[1]
query = sys.argv[2]
session_id = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] != "NONE" else None

s = requests.Session()
r = s.post(f"{API}/auth/login", json={"email":"max@gmail.com","password":"12345678"})
token = r.json()["access_token"]

data = {"message": query}
if session_id:
    data["session_id"] = session_id

try:
    resp = s.post(
        f"{API}/chat/{bot_id}/message/stream",
        data=data,
        headers={"Authorization": f"Bearer {token}"},
        stream=True,
        timeout=40
    )

    full_text = ""
    session = None
    tags = []
    suggestions = []
    products = []
    error = None

    for line in resp.iter_lines(decode_unicode=True):
        if not line or not line.startswith("data: "):
            continue
        payload = line[6:]
        if payload == "[DONE]":
            break
        try:
            evt = json.loads(payload)
            etype = evt.get("type", "")
            if etype == "session":
                session = evt.get("session_id")
            elif etype == "content":
                full_text += evt.get("content", "") or evt.get("text", "")
            elif etype == "done":
                tags = evt.get("tags", [])
                suggestions = evt.get("suggestions", [])
                products = evt.get("products", [])
                error = evt.get("error")
        except:
            pass

    result = {
        "text": full_text[:800],
        "session_id": session,
        "tags": tags,
        "suggestions": suggestions[:4],
        "product_count": len(products),
        "products": [{
            "name": p.get("name", "?")[:50],
            "price": p.get("price") or p.get("formatted_price", ""),
        } for p in products[:5]],
        "text_len": len(full_text),
        "error": error,
        "ok": True
    }
    print(json.dumps(result, ensure_ascii=False))
except requests.exceptions.Timeout:
    print(json.dumps({"ok": False, "error": "timeout"}))
except Exception as e:
    print(json.dumps({"ok": False, "error": str(e)[:200]}))
