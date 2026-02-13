import asyncio
import httpx
import re
import json
import base64
import time
from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4
from sqlalchemy import select, desc, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.knowledge import Embedding, KnowledgeSourceType, CrawledPage
from app.models.chatbot import Chatbot, ChatbotStatus
from app.models.chat import ChatSession, ChatMessage, MessageRole
from app.services.embedding_service import get_single_embedding
from app.services.vision_service import VisionService, ImageAttributes
from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.chat import (
    ChatMessageResponse,
    ChatSource,
    ImageAnalysisResult,
    ProductInfo,
)
from app.services.cache_service import get_cached_response, cache_response

logger = get_logger(__name__)

# Confidence threshold for vision analysis (lowered for better coverage)
VISION_CONFIDENCE_THRESHOLD = 0.35

# Keywords that indicate product-related queries
PRODUCT_QUERY_KEYWORDS = [
    "show",
    "find",
    "search",
    "looking for",
    "want",
    "need",
    "buy",
    "purchase",
    "price",
    "cost",
    "how much",
    "available",
    "products",
    "product",
    "item",
    "items",
    "ring",
    "earring",
    "necklace",
    "bracelet",
    "pendant",
    "jewellery",
    "jewelry",
    "gold",
    "silver",
    "diamond",
    "moissanite",
    "rose gold",
    "platinum",
    "mens",
    "women",
    "men",
    "ladies",
    "unisex",
    "collection",
    "collections",
    "recommend",
    "suggest",
    "best",
    "popular",
    "trending",
    "new",
    "latest",
]


def is_product_query(message: str) -> bool:
    """Detect if the message is asking about products."""
    if not message:
        return False
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in PRODUCT_QUERY_KEYWORDS)


def extract_price_filter(message: str) -> Optional[Dict[str, float]]:
    """
    Extract price constraints from user message.
    Returns dict with 'max_price' and/or 'min_price' if found.
    """
    if not message:
        return None

    message_lower = message.lower()
    filters = {}

    # Pattern: "under X", "below X", "less than X", "within X", "budget of X", "upto X", "up to X"
    under_patterns = [
        r"under\s*(?:rs\.?|₹|inr)?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)",
        r"below\s*(?:rs\.?|₹|inr)?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)",
        r"less\s+than\s*(?:rs\.?|₹|inr)?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)",
        r"within\s*(?:rs\.?|₹|inr)?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)",
        r"budget\s+(?:of\s+)?(?:rs\.?|₹|inr)?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)",
        r"upto\s*(?:rs\.?|₹|inr)?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)",
        r"up\s+to\s*(?:rs\.?|₹|inr)?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)",
        r"(?:rs\.?|₹|inr)\s*(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:or\s+)?(?:less|below|under)",
        r"max(?:imum)?\s*(?:price)?\s*(?:rs\.?|₹|inr)?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)",
    ]

    # Pattern: "above X", "over X", "more than X", "starting from X"
    above_patterns = [
        r"above\s*(?:rs\.?|₹|inr)?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)",
        r"over\s*(?:rs\.?|₹|inr)?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)",
        r"more\s+than\s*(?:rs\.?|₹|inr)?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)",
        r"starting\s+(?:from\s+)?(?:rs\.?|₹|inr)?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)",
        r"min(?:imum)?\s*(?:price)?\s*(?:rs\.?|₹|inr)?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)",
    ]

    # Pattern: "between X and Y" or "X to Y"
    range_patterns = [
        r"between\s*(?:rs\.?|₹|inr)?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:and|to|-)\s*(?:rs\.?|₹|inr)?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)",
        r"(?:rs\.?|₹|inr)?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:to|-)\s*(?:rs\.?|₹|inr)?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)",
    ]

    # Check range patterns first
    for pattern in range_patterns:
        match = re.search(pattern, message_lower, re.IGNORECASE)
        if match:
            try:
                min_val = float(match.group(1).replace(",", ""))
                max_val = float(match.group(2).replace(",", ""))
                filters["min_price"] = min(min_val, max_val)
                filters["max_price"] = max(min_val, max_val)
                logger.info(f"Extracted price range: {filters}")
                return filters
            except ValueError:
                pass

    # Check max price patterns
    for pattern in under_patterns:
        match = re.search(pattern, message_lower, re.IGNORECASE)
        if match:
            try:
                filters["max_price"] = float(match.group(1).replace(",", ""))
                logger.info(f"Extracted max price: {filters['max_price']}")
                break
            except ValueError:
                pass

    # Check min price patterns
    for pattern in above_patterns:
        match = re.search(pattern, message_lower, re.IGNORECASE)
        if match:
            try:
                filters["min_price"] = float(match.group(1).replace(",", ""))
                logger.info(f"Extracted min price: {filters['min_price']}")
                break
            except ValueError:
                pass

    return filters if filters else None


# Common color names for filtering
COLOR_KEYWORDS = [
    "red",
    "blue",
    "green",
    "yellow",
    "orange",
    "purple",
    "pink",
    "black",
    "white",
    "grey",
    "gray",
    "brown",
    "beige",
    "cream",
    "navy",
    "maroon",
    "teal",
    "cyan",
    "magenta",
    "gold",
    "silver",
    "bronze",
    "olive",
    "coral",
    "salmon",
    "turquoise",
    "indigo",
    "violet",
    "lavender",
    "peach",
    "mint",
    "burgundy",
    "charcoal",
    "ivory",
    "khaki",
    "tan",
    "rust",
    "mustard",
    "wine",
    "plum",
    "forest",
    "multicolor",
    "multi-color",
    "colourful",
    "colorful",
    "printed",
    "striped",
    "checkered",
    "checked",
    "plain",
    "solid",
]


def detect_product_gender(
    product_name: str, url: str, description: str = ""
) -> Optional[str]:
    """
    Generic algorithm to detect the target gender/demographic of a product.

    Uses a scoring-based approach instead of hardcoded keyword lists.
    Analyzes: product name, URL path, and description.

    Returns: 'men', 'women', 'boys', 'girls', 'kids', 'unisex', or None (neutral)
    """
    # Combine text sources with different weights
    name_lower = product_name.lower() if product_name else ""
    url_lower = url.lower() if url else ""
    desc_lower = description.lower() if description else ""

    # Initialize scores for each demographic
    scores = {
        "men": 0,
        "women": 0,
        "boys": 0,
        "girls": 0,
        "kids": 0,
    }

    # === LAYER 1: URL CATEGORY PATH (Strong signal) ===
    # Extract category from URL path patterns like /men-90/, /women/, /category/men/, etc.
    url_category_patterns = {
        "men": [
            r"/men[-_/]",
            r"/mens[-_/]",
            r"/male[-_/]",
            r"/gents[-_/]",
            r"category[-/]men",
            r"/him[-_/]",
        ],
        "women": [
            r"/women[-_/]",
            r"/womens[-_/]",
            r"/female[-_/]",
            r"/ladies[-_/]",
            r"category[-/]women",
            r"/her[-_/]",
        ],
        "boys": [r"/boys[-_/]", r"/boy[-_/]"],
        "girls": [r"/girls[-_/]", r"/girl[-_/]"],
        "kids": [
            r"/kids[-_/]",
            r"/children[-_/]",
            r"/child[-_/]",
            r"/junior[-_/]",
            r"/baby[-_/]",
            r"/infant[-_/]",
        ],
    }

    for demographic, patterns in url_category_patterns.items():
        for pattern in patterns:
            if re.search(pattern, url_lower):
                scores[demographic] += 30  # Strong signal from URL category
                break

    # === LAYER 2: PRODUCT NAME GENDER INDICATORS (Strongest signal) ===
    # Direct gender mentions in product name
    name_patterns = {
        "men": [
            r"\bmen'?s?\b",
            r"\bmale\b",
            r"\bgent'?s?\b",
            r"\bgentlemen\b",
            r"\bfor men\b",
            r"\bfor him\b",
            r"\bmasculine\b",
        ],
        "women": [
            r"\bwomen'?s?\b",
            r"\bfemale\b",
            r"\bladies?\b",
            r"\bfor women\b",
            r"\bfor her\b",
            r"\bfeminine\b",
        ],
        "boys": [r"\bboys?'?\b", r"\bfor boys?\b"],
        "girls": [r"\bgirls?'?\b", r"\bfor girls?\b"],
        "kids": [
            r"\bkids?\b",
            r"\bchildren\b",
            r"\bchild\b",
            r"\bjunior\b",
            r"\bbaby\b",
            r"\binfant\b",
            r"\btoddler\b",
        ],
    }

    for demographic, patterns in name_patterns.items():
        for pattern in patterns:
            if re.search(pattern, name_lower):
                scores[demographic] += 50  # Very strong signal from product name
                break

    # === LAYER 3: PRODUCT TYPE INDICATORS (Medium signal) ===
    # These product types are gender-specific by nature
    # Use patterns, not just keywords, for flexibility

    # Women-specific product types (clothing, accessories)
    women_product_patterns = [
        r"\b(saree|sari)s?\b",  # Indian traditional
        r"\b(lehenga|ghagra)s?\b",  # Indian traditional
        r"\b(salwar|churidar|palazzo)s?\b",  # Bottom wear
        r"\b(kurti|kurta)s?\b(?!.*\bmen)",  # Kurti (unless "men" mentioned)
        r"\b(anarkali|sharara)s?\b",  # Indian traditional
        r"\b(dupatta|chunni)s?\b",  # Accessories
        r"\b(blouse)s?\b",  # Blouse
        r"\b(bra|lingerie|panties?)\b",  # Innerwear
        r"\b(mangalsutra|sindoor)\b",  # Jewelry
        r"\b(gown|frock)s?\b",  # Dresses
        r"\b(skirt|midi|maxi)s?\b",  # Bottom wear
        r"\b(bangles?|anklet)s?\b",  # Jewelry
        r"\bmaternity\b",  # Maternity
        r"\b(lipstick|mascara|foundation|eyeshadow)\b",  # Makeup
    ]

    # Men-specific product types
    men_product_patterns = [
        r"\b(sherwani|dhoti|lungi)s?\b",  # Indian traditional
        r"\b(waistcoat|vest)s?\b",  # Formal wear
        r"\b(cufflinks?|tie\s*clip)\b",  # Accessories
        r"\b(necktie|bow\s*tie)s?\b",  # Accessories
        r"\b(blazer|suit)\b(?!.*\bwomen)",  # Formal (unless women mentioned)
        r"\b(boxers?|briefs?)\b",  # Innerwear
        r"\bmundu\b",  # Indian traditional
    ]

    for pattern in women_product_patterns:
        if re.search(pattern, name_lower):
            scores["women"] += 40
            break  # Only count once

    for pattern in men_product_patterns:
        if re.search(pattern, name_lower):
            scores["men"] += 40
            break  # Only count once

    # === LAYER 4: DESCRIPTION ANALYSIS (Weak signal) ===
    if desc_lower:
        desc_patterns = {
            "men": [r"\bmen\b", r"\bmale\b", r"\bgents\b"],
            "women": [r"\bwomen\b", r"\bfemale\b", r"\bladies\b"],
            "boys": [r"\bboys\b"],
            "girls": [r"\bgirls\b"],
            "kids": [r"\bkids\b", r"\bchildren\b"],
        }

        for demographic, patterns in desc_patterns.items():
            for pattern in patterns:
                if re.search(pattern, desc_lower):
                    scores[demographic] += 10  # Weak signal from description
                    break

    # === DETERMINE RESULT ===
    # Find the highest scoring demographic
    max_score = max(scores.values())

    if max_score < 20:
        # No strong signals - treat as neutral/unisex
        return None

    # Get all demographics with the max score
    top_demographics = [d for d, s in scores.items() if s == max_score]

    if len(top_demographics) == 1:
        return top_demographics[0]

    # If tie between men and women, check for unisex signals
    if "men" in top_demographics and "women" in top_demographics:
        return "unisex"

    # If tie between boys/girls, return 'kids'
    if "boys" in top_demographics and "girls" in top_demographics:
        return "kids"

    # Kids category includes boys/girls
    if "kids" in top_demographics:
        return "kids"

    # Default to the first one (arbitrary but consistent)
    return top_demographics[0]


