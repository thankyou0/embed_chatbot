"""
Scope Description Generator Service

Auto-generates a chatbot scope description from crawled pages.
Uses homepage, about page, and category/collection pages to build a JSON description
that helps the LLM determine if user queries are in-scope.
"""

import json
import re
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from uuid import UUID

import httpx
from sqlalchemy import select, and_, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings, get_groq_api_key
from app.core.database import get_session_factory
from app.core.logging import get_logger
from app.models.chatbot import Chatbot
from app.models.knowledge import (
    KnowledgeSource,
    CrawledPage,
    KnowledgeSourceStatus,
)

logger = get_logger(__name__)

# Pages to prioritize for description generation
PRIORITY_URL_PATTERNS = [
    r"^https?://[^/]+/?$",                    # Homepage
    r"/about",                                  # About page
    r"/collections/?$",                         # Collections index
    r"/categories/?$",                          # Categories index
    r"/pages/about",                            # Shopify about
    r"/pages/our-story",                        # Our story
    r"/pages/faq",                              # FAQ
    r"/policies/shipping",                      # Shipping policy
    r"/policies/refund",                        # Refund policy
]

# Maximum content length per page to send to LLM
MAX_PAGE_CONTENT = 1500
# Maximum total content to send
MAX_TOTAL_CONTENT = 8000

# Standard e-commerce topics that should always be in-scope
ECOMMERCE_STANDARD_TOPICS = [
    "Shipping & Delivery",
    "Returns & Refunds",
    "Exchange Policy",
    "Order Tracking",
    "Payment Methods",
    "Customer Support",
    "Product Details",
    "Pricing",
    "Discounts & Offers",
    "Size Guide",
    "Warranty",
    "Gift Cards",
    "Bulk Orders",
    "Account & Login",
    "Cancellation Policy",
    "COD (Cash on Delivery)",
    "International Shipping",
    "Store Locator",
    "Contact Information",
]

# Keywords that indicate an e-commerce / online retail business
_ECOMMERCE_KEYWORDS = [
    "e-commerce", "ecommerce", "online store", "online shop",
    "retail", "clothing", "fashion", "jewelry", "jewellery",
    "beauty", "cosmetics", "grooming", "food", "beverages",
    "home decor", "furniture", "electronics", "marketplace",
    "lifestyle", "accessories", "shoes", "footwear", "bags",
    "luggage", "health", "wellness", "supplements", "toys",
    "gifts", "boutique", "apparel", "brand",
]


def _is_ecommerce_business(description: Dict[str, Any]) -> bool:
    """Detect whether the generated scope description is for an e-commerce business."""
    biz_type = (description.get("business_type") or "").lower()
    what_they_sell = (description.get("what_they_sell") or "").lower()
    combined = f"{biz_type} {what_they_sell}"
    return any(kw in combined for kw in _ECOMMERCE_KEYWORDS)


def _ensure_ecommerce_topics(description: Dict[str, Any]) -> Dict[str, Any]:
    """For e-commerce bots, ensure standard topics are always in topics_covered."""
    if not _is_ecommerce_business(description):
        return description

    existing = set(t.lower() for t in description.get("topics_covered", []))
    topics = list(description.get("topics_covered", []))

    for topic in ECOMMERCE_STANDARD_TOPICS:
        if topic.lower() not in existing:
            topics.append(topic)
            existing.add(topic.lower())

    description["topics_covered"] = topics
    logger.info(
        f"E-commerce bot detected — ensured {len(ECOMMERCE_STANDARD_TOPICS)} "
        f"standard topics in scope (total topics: {len(topics)})"
    )
    return description


