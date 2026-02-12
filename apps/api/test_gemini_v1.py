"""
Minimal Vision Service Test for Gemini v1 Fix
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.vision_service import VisionService
from app.core.config import settings

def create_test_image():
    """Create a minimal valid PNG image (1x1 red pixel)."""
    return bytes([
        0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,
        0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,
        0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
        0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,  
        0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,
        0x54, 0x78, 0x9C, 0x63, 0xF8, 0xCF, 0xC0, 0x00,
        0x00, 0x00, 0x03, 0x00, 0x01, 0x00, 0x18, 0xDD,
        0x8D, 0xB4, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45,
        0x4E, 0x44, 0xAE, 0x42, 0x60, 0x82
    ])

async def test_gemini_v1():
    print("🚀 Testing Gemini v1 API with gemini-1.5-flash...")
    image_bytes = create_test_image()
    
    # Force Gemini provider for this test
    original_provider = settings.VISION_MODEL_PROVIDER
    settings.VISION_MODEL_PROVIDER = "gemini"
    
    try:
        result = await VisionService.analyze_image(
            image_bytes=image_bytes,
            user_context="test",
            quick_mode=True
        )
        print(f"✅ Success! Confidence: {result.confidence}")
        print(f"   Response: {result.raw_description}")
    except Exception as e:
        print(f"❌ Failed: {e}")
    finally:
        settings.VISION_MODEL_PROVIDER = original_provider

if __name__ == "__main__":
    asyncio.run(test_gemini_v1())
