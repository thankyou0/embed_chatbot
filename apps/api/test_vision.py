"""
Quick test script for vision service
Run: python test_vision.py
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.vision_service import VisionService
from app.core.config import settings

# Test image URL (a simple product image)
TEST_IMAGE_URL = "https://via.placeholder.com/400x400/FF5733/FFFFFF?text=Red+Shoes"


async def test_vision_service():
    """Test the vision service with different providers."""
    print("=" * 60)
    print("VISION SERVICE TEST")
    print("=" * 60)
    
    # Check configuration
    print("\n📋 Configuration:")
    print(f"  - VISION_MODEL_PROVIDER: {settings.VISION_MODEL_PROVIDER}")
    print(f"  - GEMINI_API_KEY: {'✅ Set' if settings.GEMINI_API_KEY else '❌ Not set'}")
    print(f"  - GROQ_API_KEY: {'✅ Set' if settings.GROQ_API_KEY else '❌ Not set'}")
    
    if not settings.GEMINI_API_KEY and not settings.GROQ_API_KEY:
        print("\n❌ ERROR: No API keys configured!")
        print("Please set GEMINI_API_KEY or GROQ_API_KEY in your .env file")
        return
    
    # Test with a sample image
    print("\n🔍 Testing with sample image...")
    
    try:
        # Download test image
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(TEST_IMAGE_URL)
            image_bytes = response.content
        
        print(f"  - Image downloaded: {len(image_bytes)} bytes")
        
        # Test vision analysis
        print("\n⏳ Running vision analysis...")
        result = await VisionService.analyze_image(
            image_bytes=image_bytes,
            user_context="What product is this?",
            quick_mode=False
        )
        
        # Display results
        print("\n✅ Analysis Results:")
        print(f"  - Confidence: {result.confidence:.2f}")
        print(f"  - Product Type: {result.product_type or 'N/A'}")
        print(f"  - Category: {result.category or 'N/A'}")
        print(f"  - Primary Color: {result.primary_color or 'N/A'}")
        print(f"  - Style: {result.style or 'N/A'}")
        print(f"  - Material: {result.material or 'N/A'}")
        print(f"  - Needs Clarification: {result.needs_clarification}")
        
        if result.needs_clarification:
            print(f"  - Question: {result.clarification_question}")
        
        # Test query building
        print("\n🔎 Query Building Test:")
        primary, detailed = VisionService.build_combined_query(
            user_message="show me similar ones",
            image_attrs=result
        )
        print(f"  - Primary Query: {primary}")
        print(f"  - Detailed Query: {detailed}")
        
        # Test LLM context formatting
        print("\n💬 LLM Context Format:")
        context = VisionService.format_image_context_for_llm(result)
        print(context if context else "  (No context generated)")
        
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


async def test_both_providers():
    """Test both Gemini and Groq providers."""
    print("\n" + "=" * 60)
    print("TESTING BOTH PROVIDERS")
    print("=" * 60)
    
    # Simple test image (1x1 red pixel)
    red_pixel_png = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf'
        b'\xc0\x00\x00\x00\x03\x00\x01\x00\x17\x00\x05\xf5\xd9\x00\x00\x00'
        b'\x00IEND\xaeB`\x82'
    )
    
    providers_to_test = []
    if settings.GEMINI_API_KEY:
        providers_to_test.append("gemini")
    if settings.GROQ_API_KEY:
        providers_to_test.append("groq")
    
    for provider in providers_to_test:
        print(f"\n🧪 Testing {provider.upper()}...")
        
        # Temporarily override provider
        original = settings.VISION_MODEL_PROVIDER
        settings.VISION_MODEL_PROVIDER = provider
        
        try:
            result = await VisionService.analyze_image(
                image_bytes=red_pixel_png,
                user_context="test image",
                quick_mode=True  # Use quick mode for faster testing
            )
            
            print(f"  ✅ {provider.upper()} works!")
            print(f"     Confidence: {result.confidence:.2f}")
            
        except Exception as e:
            print(f"  ❌ {provider.upper()} failed: {e}")
        
        finally:
            settings.VISION_MODEL_PROVIDER = original


if __name__ == "__main__":
    print("\n🚀 Starting Vision Service Tests...\n")
    
    # Run main test
    asyncio.run(test_vision_service())
    
    # Test both providers
    asyncio.run(test_both_providers())
    
    print("\n✨ Testing complete!\n")
