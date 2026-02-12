#!/usr/bin/env python3
"""
Test script to validate the vision service query building changes.
Run this inside the Docker container to test image analysis and query merging.
"""

import asyncio
import sys
sys.path.insert(0, '/app')

from app.services.vision_service import VisionService, ImageAttributes

# Test 1: Variant request detection
print("=" * 60)
print("TEST 1: Variant Request Detection")
print("=" * 60)

test_messages = [
    "show me this in blue",
    "do you have this with blue color",
    "any other color",
    "show me this kind of product if you have with blue color",
    "i want this shoe in red",
    "can i get this in black",
    "show me blue shoes",  # Not a variant request
    "what blue products do you have",  # Not a variant request
]

for msg in test_messages:
    is_variant = VisionService._is_variant_request(msg)
    result = "✓ VARIANT" if is_variant else "✗ NOT variant"
    print(f"{result}: {msg}")

# Test 2: Query building with image attributes
print("\n" + "=" * 60)
print("TEST 2: Query Building (Image + User Message)")
print("=" * 60)

# Simulate red shoe from image
image_attrs = ImageAttributes(
    product_type="running shoe",
    category="footwear",
    subcategory="athletic sneakers",
    primary_color="deep red",
    secondary_colors=["white", "maroon", "blue"],
    pattern="variegated knit",
    material="fabric",
    style="sporty",
    occasion="sports",
    gender_target="unisex",
    brand_visible="NIKE",
    notable_features=["knit upper", "white swoosh", "flexible fit"],
    confidence=1.0,
    needs_clarification=False,
    clarification_question="",
    raw_description="Red Nike running shoe"
)

test_cases = [
    ("show me this in blue color", "Should merge: blue + running shoe"),
    ("do you have this with red", "Should merge: red + running shoe"),
    ("show me other colors", "Should merge: (no color) + running shoe"),
    ("show me this product", "Should merge: red + running shoe"),
    ("what are your shoes", "NOT variant - use as-is"),
]

for user_msg, expected in test_cases:
    primary_query, detailed_query = VisionService.build_combined_query(
        user_message=user_msg,
        image_attrs=image_attrs
    )
    print(f"\nMessage: {user_msg}")
    print(f"Expected: {expected}")
    print(f"Primary Query: {primary_query}")
    print(f"Detailed Query: {detailed_query}")

# Test 3: Color extraction
print("\n" + "=" * 60)
print("TEST 3: Color Extraction from Text")
print("=" * 60)

color_test_cases = [
    "show me this in blue",
    "do you have red ones",
    "i want black color",
    "any purple shoes",
]

for text in color_test_cases:
    color = VisionService._extract_color_from_text(text.lower())
    print(f"Text: {text}")
    print(f"Extracted Color: {color or 'None'}")

print("\n" + "=" * 60)
print("All tests completed!")
print("=" * 60)
