"""
Test the new LLM-powered query builder.
This tests the generalized approach that handles all types of image + text queries.
"""
import asyncio
import json
from app.services.vision_service import VisionService, ImageAttributes


async def test_llm_query_builder():
    """Test various query combinations with the LLM-powered builder."""
    
    print("\n" + "="*70)
    print("TESTING LLM-POWERED QUERY BUILDER")
    print("="*70)
    
    # Test cases: (image_attrs, user_message, expected_behavior)
    test_cases = [
        # Case 1: Color transfer - take color from image, product from text
        {
            "name": "Color Transfer (image color → different product)",
            "image": ImageAttributes(
                product_type="sneakers",
                category="footwear",
                primary_color="light blue",
                style="casual",
                gender_target="unisex",
                confidence=0.95
            ),
            "user_message": "show me this color shirts",
            "expected_contains": ["light blue", "shirt"]
        },
        
        # Case 2: Gender override - keep product, change audience
        {
            "name": "Gender Override (kids shirt → mens)",
            "image": ImageAttributes(
                product_type="Short-sleeved button-up shirt",
                category="Clothing",
                subcategory="Traditional/Ethnic Shirt",
                primary_color="Royal Blue",
                material="Art Silk Fabric",
                style="Traditional",
                gender_target="kids",
                confidence=0.95
            ),
            "user_message": "can you have same color shirt given in image but for mens",
            "expected_contains": ["blue", "shirt", "men"]
        },
        
        # Case 3: Full attribute override
        {
            "name": "Full Override (user specifies everything different)",
            "image": ImageAttributes(
                product_type="full sleeve shirt",
                primary_color="orange",
                style="casual",
                confidence=0.90
            ),
            "user_message": "show me red shirt with half sleeve",
            "expected_contains": ["red", "half sleeve", "shirt"]
        },
        
        # Case 4: Exact match request
        {
            "name": "Exact Match (do you have this)",
            "image": ImageAttributes(
                product_type="small toy car",
                category="toys",
                primary_color="red",
                material="plastic",
                confidence=0.88
            ),
            "user_message": "do you have this one",
            "expected_contains": ["toy car", "red"]
        },
        
        # Case 5: Similar but cheaper
        {
            "name": "Similar with Modifier (similar but cheaper)",
            "image": ImageAttributes(
                product_type="leather handbag",
                primary_color="brown",
                style="elegant",
                gender_target="women",
                confidence=0.92
            ),
            "user_message": "similar but cheaper",
            "expected_contains": ["handbag", "budget"]
        },
        
        # Case 6: Style transfer
        {
            "name": "Style Transfer (same product, different style)",
            "image": ImageAttributes(
                product_type="dress",
                primary_color="black",
                style="formal",
                occasion="party",
                confidence=0.90
            ),
            "user_message": "show me this in casual style",
            "expected_contains": ["dress", "casual"]
        },
    ]
    
    results = []
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'─'*70}")
        print(f"TEST {i}: {test['name']}")
        print(f"{'─'*70}")
        
        image = test["image"]
        user_msg = test["user_message"]
        expected = test["expected_contains"]
        
        print(f"📷 Image: {image.product_type} | {image.primary_color} | for {image.gender_target}")
        print(f"💬 User: \"{user_msg}\"")
        print(f"🎯 Expected keywords: {expected}")
        
        try:
            # Test LLM-powered method
            query, intent, detailed = await VisionService.build_query_with_llm(
                user_message=user_msg,
                image_attrs=image
            )
            
            print(f"\n✅ LLM Result:")
            print(f"   Intent: {intent}")
            print(f"   Query: \"{query}\"")
            print(f"   Details: {detailed}")
            
            # Check if expected keywords are present
            query_lower = query.lower()
            found = [kw for kw in expected if kw.lower() in query_lower]
            missing = [kw for kw in expected if kw.lower() not in query_lower]
            
            if intent == "fallback":
                print(f"   ⚠️  LLM failed, using fallback heuristic")
            
            if missing:
                print(f"   ⚠️  Missing: {missing}")
                results.append(("PARTIAL", test['name'], query, missing))
            else:
                print(f"   ✓ All expected keywords found!")
                results.append(("PASS", test['name'], query, []))
                
        except Exception as e:
            import traceback
            print(f"\n❌ Error: {type(e).__name__}: {e}")
            traceback.print_exc()
            results.append(("FAIL", test['name'], str(e), expected))
        
        # Also test fallback method for comparison
        try:
            fallback_query, _ = VisionService.build_combined_query(
                user_message=user_msg,
                image_attrs=image
            )
            print(f"\n📌 Fallback Query: \"{fallback_query}\"")
        except Exception as e:
            print(f"   Fallback error: {e}")
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    passed = sum(1 for r in results if r[0] == "PASS")
    partial = sum(1 for r in results if r[0] == "PARTIAL")
    failed = sum(1 for r in results if r[0] == "FAIL")
    
    print(f"✅ Passed:  {passed}/{len(results)}")
    print(f"⚠️  Partial: {partial}/{len(results)}")
    print(f"❌ Failed:  {failed}/{len(results)}")
    
    print("\nDetailed Results:")
    for status, name, query, issues in results:
        icon = "✅" if status == "PASS" else "⚠️" if status == "PARTIAL" else "❌"
        print(f"  {icon} {name}")
        print(f"     Query: \"{query}\"")
        if issues:
            print(f"     Issues: {issues}")
    
    return passed, partial, failed


if __name__ == "__main__":
    asyncio.run(test_llm_query_builder())