def extract_attribute_filters(message: str) -> Optional[Dict[str, Any]]:
    """
    Extract product attribute filters from user message.
    Returns dict with filters like 'colors', 'styles', 'gender', etc.
    """
    if not message:
        return None

    message_lower = message.lower()
    filters = {}

    # Extract colors
    found_colors = []
    for color in COLOR_KEYWORDS:
        # Use word boundary to avoid partial matches
        if re.search(rf"\b{color}\b", message_lower):
            found_colors.append(color)

    if found_colors:
        filters["colors"] = found_colors
        logger.info(f"Extracted color filters: {found_colors}")

    # Extract gender filter
    # Men's patterns
    men_patterns = [
        r"\bmen'?s?\b",  # men, mens, men's
        r"\bmale\b",  # male
        r"\bboy'?s?\b",  # boy, boys, boy's
        r"\bgent'?s?\b",  # gent, gents, gent's
        r"\bgentlemen\b",  # gentlemen
        r"\bfor men\b",  # for men
        r"\bfor him\b",  # for him
    ]

    # Women's patterns
    women_patterns = [
        r"\bwomen'?s?\b",  # women, womens, women's
        r"\bfemale\b",  # female
        r"\bwomen\b",  # women
        r"\bladies?\b",  # lady, ladies
        r"\bgirl'?s?\b",  # girl, girls, girl's
        r"\bfor women\b",  # for women
        r"\bfor her\b",  # for her
    ]

    # Check for gender
    is_men = any(re.search(pattern, message_lower) for pattern in men_patterns)
    is_women = any(re.search(pattern, message_lower) for pattern in women_patterns)

    if is_men and not is_women:
        filters["gender"] = "men"
        logger.info("Extracted gender filter: men")
    elif is_women and not is_men:
        filters["gender"] = "women"
        logger.info("Extracted gender filter: women")
    elif is_men and is_women:
        # Both mentioned - likely unisex or comparing, don't filter
        filters["gender"] = "unisex"
        logger.info("Extracted gender filter: unisex (both mentioned)")

    return filters if filters else None


def is_collection_url(url: str) -> bool:
    """Check if URL is a collection/listing page rather than a product page"""
    if not url:
        return True

    url_lower = url.lower()

    # IMPORTANT: If URL contains /products/ or /product/, it's a product page, NOT a collection
    # This handles Shopify URLs like /collections/shirts/products/blue-shirt
    if "/products/" in url_lower or "/product/" in url_lower:
        return False

    # Patterns that indicate collection/listing pages (only if no /products/ in URL)
    collection_patterns = [
        r"/collections?/[^/]+/?$",  # Collection without product (e.g., /collections/shirts)
        r"/collections?/[^/]+\?",  # Collection with query params
        r"/collections?$",  # Just /collection or /collections
        r"/category/",  # Category pages
        r"/categories/",
        r"[?&]page=\d+",  # Pagination
        r"[?&]sort=",  # Sort parameter
        r"[?&]filter",  # Filter parameter
        r"/search",  # Search results
        r"/all-products",
        r"/shop/?$",  # Shop landing
        r"/store/?$",
    ]

    for pattern in collection_patterns:
        if re.search(pattern, url_lower):
            return True

    return False


def is_non_product_url(url: str) -> bool:
    """Check if URL is a non-product page (policy, contact, about, etc.)"""
    if not url:
        return True

    # Patterns that indicate informational/non-product pages
    non_product_patterns = [
        r"/returns?[-_]?policy",  # Returns policy
        r"/refund[-_]?policy",  # Refund policy
        r"/privacy[-_]?policy",  # Privacy policy
        r"/terms[-_]?(and[-_])?conditions?",  # Terms and conditions
        r"/terms[-_]?of[-_]?(service|use)",  # Terms of service/use
        r"/shipping[-_]?(policy|info)",  # Shipping info
        r"/contact[-_]?us",  # Contact us
        r"/contact$",  # Contact page
        r"/about[-_]?us",  # About us
        r"/about$",  # About page
        r"/faq",  # FAQ
        r"/help",  # Help page
        r"/support",  # Support page
        r"/blog/",  # Blog posts
        r"/news/",  # News
        r"/careers?",  # Careers page
        r"/jobs?",  # Jobs page
        r"/login",  # Login page
        r"/register",  # Register page
        r"/signup",  # Signup page
        r"/account",  # Account page
        r"/cart",  # Cart page
        r"/checkout",  # Checkout page
        r"/wishlist",  # Wishlist page
        r"/track[-_]?order",  # Order tracking
        r"/order[-_]?status",  # Order status
        r"/my[-_]?orders?",  # My orders
        r"/sitemap",  # Sitemap
        r"/404",  # Error page
        r"/error",  # Error page
        r"/not[-_]?found",  # Not found page
    ]

    for pattern in non_product_patterns:
        if re.search(pattern, url, re.IGNORECASE):
            return True

    return False


