"""
Real-world Vision Service Test with actual image URL
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.services.vision_service import VisionService
from app.core.config import settings
import httpx


async def test_with_real_image():
    """Test with a real product image from the internet."""
    print("=" * 70)
    print("VISION SERVICE - REAL IMAGE TEST")
    print("=" * 70)
    
    # Check configuration
    print("\n📋 Configuration:")
    print(f"  Provider: {settings.VISION_MODEL_PROVIDER}")
    print(f"  GEMINI_API_KEY: {'✅' if settings.GEMINI_API_KEY else '❌'}")
    print(f"  GROQ_API_KEY: {'✅' if settings.GROQ_API_KEY else '❌'}")
    
    if not settings.GEMINI_API_KEY and not settings.GROQ_API_KEY:
        print("\n❌ No API keys configured!")
        return
    
    # Use a real, accessible product image
    test_images = [
        {
            "url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400",
            "description": "Red Nike sneakers"
        },
        {
            "url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400",
            "description": "Watch/timepiece"
        }
    ]
    
    for test_img in test_images:
        print(f"\n📸 Testing with: {test_img['description']}")
        print(f"   URL: {test_img['url'][:60]}...")
        print("-" * 70)
        
        try:
            # Download image
            async with httpx.AsyncClient() as client:
                response = await client.get(test_img['url'], timeout=30.0)
                if response.status_code != 200:
                    print(f"   ❌ Failed to download: HTTP {response.status_code}")
                    continue
                
                image_bytes = response.content
                print(f"   ✓ Downloaded: {len(image_bytes)} bytes")
            
            # Analyze image
            print("   ⏳ Analyzing...")
            result = await VisionService.analyze_image(
                image_bytes=image_bytes,
                user_context="What product is this?",
                quick_mode=False
            )
            
            # Display results
            print(f"\n   📊 Results:")
            print(f"      Confidence: {result.confidence:.2f}")
            print(f"      Product: {result.product_type or 'Unknown'}")
            print(f"      Category: {result.category or 'Unknown'}")
            print(f"      Color: {result.primary_color or 'Unknown'}")
            print(f"      Style: {result.style or 'Unknown'}")
            print(f"      Material: {result.material or 'Unknown'}")
            
            if result.secondary_colors:
                print(f"      Secondary Colors: {', '.join(result.secondary_colors)}")
            
            if result.notable_features:
                print(f"      Features: {', '.join(result.notable_features[:3])}")
            
            if result.needs_clarification:
                print(f"      ⚠️  {result.clarification_question}")
            
            # Test query building
            primary, detailed = VisionService.build_combined_query(
                user_message="show me similar ones",
                image_attrs=result
            )
            
            print(f"\n   🔍 Generated Queries:")
            print(f"      Primary: {primary}")
            print(f"      Detailed: {detailed}")
            
            print("\n   ✅ SUCCESS")
            
        except httpx.TimeoutException:
            print(f"   ❌ Timeout downloading image")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()


if __name__ == "__main__":
    print("\n🚀 Testing Vision Service with Real Images...\n")
    asyncio.run(test_with_real_image())
    print("✨ Test complete!\n")
