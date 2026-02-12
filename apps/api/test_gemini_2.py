import httpx
import base64
import os
import json
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
model = "gemini-flash-latest"
url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

# Tiny 1x1 black PNG
TINY_IMAGE_B64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

try:
    payload = {
        "contents": [{
            "parts": [
                {"text": "What color is this 1x1 pixel?"},
                {
                    "inline_data": {
                        "mime_type": "image/png",
                        "data": TINY_IMAGE_B64
                    }
                }
            ]
        }]
    }

    print(f"Testing Gemini {model} connectivity...")
    with httpx.Client() as client:
        response = client.post(url, json=payload, headers={'Content-Type': 'application/json'}, timeout=30.0)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Success!")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Error: {response.text}")

except Exception as e:
    print(f"Failed: {str(e)}")