def extract_products_from_chunks(
    chunks: List[Dict[str, Any]],
    limit: int = 10,
    price_filter: Optional[Dict[str, float]] = None,
    attribute_filter: Optional[Dict[str, Any]] = None,
) -> List[ProductInfo]:
    """
    Extract product information from embedding chunks.

    Args:
        chunks: List of embedding chunks with product data
        limit: Maximum number of products to return
        price_filter: Optional dict with 'min_price' and/or 'max_price' constraints
        attribute_filter: Optional dict with 'colors', 'styles' etc. for filtering
    """
    products = []
    seen_urls = set()
    seen_images = set()  # Track unique images to avoid duplicates
    seen_names = set()  # Track unique product names

    for chunk in chunks:
        emb = chunk.get("embedding")
        if not emb:
            continue

        meta = emb.metadata_json or {}

        # Check if this chunk contains product data
        is_product = meta.get("is_product", False)
        product_data = meta.get("product") or {}
        url = meta.get("url", "")

        # Skip if already seen this URL or not a product
        if url in seen_urls or not is_product:
            continue

        # Skip if no product data
        if not product_data:
            continue

        # CRITICAL: Skip non-product pages (policy, contact, about, etc.)
        if is_non_product_url(url):
            logger.debug(f"Skipping non-product URL (policy/contact/etc): {url}")
            continue

        # NOTE: Collection/listing URLs are now allowed if they have valid product data
        # The crawler marks pages as is_product=True when they contain products,
        # so we trust that flag over URL pattern. Category pages often have product listings
        # and can provide valuable product information.

        # QUALITY CHECK: Ensure product has meaningful data (name OR price)
        # This prevents generic listing pages without actual product details
        # Note: .get("key", "") can return None if key exists with None value, so use `or ""`
        product_name_check = (product_data.get("name") or "").strip()
        product_price_check = product_data.get("price")
        product_images_check = product_data.get("images")

        # Skip if no name AND no price (likely a pure navigation/listing page)
        if not product_name_check and not product_price_check:
            logger.debug(f"Skipping product without name or price: {url}")
            continue

        # Validate URL - ensure it's not just a home page
        if url:
            from urllib.parse import urlparse

            parsed_url = urlparse(url)
            path = parsed_url.path.strip("/")

            # Skip if URL is just the home page or has no path
            if not path or path in ["", "index.html", "home", "index.php"]:
                logger.debug(f"Skipping product with home page URL: {url}")
                continue

        # Note: We trust is_product flag from crawler - if it detected product data,
        # the URL check above is sufficient. No need for strict URL pattern matching.

        # Get product name - use product data name, fall back to page title
        product_name = (product_data.get("name") or "").strip()
        page_title = (meta.get("title") or "").strip()

        # If product name is too short or generic, use page title instead
        generic_brand_names = ["rozzby", "store", "shop", "products", "home"]
        if (
            len(product_name) < 5
            or product_name.lower().strip() in generic_brand_names
            or product_name.lower()
            == page_title.lower().split(" - ")[0].lower().strip()
        ):
            # Page title often has format "Product Name - Brand/Site Name"
            if " - " in page_title:
                product_name = page_title.split(" - ")[0].strip()
            elif " | " in page_title:
                product_name = page_title.split(" | ")[0].strip()
            else:
                product_name = page_title.strip() if page_title else product_name

        # If still no good name, use the page title as-is
        if not product_name or len(product_name) < 3:
            product_name = page_title or "Product"

        # Skip generic/collection names
        generic_names = [
            "colour shirts",
            "color shirts",
            "shirts",
            "products",
            "collection",
            "all products",
            "home",
            "rozzby",
        ]
        if product_name.lower().strip() in generic_names:
            logger.debug(f"Skipping generic product name: {product_name}")
            continue

        # Skip if we've already seen this exact name (indicates duplicate)
        name_key = product_name.lower().strip()
        if name_key in seen_names:
            logger.debug(f"Skipping duplicate product name: {product_name}")
            continue

        # Get price for filtering
        price = product_data.get("price")
        price_value = None
        if price is not None:
            try:
                price_value = float(str(price).replace(",", ""))
            except (ValueError, TypeError):
                pass

        # Apply price filter if specified
        if price_filter and price_value is not None:
            max_price = price_filter.get("max_price")
            min_price = price_filter.get("min_price")

            if max_price is not None and price_value > max_price:
                logger.debug(
                    f"Skipping product {product_name} - price {price_value} > max {max_price}"
                )
                continue
            if min_price is not None and price_value < min_price:
                logger.debug(
                    f"Skipping product {product_name} - price {price_value} < min {min_price}"
                )
                continue

        # Apply color/attribute filter if specified
        if attribute_filter and attribute_filter.get("colors"):
            # Check if product name, description or content contains the color
            product_text = f"{product_name} {product_data.get('description') or ''} {emb.content}".lower()
            color_match = False
            for color in attribute_filter["colors"]:
                if color in product_text:
                    color_match = True
                    break
            if not color_match:
                logger.debug(f"Skipping product {product_name} - no color match")
                continue

        # Apply gender filter if specified
        if attribute_filter and attribute_filter.get("gender"):
            gender = attribute_filter["gender"]
            if gender != "unisex":  # Only filter if specific gender requested
                # Use generic gender detection algorithm
                product_gender = detect_product_gender(
                    product_name, url, product_data.get("description") or ""
                )

                if gender == "men":
                    # Skip products detected as women's/girls' only
                    if product_gender in ["women", "girls"]:
                        logger.debug(
                            f"Skipping product {product_name} - detected as {product_gender}"
                        )
                        continue

                elif gender == "women":
                    # Skip products detected as men's/boys' only
                    if product_gender in ["men", "boys"]:
                        logger.debug(
                            f"Skipping product {product_name} - detected as {product_gender}"
                        )
                        continue

        # Get images from product data - filter duplicates and generic images
        images = product_data.get("images", [])
        # Ensure images is a list
        if isinstance(images, str):
            # Try to parse JSON string
            try:
                import json

                images = json.loads(images)
            except:
                images = [images]
        if not isinstance(images, list):
            images = []

        # Log what we found
        logger.debug(
            f"Product {product_name} - images type: {type(images).__name__}, count: {len(images) if images else 0}"
        )
        if images:
            logger.debug(
                f"Product {product_name} - first image: {images[0][:80] if images[0] else 'empty'}..."
            )

        primary_image = None

        for img in images:
            if not img:
                logger.debug(f"Skipping empty image")
                continue
            # Clean the image URL - strip whitespace and newlines
            img = str(img).strip()
            logger.debug(f"Checking image: {img[:80]}...")
            # Skip base64 data URLs - they're usually placeholders
            if img.startswith("data:"):
                logger.debug(f"  -> Skipping base64 image")
                continue
            # Skip generic/placeholder images - be specific to avoid false positives
            # Check both full path and filename for problematic patterns
            img_lower = img.lower()
            img_filename = img.split("/")[-1].lower() if "/" in img else img_lower

            # Patterns to skip in the full URL path
            skip_in_path = [
                "/logo",
                "/icon",
                "/favicon",
                "/site-logo",
                "/brand-logo",
                "/website-logo",
                "website/1/logo",
            ]
            # Patterns to skip in the filename specifically
            skip_in_filename = [
                "placeholder",
                "no-image",
                "noimage",
                "logo.",
                "default.",
                "blank.",
                "logo?",
            ]

            if any(skip in img_lower for skip in skip_in_path):
                logger.debug(f"  -> Skipping logo/icon image in path: {img[:80]}")
                continue
            if any(skip in img_filename for skip in skip_in_filename):
                logger.debug(f"  -> Skipping placeholder image: {img_filename}")
                continue
            # Skip if we've already seen this exact image
            if img in seen_images:
                logger.debug(f"  -> Skipping duplicate image")
                continue
            # Valid image found!
            logger.debug(f"  -> VALID image selected!")
            primary_image = img
            seen_images.add(img)
            break

        if not primary_image:
            logger.debug(f"Product {product_name} - No valid image found in loop")

        # Fallback: Check if there's a single 'image' field at top level
        if not primary_image:
            single_image = product_data.get("image")
            if (
                single_image
                and isinstance(single_image, str)
                and not single_image.startswith("data:")
            ):
                if single_image not in seen_images:
                    primary_image = single_image
                    seen_images.add(single_image)

        # Convert price to string if it exists
        price_str = str(price) if price is not None else None

        # Build product info
        product = ProductInfo(
            name=product_name or "Product",
            url=url,
            price=price_str,
            currency=product_data.get("currency"),
            image=primary_image,
            brand=product_data.get("brand"),
            rating=product_data.get("rating"),
            review_count=product_data.get("review_count"),
        )

        logger.debug(
            f"Extracted product: {product_name}, image: {primary_image}, url: {url}"
        )

        products.append(product)
        seen_urls.add(url)
        seen_names.add(name_key)

        if len(products) >= limit:
            break

    # ── Fallback: if no structured products found, try extracting from chunk content ──
    # This handles sites where the crawler couldn't extract JSON-LD/structured product data,
    # but the page content still has product-like information (prices, names, URLs).
    if not products:
        logger.info(
            "No structured products found, attempting content-based fallback extraction"
        )
        from urllib.parse import urlparse

        seen_fallback_urls = set()
        for chunk in chunks:
            emb = chunk.get("embedding")
            if not emb:
                continue

            meta = emb.metadata_json or {}
            url = meta.get("url", "")
            page_title = (meta.get("title") or "").strip()

            if not url or url in seen_fallback_urls:
                continue

            # Skip non-product URLs
            if is_non_product_url(url):
                continue

            # Skip home pages
            parsed_url = urlparse(url)
            path = parsed_url.path.strip("/")
            if not path or path in ["", "index.html", "home", "index.php"]:
                continue

            # Check if chunk content has price indicators
            content = (emb.content or "").lower()
            has_price = bool(
                re.search(
                    r"(?:₹|rs\.?|inr|\$|€|£)\s*[\d,]+(?:\.\d{2})?",
                    content,
                    re.IGNORECASE,
                )
            )
            has_product_keywords = any(
                kw in content
                for kw in [
                    "add to cart",
                    "buy now",
                    "add to bag",
                    "in stock",
                    "out of stock",
                ]
            )

            if not has_price and not has_product_keywords:
                continue

            # Extract price from content
            price_match = re.search(
                r"(?:₹|rs\.?|inr)\s*([\d,]+(?:\.\d{2})?)", content, re.IGNORECASE
            )
            if not price_match:
                price_match = re.search(
                    r"(?:\$|€|£)\s*([\d,]+(?:\.\d{2})?)", content, re.IGNORECASE
                )
            price_str = price_match.group(0).strip() if price_match else None

            # Use page title as product name
            product_name = page_title
            if " - " in product_name:
                product_name = product_name.split(" - ")[0].strip()
            elif " | " in product_name:
                product_name = product_name.split(" | ")[0].strip()

            if not product_name or len(product_name) < 3:
                continue

            # Skip duplicates
            name_key = product_name.lower().strip()
            if name_key in seen_names:
                continue

            product = ProductInfo(
                name=product_name,
                url=url,
                price=price_str,
                currency=None,
                image=None,
                brand=None,
                rating=None,
                review_count=None,
            )
            products.append(product)
            seen_fallback_urls.add(url)
            seen_names.add(name_key)

            if len(products) >= limit:
                break

        if products:
            logger.info(
                f"Fallback extraction found {len(products)} products from chunk content"
            )

    return products