async def generate_scope_description(
    chatbot_id: UUID,
    db: Optional[AsyncSession] = None,
) -> Optional[Dict[str, Any]]:
    """
    Generate a scope description for a chatbot from its crawled pages.
    
    Queries the DB for key pages (homepage, about, collections), sends them
    to an LLM to produce a structured JSON description, and saves it to the
    chatbot's scope_description column.
    
    Returns the generated description dict, or None on failure.
    """
    own_session = db is None
    if own_session:
        session_factory = get_session_factory()
        db = session_factory()

    try:
        # 1. Get all knowledge sources for this chatbot
        ks_stmt = select(KnowledgeSource.id).where(
            and_(
                KnowledgeSource.chatbot_id == chatbot_id,
                KnowledgeSource.status == KnowledgeSourceStatus.COMPLETED,
            )
        )
        ks_result = await db.execute(ks_stmt)
        ks_ids = [row[0] for row in ks_result.fetchall()]

        if not ks_ids:
            logger.warning(f"No completed knowledge sources for chatbot {chatbot_id}")
            return None

        # 2. Get chatbot name
        chatbot_stmt = select(Chatbot.name).where(Chatbot.id == chatbot_id)
        chatbot_result = await db.execute(chatbot_stmt)
        chatbot_name = chatbot_result.scalar_one_or_none() or "Unknown"

        # 3. Fetch priority pages (homepage, about, collections)
        priority_pages = []
        for pattern in PRIORITY_URL_PATTERNS:
            stmt = (
                select(CrawledPage.url, CrawledPage.title, CrawledPage.content)
                .where(
                    and_(
                        CrawledPage.knowledge_source_id.in_(ks_ids),
                        CrawledPage.is_removed == False,
                        CrawledPage.content.isnot(None),
                        CrawledPage.url.op("~*")(pattern),
                    )
                )
                .limit(2)
            )
            result = await db.execute(stmt)
            for row in result.fetchall():
                if row not in priority_pages:
                    priority_pages.append(row)

        # 4. Get a sample of product pages to understand what they sell
        product_stmt = (
            select(CrawledPage.url, CrawledPage.title, CrawledPage.content)
            .where(
                and_(
                    CrawledPage.knowledge_source_id.in_(ks_ids),
                    CrawledPage.is_removed == False,
                    CrawledPage.is_product == True,
                    CrawledPage.content.isnot(None),
                )
            )
            .order_by(func.random())
            .limit(8)
        )
        product_result = await db.execute(product_stmt)
        product_pages = product_result.fetchall()

        # 5. Get total page counts for context
        total_stmt = select(func.count(CrawledPage.id)).where(
            and_(
                CrawledPage.knowledge_source_id.in_(ks_ids),
                CrawledPage.is_removed == False,
            )
        )
        total_pages = (await db.execute(total_stmt)).scalar() or 0

        product_count_stmt = select(func.count(CrawledPage.id)).where(
            and_(
                CrawledPage.knowledge_source_id.in_(ks_ids),
                CrawledPage.is_removed == False,
                CrawledPage.is_product == True,
            )
        )
        product_count = (await db.execute(product_count_stmt)).scalar() or 0

        # 6. Build content for LLM
        content_parts = []
        total_len = 0

        # Priority pages first
        for url, title, content in priority_pages:
            if total_len >= MAX_TOTAL_CONTENT:
                break
            truncated = (content or "")[:MAX_PAGE_CONTENT]
            content_parts.append(f"--- PAGE: {title or url} ---\nURL: {url}\n{truncated}\n")
            total_len += len(truncated)

        # Then product samples
        for url, title, content in product_pages:
            if total_len >= MAX_TOTAL_CONTENT:
                break
            truncated = (content or "")[:800]  # Less content per product
            content_parts.append(f"--- PRODUCT: {title or url} ---\n{truncated}\n")
            total_len += len(truncated)

        if not content_parts:
            logger.warning(f"No usable content found for chatbot {chatbot_id}")
            return None

        pages_content = "\n".join(content_parts)

        # 7. Build LLM prompt
        system_prompt = (
            "You are analyzing a website's crawled content to generate a concise scope description "
            "for a customer support chatbot. This description will be used to determine if user queries "
            "are relevant to this website.\n\n"
            "Based on the website content below, generate a JSON object with these fields:\n"
            "- brand_name: The brand/company name\n"
            "- business_type: What kind of business (e.g., 'E-commerce clothing brand', 'Online jewelry store')\n"
            "- what_they_sell: A comprehensive description of products/services offered. Be SPECIFIC about "
            "categories and types. Example: 'Sustainable eco-friendly clothing — t-shirts, hoodies, jackets, "
            "joggers, hats, accessories, bags'\n"
            "- topics_covered: Array of topics the chatbot can help with based on site content "
            "(e.g., ['Product details', 'Pricing', 'Shipping', 'Returns', 'Sustainability', 'Size guide'])\n"
            "  For ANY e-commerce / online store / retail business, ALWAYS include ALL of these topics "
            "even if not explicitly found in the crawled content (they are standard for every online store):\n"
            "  'Shipping & Delivery', 'Returns & Refunds', 'Exchange Policy', 'Order Tracking', "
            "  'Payment Methods', 'Customer Support', 'Product Details', 'Pricing', 'Discounts & Offers', "
            "  'Size Guide', 'Warranty', 'Gift Cards', 'Bulk Orders', 'Account & Login', "
            "  'Cancellation Policy', 'COD (Cash on Delivery)', 'International Shipping', 'Store Locator'\n"
            "- not_about: A BRIEF description of what this brand does NOT deal with. Keep this very general "
            "and broad — focus on clearly unrelated domains like 'medical advice, legal services, financial "
            "investing, academic tutoring, government services, automotive repair'. Do NOT list specific "
            "product categories here because an e-commerce store might sell anything.\n\n"
            "IMPORTANT:\n"
            "- Be FACTUAL — only include what you can see in the content\n"
            "- For 'what_they_sell', list actual product categories you see\n"
            "- For 'topics_covered', include standard e-commerce topics even if not in content\n"
            "- For 'not_about', keep it to clearly unrelated SERVICE domains, not product types\n"
            "- Return ONLY valid JSON, no markdown fences, no explanation\n"
        )

        user_prompt = (
            f"Website: {chatbot_name}\n"
            f"Total pages crawled: {total_pages}\n"
            f"Product pages: {product_count}\n\n"
            f"CRAWLED CONTENT:\n{pages_content}"
        )

        # 8. Call LLM
        description = await _call_llm_for_description(system_prompt, user_prompt)
        if not description:
            return None

        # 8b. Ensure standard e-commerce topics are always present
        description = _ensure_ecommerce_topics(description)

        # 9. Add metadata
        description["auto_generated"] = True
        description["last_updated"] = datetime.now(timezone.utc).isoformat()

        # 10. Save to chatbot
        await db.execute(
            update(Chatbot)
            .where(Chatbot.id == chatbot_id)
            .values(scope_description=description)
        )
        await db.commit()

        logger.info(
            f"Generated scope description for chatbot {chatbot_id}: "
            f"brand={description.get('brand_name')}, type={description.get('business_type')}"
        )
        return description

    except Exception as e:
        logger.error(f"Failed to generate scope description for {chatbot_id}: {e}", exc_info=True)
        if own_session:
            await db.rollback()
        return None
    finally:
        if own_session:
            await db.close()


