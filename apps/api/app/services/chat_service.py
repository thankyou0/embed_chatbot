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


def extract_attribute_filters(message: str) -> Optional[Dict[str, Any]]:
    """
    Extract product attribute filters from user message.
    Returns dict with filters like 'colors', 'styles', etc.
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

        # CRITICAL: Skip collection/listing URLs
        if is_collection_url(url):
            logger.debug(f"Skipping collection URL: {url}")
            continue

        # Validate URL - ensure it's a proper product URL
        if url:
            from urllib.parse import urlparse

            parsed_url = urlparse(url)
            path = parsed_url.path.strip("/")

            # Skip if URL is just the home page or has no product identifier
            if not path or path in ["", "index.html", "home", "index.php"]:
                logger.debug(f"Skipping product with home page URL: {url}")
                continue

        # Note: We trust is_product flag from crawler - if it detected product data,
        # the URL check above is sufficient. No need for strict URL pattern matching.

        # Get product name - use product data name, fall back to page title
        product_name = product_data.get("name") or ""
        page_title = meta.get("title", "")

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
            product_text = f"{product_name} {product_data.get('description', '')} {emb.content}".lower()
            color_match = False
            for color in attribute_filter["colors"]:
                if color in product_text:
                    color_match = True
                    break
            if not color_match:
                logger.debug(f"Skipping product {product_name} - no color match")
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
            # Only skip if the filename itself contains these words, not the path
            img_filename = img.split("/")[-1].lower() if "/" in img else img.lower()
            if any(
                skip in img_filename
                for skip in [
                    "placeholder",
                    "no-image",
                    "noimage",
                    "logo.",
                    "default.",
                    "blank.",
                ]
            ):
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

    return products


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
                paused_message = (
                    f"🚧 {chatbot.name} is currently offline for maintenance. "
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

            # --- 4. Get chat history and summary ---
            history = await ChatService.get_history(db, session.id, limit=6)
            summary = session.conversation_summary or ""

            # --- 5. Retrieve relevant context using RAG ---
            query_embedding = await get_single_embedding(text_content)

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

            # --- Early out-of-scope detection ---
            # Check if this is a greeting (should always be answered)
            greeting_patterns = [
                r"^\s*(hi+|hello+|hey+|heya*|good\s+(morning|afternoon|evening)|howdy|what\'?s\s+up)\s*[!.?]*\s*$",
            ]
            is_greeting = any(
                re.match(p, text_content.lower().strip()) for p in greeting_patterns
            )

            # Very low retrieval confidence + not a greeting = likely out-of-scope
            # We still let the LLM handle it, but this flag helps with post-processing
            is_likely_out_of_scope = (
                retrieval_confidence < 0.35 and not is_greeting and sources_count > 0
            )

            # Log for debugging
            if is_likely_out_of_scope:
                logger.info(
                    f"Low retrieval confidence ({retrieval_confidence:.2f}) for query: {text_content[:100]}"
                )

            # --- 6. Build system prompt with context ---
            context_text = ""
            if top_chunks:
                context_text = "Relevant information from knowledge base:\n\n"
                for i, c in enumerate(top_chunks[:8], 1):
                    meta = c["embedding"].metadata_json or {}
                    title = meta.get("title", "Untitled")
                    url = meta.get("url", "")
                    content = c["embedding"].content[:500]
                    context_text += (
                        f"[Source {i}] Title: {title}\nURL: {url}\n{content}\n\n"
                    )

            # Extract filters
            price_filter = extract_price_filter(text_content)
            attribute_filter = extract_attribute_filters(text_content)

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
                    price_context = f"\n\nPrice Filter: Between {price_filter['min_price']} and {price_filter['max_price']}"
                elif "max_price" in price_filter:
                    price_context = (
                        f"\n\nPrice Filter: Under {price_filter['max_price']}"
                    )
                elif "min_price" in price_filter:
                    price_context = (
                        f"\n\nPrice Filter: Above {price_filter['min_price']}"
                    )

            attribute_context = ""
            if attribute_filter:
                if "color" in attribute_filter:
                    attribute_context += (
                        f"\n\nColor Filter: {attribute_filter['color']}"
                    )

            # Determine if we have relevant context
            has_relevant_context = retrieval_confidence > 0.5 and sources_count > 0

            system_prompt = (
                f"You are a helpful AI assistant for {chatbot.name}. "
                "Your role is to answer questions STRICTLY based on the provided context.\n\n"
                "**CRITICAL RULES - MUST FOLLOW:**\n"
                "1. **ONLY USE PROVIDED CONTEXT**: You can ONLY answer questions using information explicitly present in the 'Relevant information from knowledge base' section below.\n"
                "2. **NO FABRICATION**: NEVER make up, invent, or hallucinate information. If the context doesn't contain the answer, admit it.\n"
                "3. **NO GENERAL KNOWLEDGE**: Do NOT use your general knowledge to answer questions about products, services, prices, policies, people, companies, or any factual information that isn't in the context.\n"
                "4. **OUT-OF-SCOPE HANDLING**: For questions about topics NOT covered in the context (e.g., celebrities, competitors, unrelated products, general knowledge), respond with:\n"
                f"   'I'm sorry, I can only help with questions about {chatbot.name} and the information I have access to. Is there something specific about {chatbot.name} I can help you with?'\n"
                "   Then append `[[IRRELEVANT]]` at the end.\n"
                "5. **GREETINGS ARE FINE**: You can respond warmly to greetings (Hi, Hello, etc.) without needing context.\n"
                "6. **CONTEXT QUALITY CHECK**: If the retrieved context doesn't seem relevant to the user's question (low similarity), politely say you don't have information about that specific topic.\n\n"
                "**Response Formatting (Fix #5):**\n"
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
                "- DO NOT use markdown symbols (##, *, **, etc.)\n\n"
                "**Special Cases:**\n"
                "- **Product Listings**: If product carousel will show, just say 'Here are our products:' or similar. Don't list details.\n"
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
                "4. JSON list of exactly 3 context-aware, user-perspective suggestions (Fix #6):\n"
                "   - MUST be what the USER would type/click next (not agent questions)\n"
                "   - MUST relate directly to the current conversation context and user's query\n"
                "   - Should be 6-15 words for clarity\n"
                "   - Examples:\n"
                '     * If discussing product features: ["Show me similar products", "What\'s the price range?", "Do you have this in other colors?"]\n'
                '     * If discussing prices: ["Show me products under $50", "What\'s included in the price?", "Any ongoing discounts?"]\n'
                '     * If query is [[IRRELEVANT]]: ["What products do you offer?", "Tell me about your services", "How can I contact you?"]\n'
                '     * If query is [[MISSING_INFO]]: ["Show me available products", "Browse your collection", "What can you help me with?"]\n'
                "   - Avoid generic suggestions - make them specific to the current context\n"
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

            # --- 7. Generate streaming response from Groq ---
            sources = []
            for c in top_chunks:
                meta = c["embedding"].metadata_json
                if meta.get("url"):
                    source = ChatSource(
                        title=meta.get("title") or meta.get("url"), url=meta.get("url")
                    )
                    if source not in sources:
                        sources.append(source)

            # Extract products if this is a product-related query
            products = []
            if is_product_query(text_content) or (image_attrs is not None):
                products = extract_products_from_chunks(
                    combined_results[:30],
                    limit=10,
                    price_filter=price_filter,
                    attribute_filter=attribute_filter,
                )

            # Stream response from Groq
            full_content = ""
            yielded_len = 0
            stop_yielding = False

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
            # Post-processing validation
            if is_missing_info:
                user_lower = text_content.lower().strip()
                response_lower = full_content.lower()

                # Check for greetings
                greeting_patterns = [
                    r"\bhi+\b",
                    r"\bhello+\b",
                    r"\bhey+\b",
                    r"\bheya+\b",
                    r"\bgood\s+morning",
                    r"\bgood\s+afternoon",
                    r"\bgood\s+evening",
                    r"\bhowdy\b",
                    r"\bwhat\'?s\s+up\b",
                ]
                is_greeting = any(re.search(p, user_lower) for p in greeting_patterns)

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
                # If user asks for contact and we give a response (even if generic), don't mark as missing info
                # The prompt should prevent MISSING_INFO tag here, but as a fallback:
                if has_contact_query:
                    # If response contains helpful keywords or is not just "I don't know"
                    if len(response_lower) > 20:
                        is_missing_info = False

                # Check for product queries
                # If we found products and are returning them, it's NOT missing info
                if products:
                    is_missing_info = False

                if is_greeting:
                    is_missing_info = False

            # Clean content
            full_content = full_content.replace("[[IRRELEVANT]]", "").replace(
                "[[MISSING_INFO]]", ""
            )

            # Extract suggestions
            parts = full_content.split("---SUGGESTIONS---")
            final_message = parts[0].strip()
            suggestion_block = parts[1] if len(parts) > 1 else ""

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

            final_message = re.sub(
                r"---SUGGESTIONS---.*", "", final_message, flags=re.DOTALL
            ).strip()

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

            # Update message counts (only for non-preview chats)
            if not is_preview:
                # Increment per-chatbot message count
                chatbot.message_count = (chatbot.message_count or 0) + 1

                # Get and update global message count
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