def _sanitize_display_name(raw_name: str) -> str:
    """
    Sanitize chatbot display name for use in LLM prompts and responses.

    Handles generalized cases:
    - Literal 'undefined', 'null', 'none', empty → fallback to 'our services'
    - URLs → extract clean brand/domain name (e.g., 'https://ramrajcotton.in/' → 'Ramrajcotton')
    - Normal names → returned as-is
    """
    if not raw_name:
        return "our services"

    name = raw_name.strip()

    # Reject common invalid literal values (case-insensitive)
    if name.lower() in ("undefined", "null", "none", "n/a", "nan", ""):
        return "our services"

    # Detect if name is a URL
    if re.match(r"^https?://", name, re.IGNORECASE):
        try:
            from urllib.parse import urlparse

            parsed = urlparse(name)
            domain = parsed.hostname or ""
            # Remove 'www.' prefix
            domain = re.sub(r"^www\.", "", domain)
            if not domain:
                return "our services"

            # Split domain into parts
            parts = domain.split(".")
            # Known TLDs to strip from the end
            tlds = {
                "com",
                "org",
                "net",
                "io",
                "dev",
                "co",
                "in",
                "uk",
                "us",
                "ca",
                "au",
                "de",
                "fr",
                "jp",
                "store",
                "shop",
                "app",
                "ai",
                "info",
                "biz",
                "me",
                "xyz",
                "tech",
                "online",
                "site",
                "website",
                "page",
            }
            while len(parts) > 1 and parts[-1].lower() in tlds:
                parts.pop()

            # Join remaining parts and split by common word-separators
            base = "-".join(parts)
            words = re.split(r"[-_.]", base)
            # Title case each word
            brand_name = " ".join(w.capitalize() for w in words if w)
            return brand_name if brand_name else "our services"
        except Exception:
            return "our services"

    return name


def _url_to_domain(url: str) -> str:
    """Extract clean domain from a URL for display. Returns '' if not a URL."""
    match = re.match(r"^https?://(?:www\.)?([^/]+)", url, re.IGNORECASE)
    return match.group(1) if match else ""


def _extract_content_words(text: str) -> set:
    """
    Extract meaningful content words from text, stripping stop words.
    Generalized approach — works for any domain.
    """
    stop_words = {
        "the",
        "a",
        "an",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "what",
        "do",
        "does",
        "did",
        "you",
        "have",
        "has",
        "had",
        "tell",
        "me",
        "show",
        "want",
        "need",
        "about",
        "any",
        "can",
        "could",
        "i",
        "my",
        "your",
        "we",
        "our",
        "they",
        "their",
        "he",
        "she",
        "in",
        "on",
        "for",
        "with",
        "to",
        "of",
        "at",
        "by",
        "from",
        "up",
        "and",
        "or",
        "but",
        "not",
        "no",
        "so",
        "if",
        "just",
        "also",
        "it",
        "this",
        "that",
        "these",
        "those",
        "them",
        "there",
        "would",
        "should",
        "will",
        "shall",
        "may",
        "might",
        "some",
        "all",
        "each",
        "every",
        "much",
        "many",
        "very",
        "too",
        "get",
        "got",
        "go",
        "going",
        "come",
        "take",
        "make",
        "know",
        "please",
        "thanks",
        "thank",
        "yes",
        "no",
        "ok",
        "okay",
        "hi",
        "hello",
        "hey",
        "how",
        "well",
        "like",
        "look",
        "looking",
    }
    words = set(re.findall(r"\b[a-z]+\b", text.lower()))
    return words - stop_words


def _has_referential_language(message: str) -> bool:
    """
    Generalized detection of referential/anaphoric language that needs prior context.
    Uses regex patterns to catch pronouns, demonstratives, and relative references.
    """
    message_lower = message.lower().strip()

    # Referential pronouns and demonstratives (object/subject references)
    referential_patterns = [
        r"\bit\b",
        r"\bthat\b",
        r"\bthis\b",
        r"\bthese\b",
        r"\bthose\b",
        r"\bthem\b",
        r"\bthey\b",
        r"\bhis\b",
        r"\bher\b",
        r"\bits\b",
        r"\bthe one\b",
        r"\bthe ones\b",
        r"\bthe same\b",
    ]

    # Comparative / continuation references
    continuation_patterns = [
        r"\bmore\b",
        r"\bless\b",
        r"\balso\b",
        r"\btoo\b",
        r"\beither\b",
        r"\bother\b",
        r"\banother\b",
        r"\bsame\b",
        r"\bsimilar\b",
        r"\bcompare\b",
        r"\bdifference\b",
        r"\bversus\b",
        r"\bvs\b",
        r"\bcheaper\b",
        r"\bexpensive\b",
        r"\bbetter\b",
        r"\bworse\b",
        r"\bbigger\b",
        r"\bsmaller\b",
        r"\blarger\b",
    ]

    for pattern in referential_patterns + continuation_patterns:
        if re.search(pattern, message_lower):
            return True

    return False


def _is_greeting(message: str) -> bool:
    """Check if the message is a greeting. Generalized."""
    return bool(
        re.match(
            r"^\s*(hi+|hello+|hey+|heya*|good\s+(morning|afternoon|evening|night)|"
            r"howdy|what\'?s\s+up|sup|yo+|greetings?)\s*[!.?,]*\s*$",
            message.lower().strip(),
        )
    )


def _is_short_ambiguous(message: str) -> bool:
    """
    Detect short ambiguous messages that are likely follow-ups.
    E.g. "size 8?", "in blue", "for men", "under $50"
    """
    words = message.strip().split()
    return len(words) <= 4


def _compute_topic_overlap(msg_a: str, msg_b: str) -> float:
    """
    Compute semantic word overlap ratio between two messages.
    Returns 0.0 (no overlap) to 1.0 (full overlap).
    """
    words_a = _extract_content_words(msg_a)
    words_b = _extract_content_words(msg_b)

    if not words_a or not words_b:
        return 0.0

    overlap = len(words_a & words_b)
    return overlap / max(len(words_a), 1)


def enrich_query_with_context(
    current_message: str,
    history: List[ChatMessage],
    summary: str,
    max_context_length: int = 300,
) -> str:
    """
    Generalized query enrichment for RAG retrieval.

    Decision tree (priority order):
    1. Greetings -> as-is (no retrieval context needed)
    2. No history -> as-is (nothing to enrich with)
    3. Has referential language (pronouns, comparatives) -> ALWAYS enrich with context
    4. Short ambiguous (<=4 words, no clear subject) -> enrich with context
    5. Complete new topic (low word overlap with recent history) -> as-is
    6. Everything else with history -> light context from summary

    KEY PRINCIPLE: Check for references FIRST, before checking if it
    "looks standalone". "I want to buy it for my brother" has "it" -> needs context,
    regardless of length or structure.
    """
    current_lower = current_message.lower().strip()

    # --- CASE 1: Greetings -> always as-is ---
    if _is_greeting(current_message):
        logger.debug("🎯 Query Enrichment: GREETING -> as-is")
        return current_message

    # --- CASE 2: No history -> as-is (first message) ---
    if not history or len(history) == 0:
        logger.debug("🎯 Query Enrichment: NO HISTORY -> as-is")
        return current_message

    # Gather recent messages for context
    last_user_msg = None
    last_bot_msg = None
    for h in reversed(history):
        if h.role == MessageRole.USER and last_user_msg is None:
            last_user_msg = h.content
        elif h.role == MessageRole.ASSISTANT and last_bot_msg is None:
            last_bot_msg = h.content
        if last_user_msg and last_bot_msg:
            break

    # --- CASE 3: Referential language detected -> MUST enrich ---
    # This catches: "buy it", "tell me more about that", "cheaper ones",
    # "for my brother" (when there's prior context about products), etc.
    if _has_referential_language(current_message):
        context = _build_context_string(last_user_msg, last_bot_msg, max_context_length)
        if context:
            enriched = f"{context}. {current_message}"
            logger.debug(
                f"🎯 Query Enrichment: REFERENTIAL -> enriched ({len(context)} chars)"
            )
            return enriched

    # --- CASE 4: Short ambiguous query -> likely follow-up ---
    if _is_short_ambiguous(current_message):
        # Only enrich if there's actual prior conversation context
        context = _build_context_string(last_user_msg, last_bot_msg, max_context_length)
        if context:
            enriched = f"{context}. {current_message}"
            logger.debug(
                f"🎯 Query Enrichment: SHORT AMBIGUOUS -> enriched ({len(context)} chars)"
            )
            return enriched

    # --- CASE 5: Check if it's a new topic (low overlap with recent history) ---
    if last_user_msg:
        overlap = _compute_topic_overlap(current_message, last_user_msg)
        if overlap < 0.15:
            # New topic — don't pollute with old context
            logger.debug(
                f"🎯 Query Enrichment: NEW TOPIC (overlap={overlap:.2f}) -> as-is"
            )
            return current_message

    # --- CASE 6: Moderate overlap — add light summary context ---
    if summary and len(summary.strip()) > 10:
        recent_summary = summary[-200:].strip()
        enriched = f"{recent_summary} {current_message}"
        logger.debug(
            f"🎯 Query Enrichment: CONTEXTUAL -> light summary ({len(recent_summary)} chars)"
        )
        return enriched

    # --- Default: as-is ---
    logger.debug("🎯 Query Enrichment: DEFAULT -> as-is")
    return current_message


