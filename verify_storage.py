import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import sys
from pathlib import Path

# Add apps/api to path so we can import app
api_path = Path(__file__).resolve().parent / "apps" / "api"
sys.path.append(str(api_path))

from app.services.file_service import FileService
from app.core.config import settings

async def test_upload():
    print("--- Storage Verification ---")
    print(f"Endpoint: {settings.S3_ENDPOINT_URL}")
    print(f"Bucket: {settings.S3_BUCKET_NAME}")
    
    test_content = b"This is a test file for Supabase Storage verification."
    test_filename = "test_verification.txt"
    test_dir = "test-uploads"
    
    try:
        print(f"Attempting to upload {test_filename}...")
        url = await FileService.save_file(test_content, test_dir, test_filename)
        
        print("\nSUCCESS!")
        print(f"Status: File uploaded successfully.")
        print(f"Public URL: {url}")
        print("\nCopy the URL above and paste it in your browser. If you see the text, everything is configured correctly!")
        
    except Exception as e:
        print("\nFAILED!")
        print(f"Error: {str(e)}")
        print("\nSuggestions:")
        print("1. Ensure your 'chatbot-uploads' bucket exists in Supabase Storage.")
        print("2. Ensure the bucket is set to 'Public'.")
        print("3. Check your S3_SECRET_ACCESS_KEY in .env.")

if __name__ == "__main__":
    asyncio.run(test_upload())
