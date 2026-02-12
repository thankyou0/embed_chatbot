"""
Simple Vision Service Test for Docker
Tests with actual image data (no external dependencies)
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
    # This is a valid 1x1 red pixel PNG image
    return bytes([
        0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
        0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR chunk
        0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,  # Width=1, Height=1
        0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,  
        0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,  # IDAT chunk
        0x54, 0x78, 0x9C, 0x63, 0xF8, 0xCF, 0xC0, 0x00,  # Red pixel data
        0x00, 0x00, 0x03, 0x00, 0x01, 0x00, 0x18, 0xDD,
        0x8D, 0xB4, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45,  # IEND chunk
        0x4E, 0x44, 0xAE, 0x42, 0x60, 0x82
    ])


async def test_vision_api():
    """Test the vision API with a real image."""
    print("=" * 70)
    print("VISION SERVICE API TEST (Docker)")
    print("=" * 70)
    
    # Check configuration
    print("\n📋 Configuration:")
    print(f"  Provider: {settings.VISION_MODEL_PROVIDER}")
    print(f"  GEMINI_API_KEY: {'✅ Configured' if settings.GEMINI_API_KEY else '❌ Not set'}")
    print(f"  GROQ_API_KEY: {'✅ Configured' if settings.GROQ_API_KEY else '❌ Not set'}")
    
    if not settings.GEMINI_API_KEY and not settings.GROQ_API_KEY:
        print("\n❌ ERROR: No API keys configured!")
        print("Add GEMINI_API_KEY or GROQ_API_KEY to your .env file")
        return False
    
    # Create test image
    print("\n🖼️  Creating test image (1x1 red pixel PNG)...")
    image_bytes = create_test_image()
    print(f"  Image size: {len(image_bytes)} bytes")
    
    # Test 1: Basic analysis
    print("\n🔬 Test 1: Basic Image Analysis")
    print("-" * 70)
    
    try:
        result = await VisionService.analyze_image(
            image_bytes=image_bytes,
            user_context="What color is this?",
            quick_mode=False
        )
        
        print(f"✅ Analysis successful!")
        print(f"   Confidence: {result.confidence:.2f}")
        print(f"   Primary Color: {result.primary_color or 'N/A'}")
        print(f"   Product Type: {result.product_type or 'N/A'}")
        print(f"   Category: {result.category or 'N/A'}")
        
        if result.needs_clarification:
            print(f"   ⚠️  Needs clarification: {result.clarification_question}")
        
    except Exception as e:
        print(f"❌ Test 1 FAILED: {e}")
        return False
    
    # Test 2: Quick mode
    print("\n⚡ Test 2: Quick Mode Analysis")
    print("-" * 70)
    
    try:
        result_quick = await VisionService.analyze_image(
            image_bytes=image_bytes,
            user_context="",
            quick_mode=True
        )
        
        print(f"✅ Quick analysis successful!")
        print(f"   Confidence: {result_quick.confidence:.2f}")
        print(f"   Response: {result_quick.raw_description[:100]}...")
        
    except Exception as e:
        print(f"❌ Test 2 FAILED: {e}")
        return False
    
    # Test 3: Query building
    print("\n🔎 Test 3: Query Building")
    print("-" * 70)
    
    try:
        primary, detailed = VisionService.build_combined_query(
            user_message="show me similar products",
            image_attrs=result
        )
        
        print(f"✅ Query building successful!")
        print(f"   Primary: {primary}")
        print(f"   Detailed: {detailed}")
        
    except Exception as e:
        print(f"❌ Test 3 FAILED: {e}")
        return False
    
    # Test 4: LLM context formatting
    print("\n💬 Test 4: LLM Context Formatting")
    print("-" * 70)
    
    try:
        context = VisionService.format_image_context_for_llm(result)
        print(f"✅ Context formatting successful!")
        if context:
            print(context)
        else:
            print("   (No context - confidence too low)")
        
    except Exception as e:
        print(f"❌ Test 4 FAILED: {e}")
        return False
    
    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED!")
    print("=" * 70)
    return True


async def test_provider_specific():
    """Test specific provider."""
    print("\n" + "=" * 70)
    print("PROVIDER-SPECIFIC TEST")
    print("=" * 70)
    
    image_bytes = create_test_image()
    
    # Determine which provider to test
    if settings.GROQ_API_KEY:
        print("\n🧪 Testing GROQ (Llama 4 Scout)...")
        original = settings.VISION_MODEL_PROVIDER
        settings.VISION_MODEL_PROVIDER = "groq"
        
        try:
            result = await VisionService.analyze_image(
                image_bytes=image_bytes,
                user_context="test",
                quick_mode=True
            )
            
            print(f"✅ GROQ works! Confidence: {result.confidence:.2f}")
            print(f"   Model: {VisionService.PROVIDERS['groq']['model']}")
            
        except Exception as e:
            print(f"❌ GROQ failed: {e}")
        
        finally:
            settings.VISION_MODEL_PROVIDER = original
    
    if settings.GEMINI_API_KEY:
        print("\n🧪 Testing GEMINI...")
        original = settings.VISION_MODEL_PROVIDER
        settings.VISION_MODEL_PROVIDER = "gemini"
        
        try:
            result = await VisionService.analyze_image(
                image_bytes=image_bytes,
                user_context="test",
                quick_mode=True
            )
            
            print(f"✅ GEMINI works! Confidence: {result.confidence:.2f}")
            print(f"   Model: {VisionService.PROVIDERS['gemini']['model']}")
            
        except Exception as e:
            print(f"❌ GEMINI failed: {e}")
        
        finally:
            settings.VISION_MODEL_PROVIDER = original


if __name__ == "__main__":
    print("\n🚀 Starting Vision Service Tests (Docker Environment)...\n")
    
    success = asyncio.run(test_vision_api())
    
    if success:
        asyncio.run(test_provider_specific())
    
    print("\n✨ Testing complete!\n")