def _build_context_string(
    last_user_msg: Optional[str], last_bot_msg: Optional[str], max_length: int = 300
) -> str:
    """
    Build a concise context string from recent conversation history.
    Prioritizes the user's last question, with a snippet of the bot's response.
    """
    parts = []

    if last_user_msg:
        # Truncate to keep embedding input manageable
        parts.append(last_user_msg[:200].strip())

    if last_bot_msg:
        # Take first meaningful portion of bot response (usually the key info)
        # Strip HTML tags for cleaner embedding input
        clean_bot = re.sub(r"<[^>]+>", " ", last_bot_msg)
        clean_bot = re.sub(r"\s+", " ", clean_bot).strip()
        parts.append(clean_bot[:150])

    context = " ".join(parts)
    if len(context) > max_length:
        context = context[:max_length]

    return context


class ChatService:
    @staticmethod
    async def get_or_create_session(
        db: AsyncSession,
        chatbot_id: UUID,
        session_id: Optional[str] = None,
        is_preview: bool = False,
    ) -> ChatSession:
        if session_id:
            try:
                session_uuid = UUID(session_id)
                stmt = select(ChatSession).where(
                    ChatSession.id == session_uuid, ChatSession.chatbot_id == chatbot_id
                )
                result = await db.execute(stmt)
                session = result.scalar_one_or_none()
                if session:
                    return session
            except (ValueError, AttributeError):
                pass

        # Create new session if not found or invalid
        session = ChatSession(chatbot_id=chatbot_id, is_preview=is_preview)
        db.add(session)
        await db.commit()
        await db.refresh(session)
        return session

    @staticmethod
    async def get_history(
        db: AsyncSession, session_id: UUID, limit: int = 6
    ) -> List[ChatMessage]:
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(desc(ChatMessage.created_at))
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(reversed(result.scalars().all()))

    @staticmethod
    async def summarize_conversation(
        session: ChatSession, last_messages: List[ChatMessage]
    ) -> str:
        if not last_messages:
            return session.conversation_summary or ""

        messages_str = "\n".join(
            [f"{m.role.value}: {m.content}" for m in last_messages]
        )

        async with httpx.AsyncClient() as client:
            prompt = (
                "Summarize this conversation in 1-2 sentences, focusing on what the user is looking for:\n"
                f"{messages_str}\n\n"
                f"Previous summary: {session.conversation_summary or 'None'}\n\n"
                "Updated summary:"
            )

            try:
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "llama-3.1-8b-instant",  # Use a smaller model for summarization
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a helpful assistant that summarizes conversations accurately and concisely.",
                            },
                            {"role": "user", "content": prompt},
                        ],
                        "temperature": 0.3,
                    },
                    timeout=10.0,
                )
                if response.status_code == 200:
                    res_data = response.json()
                    return res_data["choices"][0]["message"]["content"].strip()
            except Exception as e:
                logger.error(f"Error generating summary: {e}")

        return session.conversation_summary or ""

    @staticmethod
    async def get_response_stream(
        db: AsyncSession,
        chatbot_id: UUID,
        message: Optional[str] = None,
        session_id: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        is_preview: bool = False,
    ):
        """
        Stream chat response as Server-Sent Events.

        Yields chunks in the format:
        - {"type": "session", "session_id": "..."}
        - {"type": "content", "content": "text chunk"}
        - {"type": "done", "sources": [...], "suggestions": [...], "products": [...], "image_analysis": {...}}
        - {"type": "error", "error": "error message"}
        """
        start_time = time.time()

        try:
            # --- 1. Get chatbot and session (if provided) ---
            chatbot_stmt = select(Chatbot).where(Chatbot.id == chatbot_id)
            chatbot_res = await db.execute(chatbot_stmt)
            chatbot = chatbot_res.scalar_one()

            session = None
            if session_id:
                try:
                    session_uuid = UUID(session_id)
                    session_stmt = select(ChatSession).where(
                        ChatSession.id == session_uuid,
                        ChatSession.chatbot_id == chatbot_id,
                    )
                    session_res = await db.execute(session_stmt)
                    session = session_res.scalar_one_or_none()
                except (ValueError, AttributeError):
                    session = None

            # Check conversation limits only when starting a new session
            if session is None:
                if not is_preview:
                    from app.services.billing_service import BillingService

                    conv_limit = await BillingService.check_conversation_limit(
                        db, chatbot.tenant_id
                    )
                    if conv_limit["exceeded"]:
                        limit_message = (
                            "Conversation limit reached. "
                            f"You have used {conv_limit['current']} out of {conv_limit['limit']} conversations "
                            f"on your {conv_limit['plan']} plan. Please upgrade your plan to continue."
                        )
                        for char in limit_message:
                            yield {"type": "content", "content": char}
                            await asyncio.sleep(0.02)

                        yield {
                            "type": "done",
                            "sources": [],
                            "suggestions": [],
                            "products": [],
                            "image_analysis": None,
                            "error": "conversation_limit_exceeded",
                        }
                        return

                # Create a new session when under limit (or preview)
                session = ChatSession(chatbot_id=chatbot_id, is_preview=is_preview)
                db.add(session)
                await db.commit()
                await db.refresh(session)

            # Send session ID first
            yield {"type": "session", "session_id": str(session.id)}

            # --- 2. Get chatbot and history ---

            # Check message limits (only for non-preview chats)
            if not is_preview:
                from app.services.billing_service import BillingService

                limit_check = await BillingService.check_message_limit(
                    db, chatbot.tenant_id
                )
                if limit_check["exceeded"]:
                    limit_message = (
                        f"❌ Message limit reached. "
                        f"You have used {limit_check['current']} out of {limit_check['limit']} messages "
                        f"on your {limit_check['plan']} plan. Please upgrade your plan to continue."
                    )

                    # Stream limit reached message
                    for char in limit_message:
                        yield {"type": "content", "content": char}
                        await asyncio.sleep(0.02)

                    # Save user message but not assistant response
                    if message:
                        user_msg = ChatMessage(
                            session_id=session.id,
                            role=MessageRole.USER,
                            content=message,
                            metadata_json={"limit_exceeded": True},
                        )
                        db.add(user_msg)

                    await db.commit()

                    yield {
                        "type": "done",
                        "sources": [],
                        "suggestions": [],
                        "products": [],
                        "image_analysis": None,
                        "error": "message_limit_exceeded",
                    }
                    return

            # Check if chatbot is paused (and not in preview mode)
            if not is_preview and chatbot.status == ChatbotStatus.PAUSED:
                paused_display = _sanitize_display_name(chatbot.name)
                paused_message = (
                    f"🚧 {paused_display} is currently offline for maintenance. "
                    "Please check back later. We appreciate your patience!"
                )

                # Stream paused message
                for char in paused_message:
                    yield {"type": "content", "content": char}
                    await asyncio.sleep(0.02)

                # Save messages
                if message:
                    user_msg = ChatMessage(
                        session_id=session.id,
                        role=MessageRole.USER,
                        content=message,
                        metadata_json={"paused_chatbot": True},
                    )
                    db.add(user_msg)

                assistant_msg = ChatMessage(
                    session_id=session.id,
                    role=MessageRole.ASSISTANT,
                    content=paused_message,
                    metadata_json={
                        "is_paused_response": True,
                        "response_time_ms": int((time.time() - start_time) * 1000),
                    },
                )
                db.add(assistant_msg)
                await db.commit()

                yield {
                    "type": "done",
                    "sources": [],
                    "suggestions": [],
                    "products": [],
                    "image_analysis": None,
                }
                return

            # --- 3. Process image if provided (enhanced vision analysis) ---
            image_attrs = None
            image_analysis_result = None
            effective_message = message

            if image_bytes:
                try:
                    # Use enhanced vision service with user context
                    image_attrs = await VisionService.analyze_image(
                        image_bytes,
                        user_context=message or "",
                        quick_mode=False,  # Use full analysis for better results
                    )

                    # Build ImageAnalysisResult for response
                    image_analysis_result = ImageAnalysisResult(
                        product_type=image_attrs.product_type,
                        category=image_attrs.category,
                        color=image_attrs.primary_color,  # Use primary_color
                        style=image_attrs.style,
                        other_attributes=image_attrs.other_attributes
                        or ", ".join(image_attrs.notable_features[:3]),
                        confidence=image_attrs.confidence,
                        needs_clarification=image_attrs.needs_clarification,
                    )

                    # Use LLM-powered query building for intelligent intent understanding
                    if image_attrs.confidence >= VISION_CONFIDENCE_THRESHOLD:
                        # Try LLM-powered query building first (handles complex cases)
                        try:
                            primary_query, intent, detailed_info = (
                                await VisionService.build_query_with_llm(
                                    user_message=message or "", image_attrs=image_attrs
                                )
                            )
                            effective_message = primary_query
                            logger.info(
                                f"LLM Query: intent='{intent}', query='{primary_query}'"
                            )
                        except Exception as llm_err:
                            # Fallback to heuristic method
                            logger.warning(
                                f"LLM query building failed, using fallback: {llm_err}"
                            )
                            primary_query, detailed_query = (
                                VisionService.build_combined_query(
                                    user_message=message or "", image_attrs=image_attrs
                                )
                            )
                            effective_message = primary_query

                        # Log for debugging
                        logger.info(
                            f"Vision analysis: confidence={image_attrs.confidence:.2f}, "
                            f"product={image_attrs.product_type}, color={image_attrs.primary_color}, "
                            f"query='{effective_message}'"
                        )
                    elif image_attrs.needs_clarification:
                        # Image was unclear, keep original message
                        logger.info(
                            f"Vision analysis needs clarification: {image_attrs.clarification_question}"
                        )

                except Exception as e:
                    logger.error(f"Vision analysis failed: {e}", exc_info=True)

            text_content = effective_message or message or "What is this?"

            # --- 3.5. Check query cache (skip for image queries) ---
            cache_hit = None
            if not image_bytes and text_content:
                try:
                    cache_hit = await get_cached_response(str(chatbot_id), text_content)
                except Exception as e:
                    logger.debug(f"Cache lookup error (non-fatal): {e}")

            if cache_hit:
                # Stream cached response directly
                logger.info(
                    f"Cache HIT — returning cached response for: {text_content[:60]}"
                )
                yield {"type": "content", "content": cache_hit["content"]}

                # Save messages to DB (even cached responses should be tracked)
                from sqlalchemy import func

                user_msg = ChatMessage(
                    session_id=session.id,
                    role=MessageRole.USER,
                    content=text_content,
                    metadata_json={"cached": True},
                )
                assistant_msg = ChatMessage(
                    session_id=session.id,
                    role=MessageRole.ASSISTANT,
                    content=cache_hit["content"],
                    metadata_json={
                        "cached": True,
                        "suggestions": cache_hit.get("suggestions", []),
                    },
                )
                db.add(user_msg)
                db.add(assistant_msg)
                session.last_message_at = func.now()

                if not is_preview:
                    chatbot.message_count = (chatbot.message_count or 0) + 1

                await db.commit()

                yield {
                    "type": "done",
                    "sources": cache_hit.get("sources", []),
                    "suggestions": cache_hit.get("suggestions", [])[:2],
                    "products": cache_hit.get("products", []),
                    "image_analysis": None,
                }
                return

            # --- 4. Get chat history and summary ---
            history = await ChatService.get_history(db, session.id, limit=6)
            summary = session.conversation_summary or ""

            # --- 5. Smart Query Enrichment for Better Retrieval ---
            # Intelligently add context for follow-ups while keeping standalone queries clean
            enriched_query = enrich_query_with_context(
                current_message=text_content,
                history=history,
                summary=summary,
                max_context_length=250,
            )

            logger.debug(f"Original query: {text_content[:100]}")
            if enriched_query != text_content:
                logger.debug(f"Enriched query: {enriched_query[:150]}")

            # --- 6. Retrieve relevant context using RAG ---
            query_embedding = await get_single_embedding(enriched_query)

            # Text-based retrieval
            stmt = (
                select(
                    Embedding,
                    Embedding.embedding.cosine_distance(query_embedding).label("dist"),
                )
                .outerjoin(
                    CrawledPage,
                    and_(
                        Embedding.metadata_json["url"].astext == CrawledPage.url,
                        Embedding.knowledge_source_id
                        == CrawledPage.knowledge_source_id,
                    ),
                )
                .where(
                    and_(
                        Embedding.chatbot_id == chatbot_id,
                        or_(
                            Embedding.source_type == KnowledgeSourceType.QA_PAIR,
                            or_(
                                CrawledPage.is_removed == False,
                                CrawledPage.id.is_(None),
                            ),
                        ),
                    )
                )
                .order_by(Embedding.embedding.cosine_distance(query_embedding))
                .limit(20)
            )

            result = await db.execute(stmt)
            text_hits = result.all()

            text_results = []
            for emb, dist in text_hits:
                # Convert distance to similarity score (1 - distance)
                score = (1.0 - float(dist)) * getattr(emb, "priority_weight", 1.0)
                if emb.source_type == KnowledgeSourceType.QA_PAIR:
                    score += 0.15

                text_results.append(
                    {"embedding": emb, "score": score, "source": "text"}
                )

            # Vision-based retrieval if image provided
            vision_results = []
            if image_attrs and image_attrs.confidence >= VISION_CONFIDENCE_THRESHOLD:
                vision_embedding = await get_single_embedding(effective_message)
                vision_stmt = (
                    select(
                        Embedding,
                        Embedding.embedding.cosine_distance(vision_embedding).label(
                            "dist"
                        ),
                    )
                    .where(
                        and_(
                            Embedding.chatbot_id == chatbot_id,
                            or_(
                                Embedding.source_type == KnowledgeSourceType.QA_PAIR,
                                # For vision, we usually only care about products/images
                                True,
                            ),
                        )
                    )
                    .order_by(Embedding.embedding.cosine_distance(vision_embedding))
                    .limit(30)
                )

                vision_result = await db.execute(vision_stmt)
                vision_hits = vision_result.all()

                for emb, dist in vision_hits:
                    meta = emb.metadata_json or {}
                    if is_non_product_url(meta.get("url", "")):
                        continue

                    score = (1.0 - float(dist)) * getattr(emb, "priority_weight", 1.0)
                    vision_results.append(
                        {"embedding": emb, "score": score, "source": "vision"}
                    )

            # Combine results
            combined_results = text_results + vision_results
            combined_results.sort(key=lambda x: x["score"], reverse=True)

            # Deduplicate
            seen_chunks = set()
            top_chunks = []
            for r in combined_results:
                chunk_id = r["embedding"].id
                if chunk_id not in seen_chunks:
                    seen_chunks.add(chunk_id)
                    top_chunks.append(r)
                if len(top_chunks) >= 12:
                    break

            # Calculate retrieval confidence
            retrieval_confidence = (
                max([c["score"] for c in top_chunks]) if top_chunks else 0.0
            )
            sources_count = len(top_chunks)

            # --- Extract filters for product searching ---
            # We do this before product extraction to apply filters correctly
            price_filter = extract_price_filter(text_content)
            attribute_filter = extract_attribute_filters(text_content)

            # --- Extract products EARLY (before building system prompt) ---
            # This allows us to tell the LLM accurately if products exist
            products = []
            if (
                is_product_query(text_content)
                or is_product_query(enriched_query)
                or (image_attrs is not None)
            ):
                products = extract_products_from_chunks(
                    combined_results[:30],
                    limit=10,
                    price_filter=price_filter,
                    attribute_filter=attribute_filter,
                )
                logger.info(f"Found {len(products)} products for product query")

            # --- Early out-of-scope detection ---
            is_greeting = _is_greeting(text_content)

            # Interpret low retrieval confidence more intelligently:
            # - For product queries with products found → NOT out of scope (product pages retrieved successfully)
            # - For general queries with low confidence → likely out of scope
            is_product_request = is_product_query(text_content) or is_product_query(
                enriched_query
            )
            if is_product_request and len(products) > 0:
                # Product pages were found and extracted → DON'T consider out of scope
                is_likely_out_of_scope = False
                logger.debug(
                    f"Product query with {len(products)} products → treating as IN SCOPE"
                )
            else:
                # Non-product query or no products found → apply confidence threshold
                is_likely_out_of_scope = (
                    retrieval_confidence < 0.35
                    and not is_greeting
                    and sources_count > 0
                )
                if is_likely_out_of_scope:
                    logger.info(
                        f"Low retrieval confidence ({retrieval_confidence:.2f}) for query: {text_content[:100]}"
                    )

            # --- 7. Build system prompt with context ---
            context_text = ""
            if top_chunks:
                context_text = "Relevant information from knowledge base:\n\n"
                for i, c in enumerate(top_chunks[:8], 1):
                    meta = c["embedding"].metadata_json or {}
                    title = meta.get("title", "Untitled")
                    url = meta.get("url", "")
                    content = c["embedding"].content[:500]
                    # Add product indicator if this chunk has product data
                    is_product_chunk = meta.get("is_product", False)
                    product_marker = " [PRODUCT PAGE]" if is_product_chunk else ""
                    context_text += f"[Source {i}]{product_marker} Title: {title}\nURL: {url}\n{content}\n\n"

                # If products were extracted, add explicit note
                if len(products) > 0:
                    context_text += f"\n✅ IMPORTANT: {len(products)} product(s) matching the query have been found and will be shown in the carousel.\n"

            # Build context strings
            image_context = ""
            if image_attrs and image_attrs.confidence >= VISION_CONFIDENCE_THRESHOLD:
                # Use enhanced formatting from VisionService
                image_context = "\n\n" + VisionService.format_image_context_for_llm(
                    image_attrs
                )

                # Add clarification question if needed
                if (
                    image_attrs.needs_clarification
                    and image_attrs.clarification_question
                ):
                    image_context += f"\nNote: Image may need clarification. Suggested question: {image_attrs.clarification_question}"

            price_context = ""
            if price_filter:
                if "max_price" in price_filter and "min_price" in price_filter:
                    price_context = f"\n\nPrice Filter Applied: Showing products between {price_filter['min_price']} and {price_filter['max_price']}"
                elif "max_price" in price_filter:
                    price_context = f"\n\nPrice Filter Applied: Showing products under {price_filter['max_price']}"
                elif "min_price" in price_filter:
                    price_context = f"\n\nPrice Filter Applied: Showing products above {price_filter['min_price']}"

                # If products exist and filter applied, LLM should acknowledge the filter
                if len(products) > 0:
                    price_context += f" ({len(products)} products match)"

            attribute_context = ""
            if attribute_filter:
                if "color" in attribute_filter:
                    attribute_context += (
                        f"\n\nColor Filter Applied: {attribute_filter['color']}"
                    )
                    if len(products) > 0:
                        attribute_context += f" ({len(products)} products match)"
                if (
                    "gender" in attribute_filter
                    and attribute_filter["gender"] != "unisex"
                ):
                    attribute_context += (
                        f"\n\nCategory: {attribute_filter['gender'].title()}'s products"
                    )

            # Determine if we have relevant context
            has_relevant_context = retrieval_confidence > 0.5 and sources_count > 0

            # Safe chatbot display name (prevent "undefined", URLs, or empty name)
            chatbot_display_name = _sanitize_display_name(chatbot.name)
            chatbot_raw_name = (
                chatbot.name or ""
            ).strip()  # Keep raw for URL scrubbing

            # Build product carousel instruction (now that we KNOW if products exist)
            product_carousel_instruction = ""
            has_products_to_show = len(products) > 0

            if has_products_to_show:
                product_carousel_instruction = (
                    "\n\n**🎯 CRITICAL - PRODUCT CAROUSEL ACTIVE:**\n"
                    f"We have found {len(products)} products matching the user's request. A product carousel with images, prices, and links will be displayed automatically.\n\n"
                    "**YOUR TASK (MANDATORY):**\n"
                    "1. Write ONLY 1-2 SHORT sentences acknowledging what the user is looking for\n"
                    "2. Examples: 'Here are some great options!', 'I found these for you!', 'Take a look at these!'\n"
                    "3. DO NOT list product names, prices, or create bullet lists - the carousel shows all details\n"
                    "4. DO NOT mark this query as [[IRRELEVANT]] - products exist!\n"
                    "5. DO NOT write rejection messages like 'I can only assist with...'"
                )

            system_prompt = (
                f"You are a helpful AI assistant for {chatbot_display_name}. "
                "Your role is to answer questions STRICTLY based on the provided context.\n\n"
                "**CRITICAL RULES - MUST FOLLOW:**\n"
                "1. **ONLY USE PROVIDED CONTEXT**: You can ONLY answer questions using information explicitly present in the 'Relevant information from knowledge base' section below.\n"
                "2. **NO FABRICATION**: NEVER make up, invent, or hallucinate information. If the context doesn't contain the answer, admit it.\n"
                "3. **NO GENERAL KNOWLEDGE**: Do NOT use your general knowledge to answer questions about products, services, prices, policies, people, companies, or any factual information that isn't in the context.\n"
                "4. **OUT-OF-SCOPE HANDLING**: \n"
                "   - For questions about celebrities, news, politics, competitors, or completely unrelated topics, respond with:\n"
                f"     'I'm sorry, I can only assist with questions related to {chatbot_display_name}. Is there something else I can help you with?'\n"
                "   - Then append `[[IRRELEVANT]]` at the end\n"
                f"   - **EXCEPTION**: If the product carousel instruction above says products exist, DO NOT mark as [[IRRELEVANT]] even if context is limited. The products speak for themselves!\n"
                "   - NEVER output the word 'undefined' in your response. Always use the actual business name above.\n"
                "5. **GREETINGS ARE FINE**: You can respond warmly to greetings (Hi, Hello, etc.) without needing context.\n"
                "6. **CONTEXT QUALITY CHECK**: If the retrieved context doesn't seem relevant to the user's question (low similarity), politely say you don't have information about that specific topic.\n"
                "7. **CONVERSATION CONTINUITY**: The user may ask follow-up questions referencing previous messages. Use the conversation history and background context to understand what they're referring to. If they say 'it', 'that', 'those', etc., refer to the conversation history to understand the reference.\n\n"
                "**Response Formatting:**\n"
                "- Be friendly and conversational\n"
                "- Use HTML formatting appropriately for better readability:\n"
                "  • <strong>text</strong> for important terms, product names, key features, prices\n"
                "  • <em>text</em> for emphasis or subtle highlights\n"
                "  • <br> for line breaks when needed\n"
                "  • <ul><li>item</li></ul> for bullet lists (use when listing features, options, benefits)\n"
                "  • <ol><li>item</li></ol> for numbered lists (use for steps or ordered information)\n"
                "- Use lists (<ul> or <ol>) when presenting 3+ items or features\n"
                "- Use <strong> to highlight product names, prices, key specifications\n"
                "- Keep answers well-structured and scannable\n"
                "- DO NOT use markdown symbols (##, *, **, etc.)\n"
                f"{product_carousel_instruction}\n"
                "**Special Cases:**\n"
                "- **Product Listings**: If product carousel is active, keep text to 1-2 sentences only. Products are displayed separately.\n"
                "- **Price Filters**: ONLY mention products within the specified price range from the context.\n"
                "- **Missing Specific Info**: If asked about specific details not in context, say 'I don't have that specific information' and append `[[MISSING_INFO]]`\n\n"
                f"Background Context: {summary}{image_context}{price_context}{attribute_context}\n"
                f"Retrieval Confidence: {retrieval_confidence:.2f} (contexts found: {sources_count})\n"
                f"{context_text}\n"
                "\n"
                "--- STRICT RESPONSE FORMAT ---\n"
                "1. Your Answer (ONLY from the context above, well-formatted with HTML)\n"
                "2. (Optional) `[[IRRELEVANT]]` if query is completely unrelated to the business, OR `[[MISSING_INFO]]` if specific business detail is missing. Do NOT output both.\n"
                "3. `---SUGGESTIONS---`\n"
                "4. JSON list of exactly 3 context-aware, user-perspective suggestions:\n"
                "   - MUST be what the USER would type/click next (not agent questions)\n"
                "   - MUST relate directly to the current conversation context and user's query\n"
                "   - Should be 6-15 words for clarity\n"
                "   - Examples by scenario:\n"
                f'     * If products are shown: ["Show me more options", "What\'s included with purchase?", "Do you offer free shipping?"]\n'
                '     * If discussing product features: ["What colors are available?", "What\'s the price range?", "Show me similar items"]\n'
                '     * If discussing prices: ["Show me products under $50", "Any ongoing discounts?", "What\'s the best value?"]\n'
                f'     * If query is [[IRRELEVANT]]: ["What products do you offer?", "Tell me about {chatbot_display_name}", "How can I contact you?"]\n'
                '     * If query is [[MISSING_INFO]]: ["Show me available products", "Browse your collection", "What can you help me with?"]\n'
                "   - Make suggestions specific to the conversation, not generic\n"
                "5. `---END---`\n"
            )

            llm_messages = [{"role": "system", "content": system_prompt}]

            # Add recent history
            for h in history[-4:]:
                llm_messages.append({"role": h.role.value, "content": h.content})

            # Build user message content
            user_content = f"User question: {text_content}"
            if image_attrs:
                user_content += f"\n\n(User uploaded an image and is looking for: {effective_message})"

            llm_messages.append({"role": "user", "content": user_content})

            # --- 8. Generate streaming response from Groq ---
            sources = []
            for c in top_chunks:
                meta = c["embedding"].metadata_json
                if meta.get("url"):
                    source = ChatSource(
                        title=meta.get("title") or meta.get("url"), url=meta.get("url")
                    )
                    if source not in sources:
                        sources.append(source)

            # Products already extracted earlier (before system prompt construction)
            # This ensures the LLM knows whether products exist when generating the response

            # Stream response from Groq
            full_content = ""
            yielded_len = 0
            stop_yielding = False
            final_message = ""  # Initialize early to prevent UnboundLocalError

            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "llama-3.3-70b-versatile",
                        "messages": llm_messages,
                        "temperature": 0.1,
                        "stream": True,
                    },
                    timeout=60.0,
                ) as response:
                    if response.status_code != 200:
                        error_text = await response.aread()
                        logger.error(f"Groq error: {error_text}")
                        raise Exception("Service error")

                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                break

                            try:
                                chunk = json.loads(data)
                                delta = chunk.get("choices", [{}])[0].get("delta", {})
                                content = delta.get("content", "")

                                if content:
                                    full_content += content

                                    if not stop_yielding:
                                        # Check for markers in the accumulated content
                                        # Markers: [[IRRELEVANT]], [[MISSING_INFO]], ---SUGGESTIONS---
                                        markers = ["[[", "---"]
                                        marker_pos = -1
                                        for m in markers:
                                            pos = full_content.find(m)
                                            if pos != -1:
                                                if marker_pos == -1 or pos < marker_pos:
                                                    marker_pos = pos

                                        if marker_pos != -1:
                                            # We found a delimiter! Yield everything before it.
                                            if yielded_len < marker_pos:
                                                to_yield = full_content[
                                                    yielded_len:marker_pos
                                                ]
                                                if to_yield:
                                                    yield {
                                                        "type": "content",
                                                        "content": to_yield,
                                                    }
                                                yielded_len = marker_pos
                                            stop_yielding = True
                                        else:
                                            # No marker yet. But we must be careful not to yield partial markers.
                                            # e.g. if chunk ends in "[", don't yield it yet.
                                            safe_to_yield_until = len(full_content)
                                            for partial in ["[", "-"]:
                                                if full_content.endswith(partial):
                                                    safe_to_yield_until = min(
                                                        safe_to_yield_until,
                                                        len(full_content)
                                                        - len(partial),
                                                    )
                                                    # Specific check for "[[" or "---" split across chunks
                                                    if (
                                                        partial == "["
                                                        and full_content.endswith("[")
                                                    ):
                                                        # Safe until the first [
                                                        pass

                                            # Simpler buffering: if content ends with potential marker start, wait.
                                            # Most markers start with "[" or "-".
                                            if full_content.endswith(
                                                "["
                                            ) or full_content.endswith("-"):
                                                safe_to_yield_until = (
                                                    len(full_content) - 1
                                                )
                                                if (
                                                    full_content.endswith("-")
                                                    and full_content[-2:] == "--"
                                                ):
                                                    safe_to_yield_until = (
                                                        len(full_content) - 2
                                                    )

                                            if yielded_len < safe_to_yield_until:
                                                to_yield = full_content[
                                                    yielded_len:safe_to_yield_until
                                                ]
                                                if to_yield:
                                                    yield {
                                                        "type": "content",
                                                        "content": to_yield,
                                                    }
                                                yielded_len = safe_to_yield_until
                            except json.JSONDecodeError:
                                continue

            # --- 8. Post-process response ---
            is_irrelevant = "[[IRRELEVANT]]" in full_content
            is_missing_info = "[[MISSING_INFO]]" in full_content

            # Post-processing validation
            if is_missing_info:
                user_lower = text_content.lower().strip()
                response_lower = full_content.lower()

                # Check for greetings (use shared function)
                if _is_greeting(text_content):
                    is_missing_info = False

                # Check for contact info queries
                contact_patterns = [
                    "contact",
                    "reach",
                    "phone",
                    "email",
                    "address",
                    "location",
                    "call",
                    "support",
                ]
                has_contact_query = any(
                    pattern in user_lower for pattern in contact_patterns
                )
                if has_contact_query and len(response_lower) > 20:
                    is_missing_info = False

                # If we found products and are returning them, it's NOT missing info
                if products:
                    is_missing_info = False

            # Clean content — strip tags and sanitize artifacts
            full_content = full_content.replace("[[IRRELEVANT]]", "").replace(
                "[[MISSING_INFO]]", ""
            )

            # --- Generalized response sanitization ---
            # 1. Replace any literal "undefined" with the proper display name
            full_content = re.sub(
                r"\bundefined\b",
                chatbot_display_name,
                full_content,
                flags=re.IGNORECASE,
            )

            # 2. Replace any raw URLs that match the chatbot's name/source with the clean brand name
            #    This handles cases where the LLM echoes back the URL instead of brand name
            if chatbot_raw_name and re.match(
                r"^https?://", chatbot_raw_name, re.IGNORECASE
            ):
                # Escape URL for regex and replace it with clean name everywhere in the response
                escaped_url = re.escape(chatbot_raw_name)
                full_content = re.sub(
                    escaped_url, chatbot_display_name, full_content, flags=re.IGNORECASE
                )
                # Also handle URL without trailing slash
                escaped_url_no_slash = re.escape(chatbot_raw_name.rstrip("/"))
                full_content = re.sub(
                    escaped_url_no_slash,
                    chatbot_display_name,
                    full_content,
                    flags=re.IGNORECASE,
                )
                # Also catch the domain-only variant
                domain = _url_to_domain(chatbot_raw_name)
                if domain:
                    # Replace domain references like "ramrajcotton.in" with brand name
                    full_content = re.sub(
                        r"https?://(?:www\.)?" + re.escape(domain) + r"[/\w.-]*",
                        chatbot_display_name,
                        full_content,
                        flags=re.IGNORECASE,
                    )

            # 3. General: replace any remaining full URLs in the text that look like raw domain echoes
            #    (Only replace if they appear in conversational context like "related to https://...")
            full_content = re.sub(
                r"(related to|about|for|regarding)\s+(https?://[^\s<]+)",
                lambda m: f"{m.group(1)} {chatbot_display_name}",
                full_content,
                flags=re.IGNORECASE,
            )

            # Extract suggestions and final_message BEFORE any logic that uses final_message
            parts = full_content.split("---SUGGESTIONS---")
            final_message = parts[0].strip()
            suggestion_block = parts[1] if len(parts) > 1 else ""

            # --- Fix contradictory IRRELEVANT + products scenario ---
            # If LLM marked IRRELEVANT but we have products, this is a mistake
            # The LLM saw limited context but didn't realize products exist
            if is_irrelevant and products:
                is_irrelevant = False
                logger.warning(
                    f"LLM marked IRRELEVANT but {len(products)} products exist - overriding"
                )

                # CRITICAL: Replace rejection message with friendly product intro
                # The LLM likely wrote "I can only assist with..." which contradicts the carousel
                rejection_patterns = [
                    r"i'm sorry[,.]? i can only assist with",
                    r"i can only help with",
                    r"i can only answer questions about",
                    r"i don't have information about",
                    r"i cannot assist with",
                    r"that (?:question|topic) is (?:outside|beyond)",
                ]

                message_lower = final_message.lower()
                is_rejection_message = any(
                    re.search(pattern, message_lower) for pattern in rejection_patterns
                )

                if is_rejection_message:
                    # Replace the entire rejection message with a friendly product intro
                    final_message = f"Here are some great options from {chatbot_display_name} that match what you're looking for!"
                    logger.info("Replaced LLM rejection message with product intro")

            suggestions = []
            if suggestion_block:
                suggestion_block = suggestion_block.replace("---END---", "").strip()
                json_match = re.search(r"(\[.*?\])", suggestion_block, re.DOTALL)
                if json_match:
                    try:
                        suggestions = json.loads(json_match.group(1))
                    except:
                        suggestions = [
                            q.strip(' "[]')
                            for q in suggestion_block.split("\n")
                            if len(q.strip()) > 5
                        ][:2]

            # --- Sanitize suggestions (same URL/undefined cleanup) ---
            def _sanitize_suggestion(s: str) -> str:
                """Clean a single suggestion string of URLs, 'undefined', etc."""
                if not isinstance(s, str):
                    return str(s)
                # Replace 'undefined'
                s = re.sub(
                    r"\bundefined\b", chatbot_display_name, s, flags=re.IGNORECASE
                )
                # Replace raw URLs with clean brand name
                if chatbot_raw_name and re.match(
                    r"^https?://", chatbot_raw_name, re.IGNORECASE
                ):
                    s = s.replace(chatbot_raw_name, chatbot_display_name)
                    s = s.replace(chatbot_raw_name.rstrip("/"), chatbot_display_name)
                # Catch any remaining URLs in suggestions
                s = re.sub(
                    r'https?://[^\s"\']+', chatbot_display_name, s, flags=re.IGNORECASE
                )
                return s.strip()

            suggestions = [_sanitize_suggestion(s) for s in suggestions if s]

            final_message = re.sub(
                r"---SUGGESTIONS---.*", "", final_message, flags=re.DOTALL
            ).strip()

            # --- 8.5. Cache successful responses (skip images, irrelevant, missing info) ---
            if (
                not image_bytes
                and not is_irrelevant
                and not is_missing_info
                and final_message
                and len(final_message) > 20
            ):
                try:
                    await cache_response(
                        chatbot_id=str(chatbot_id),
                        query=text_content,
                        content=final_message,
                        sources=[{"title": s.title, "url": s.url} for s in sources],
                        suggestions=(
                            suggestions[:2] if isinstance(suggestions, list) else []
                        ),
                        products=[p.dict() for p in products],
                    )
                except Exception as e:
                    logger.debug(f"Cache write error (non-fatal): {e}")

            # --- 9. Save messages to DB ---
            response_time_ms = int((time.time() - start_time) * 1000)

            if is_missing_info:
                was_answered = False
            elif is_irrelevant:
                was_answered = True
            else:
                was_answered = True

            user_metadata = {}
            if image_attrs:
                user_metadata["image_analysis"] = image_attrs.to_dict()
                user_metadata["effective_query"] = effective_message

            user_msg = ChatMessage(
                session_id=session.id,
                role=MessageRole.USER,
                content=text_content or "(Image uploaded)",
                metadata_json=user_metadata,
            )

            assistant_metadata = {
                "suggestions": suggestions,
                "retrieval_confidence": round(retrieval_confidence, 3),
                "sources_count": sources_count,
                "response_time_ms": response_time_ms,
                "was_answered": was_answered,
                "is_irrelevant": is_irrelevant,
                "is_missing_info": is_missing_info,
            }

            assistant_msg = ChatMessage(
                session_id=session.id,
                role=MessageRole.ASSISTANT,
                content=final_message,
                metadata_json=assistant_metadata,
            )
            db.add(user_msg)
            db.add(assistant_msg)

            # Update message counts (user messages only, excludes preview sessions)
            if not is_preview:
                chatbot.message_count = (chatbot.message_count or 0) + 1

                # Get and update global message count (user messages only)
                from app.models.subscription import Subscription

                sub_stmt = select(Subscription).where(
                    Subscription.tenant_id == chatbot.tenant_id
                )
                sub_result = await db.execute(sub_stmt)
                subscription = sub_result.scalar_one_or_none()
                if subscription:
                    subscription.global_message_count = (
                        subscription.global_message_count or 0
                    ) + 1

            # Update summary if needed
            from sqlalchemy import func

            count_stmt = select(func.count(ChatMessage.id)).where(
                ChatMessage.session_id == session.id
            )
            count_res = await db.execute(count_stmt)
            existing_count = count_res.scalar() or 0
            total_messages = existing_count + 2

            if total_messages % 8 == 0:
                new_summary = await ChatService.summarize_conversation(
                    session, history + [user_msg, assistant_msg]
                )
                session.conversation_summary = new_summary

            session.last_message_at = func.now()
            await db.commit()

            # --- 10. Send final metadata ---
            yield {
                "type": "done",
                "sources": [{"title": s.title, "url": s.url} for s in sources],
                "suggestions": suggestions[:2] if isinstance(suggestions, list) else [],
                "products": [p.dict() for p in products],
                "image_analysis": (
                    image_analysis_result.dict() if image_analysis_result else None
                ),
            }

        except Exception as e:
            logger.error(f"Error in streaming chat service: {e}")
            import traceback

            traceback.print_exc()
            yield {"type": "error", "error": str(e)}
