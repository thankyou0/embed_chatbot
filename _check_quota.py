import requests, json

s = requests.Session()
r = s.post('http://localhost:8000/api/v1/auth/login', json={'email':'max@gmail.com','password':'12345678'})
token = r.json()['access_token']
s.headers.update({'Authorization': f'Bearer {token}'})

# List all bots
bots = s.get('http://localhost:8000/api/v1/chatbots/')
bot_data = bots.json()
if isinstance(bot_data, dict) and 'chatbots' in bot_data:
    bot_list = bot_data['chatbots']
else:
    bot_list = bot_data if isinstance(bot_data, list) else []

print(f"Total bots: {len(bot_list)}")
total_pages = 0
for b in bot_list:
    # Get knowledge sources for each bot to check pages
    ks_r = s.get(f'http://localhost:8000/api/v1/chatbots/{b["id"]}/knowledge-sources')
    pages = 0
    ks_status = "no-ks"
    if ks_r.ok:
        ks_data = ks_r.json()
        if isinstance(ks_data, list):
            for ks in ks_data:
                pages += ks.get('page_count', 0) or 0
                ks_status = ks.get('status', '?')
        elif isinstance(ks_data, dict):
            for ks in ks_data.get('knowledge_sources', ks_data.get('items', [])):
                pages += ks.get('page_count', 0) or 0
                ks_status = ks.get('status', '?')
    total_pages += pages
    print(f"  {b['name']:30s} | pages={pages:4d} | ks={ks_status} | id={b['id']}")

print(f"\nTotal pages across all bots: {total_pages}")

print(f"\nTotal pages across all bots: {total_pages}")

# Check a few bots' KS in detail
for b in bot_list[:3]:
    ks_r = s.get(f'http://localhost:8000/api/v1/chatbots/{b["id"]}/knowledge-sources')
    print(f"\n--- {b['name']} ---")
    print(json.dumps(ks_r.json(), indent=2, default=str)[:500])

# Check quota via DB 
import subprocess
result = subprocess.run(['docker', 'exec', 'chatbot_postgres', 'psql', '-U', 'postgres', '-d', 'chatbot', '-c',
    "SELECT t.name, t.page_quota, (SELECT COUNT(*) FROM pages p JOIN knowledge_sources ks ON p.knowledge_source_id=ks.id JOIN chatbots c ON ks.chatbot_id=c.id WHERE c.tenant_id=t.id) as used_pages FROM tenants t WHERE t.id=3;"],
    capture_output=True, text=True)
print("\nQuota from DB:")
print(result.stdout)
print(result.stderr[:200] if result.stderr else "")