async def _call_llm_for_description(
    system_prompt: str,
    user_prompt: str,
) -> Optional[Dict[str, Any]]:
    """Call LLM (Groq) to generate scope description JSON."""
    providers = []

    # Groq
    providers.append((
        "https://api.groq.com/openai/v1/chat/completions",
        get_groq_api_key(),
        settings.GROQ_CALL2_MODEL,
    ))

    for url, key, model in providers:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    url,
                    headers={
                        "Authorization": f"Bearer {key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        "temperature": 0.1,
                        "max_tokens": 500,
                    },
                )

                if resp.status_code == 200:
                    raw = resp.json()["choices"][0]["message"]["content"].strip()
                    # Strip markdown fences
                    if raw.startswith("```"):
                        raw = re.sub(r"^```\w*\n?", "", raw)
                        raw = re.sub(r"\n?```$", "", raw)
                    raw = raw.strip()

                    parsed = json.loads(raw)

                    # Validate required fields
                    required = ["brand_name", "business_type", "what_they_sell"]
                    if all(parsed.get(f) for f in required):
                        # Ensure topics_covered is a list
                        if not isinstance(parsed.get("topics_covered"), list):
                            parsed["topics_covered"] = []
                        # Ensure not_about is a string
                        if not isinstance(parsed.get("not_about"), str):
                            parsed["not_about"] = ""
                        return parsed
                    else:
                        logger.warning(f"LLM returned incomplete description: {raw[:200]}")
                else:
                    logger.warning(
                        f"LLM call failed ({resp.status_code}) for scope description: {resp.text[:200]}"
                    )
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse scope description JSON: {e}")
        except Exception as e:
            logger.warning(f"Scope description LLM call failed: {e}")

    return None
