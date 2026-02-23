"""Check API keys configuration and rotation."""
from app.core.config import settings, get_groq_api_key, get_openrouter_api_key

print("=== API KEYS STATUS ===")
or_keys = settings.OPENROUTER_API_KEYS
or_key = settings.OPENROUTER_API_KEY
groq_keys = settings.GROQ_API_KEYS
groq_key = settings.GROQ_API_KEY

or_count = len([k for k in or_keys.split(",") if k.strip()]) if or_keys else 0
groq_count = len([k for k in groq_keys.split(",") if k.strip()]) if groq_keys else 0

print(f"OPENROUTER_API_KEYS (multi): {or_count} keys configured")
print(f"OPENROUTER_API_KEY (single): {'SET' if or_key else 'NOT SET'}")
print(f"GROQ_API_KEYS (multi): {groq_count} keys configured")
print(f"GROQ_API_KEY (single): {'SET' if groq_key else 'NOT SET'}")
print()
print("=== MODELS ===")
print(f"OpenRouter Call1: {settings.OPENROUTER_CALL1_MODEL}")
print(f"OpenRouter Call2: {settings.OPENROUTER_CALL2_MODEL}")
print(f"OpenRouter Trans: {settings.OPENROUTER_TRANSLATION_MODEL}")
print(f"Groq Call1: {settings.GROQ_CALL1_MODEL}")
print(f"Groq Call2: {settings.GROQ_CALL2_MODEL}")
print(f"Groq Trans: {settings.GROQ_TRANSLATION_MODEL}")
print()
print("=== KEY ROTATION TEST ===")
print("OpenRouter keys (5 calls):")
for i in range(5):
    k = get_openrouter_api_key()
    suffix = k[-8:] if k else "NONE"
    print(f"  Call {i+1}: ...{suffix}")
print("Groq keys (5 calls):")
for i in range(5):
    k = get_groq_api_key()
    suffix = k[-8:] if k else "NONE"
    print(f"  Call {i+1}: ...{suffix}")
