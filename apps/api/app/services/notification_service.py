"""
Crawl Notification Service

Creates persistent notifications for crawl events so users never miss
important status updates — even if they navigate away from the page.
"""

from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, update, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session_factory
from app.core.logging import get_logger
from app.models.knowledge import (
    CrawlNotification,
    CrawlNotificationType,
    KnowledgeSource,
)

logger = get_logger(__name__)


async def create_notification(
    knowledge_source_id: str,
    notification_type: CrawlNotificationType,
    message: str,
    severity: str = "info",
    db: Optional[AsyncSession] = None,
) -> CrawlNotification:
    """
    Create a persistent crawl notification.

    Args:
        knowledge_source_id: The knowledge source this notification belongs to.
        notification_type: Type of event (e.g. CRAWL_COMPLETED, JS_HEAVY_DETECTED).
        message: User-facing message text.
        severity: "info" | "success" | "warning" | "error"
        db: Optional DB session. If None, creates its own session.
    """
    own_session = db is None
    if own_session:
        session_factory = get_session_factory()
        db = session_factory()

    try:
        notification = CrawlNotification(
            knowledge_source_id=knowledge_source_id,
            notification_type=notification_type.value,
            message=message,
            severity=severity,
            is_read=False,
        )
        db.add(notification)
        await db.commit()
        await db.refresh(notification)

        logger.info(
            f"Notification created [{severity}] for KS {knowledge_source_id}: "
            f"{notification_type.value} — {message[:80]}"
        )
        return notification
    except Exception as e:
        logger.error(f"Failed to create notification: {e}")
        if own_session:
            await db.rollback()
        raise
    finally:
        if own_session:
            await db.close()


async def get_unread_notifications(
    chatbot_id: UUID,
    db: AsyncSession,
    limit: int = 50,
) -> List[CrawlNotification]:
    """
    Fetch unread notifications for all knowledge sources belonging to a chatbot.
    Returns newest first. Joins through knowledge_sources to filter by chatbot_id.
    """
    stmt = (
        select(CrawlNotification)
        .join(
            KnowledgeSource,
            KnowledgeSource.id == CrawlNotification.knowledge_source_id,
        )
        .where(
            and_(
                KnowledgeSource.chatbot_id == chatbot_id,
                CrawlNotification.is_read == False,
            )
        )
        .order_by(CrawlNotification.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_all_notifications(
    chatbot_id: UUID,
    db: AsyncSession,
    limit: int = 100,
) -> List[CrawlNotification]:
    """
    Fetch all recent notifications for a chatbot (read and unread).
    """
    stmt = (
        select(CrawlNotification)
        .join(
            KnowledgeSource,
            KnowledgeSource.id == CrawlNotification.knowledge_source_id,
        )
        .where(KnowledgeSource.chatbot_id == chatbot_id)
        .order_by(CrawlNotification.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def mark_notifications_read(
    notification_ids: List[str],
    db: AsyncSession,
) -> int:
    """
    Mark specific notifications as read. Returns count of updated rows.
    """
    if not notification_ids:
        return 0

    from uuid import UUID as _UUID

    uuids = [_UUID(nid) for nid in notification_ids]
    result = await db.execute(
        update(CrawlNotification)
        .where(CrawlNotification.id.in_(uuids))
        .values(is_read=True)
    )
    await db.commit()
    return result.rowcount


async def mark_all_read_for_chatbot(
    chatbot_id: UUID,
    db: AsyncSession,
) -> int:
    """
    Mark all notifications for a chatbot as read.
    """
    ks_ids = select(KnowledgeSource.id).where(
        KnowledgeSource.chatbot_id == chatbot_id
    )
    result = await db.execute(
        update(CrawlNotification)
        .where(
            and_(
                CrawlNotification.knowledge_source_id.in_(ks_ids),
                CrawlNotification.is_read == False,
            )
        )
        .values(is_read=True)
    )
    await db.commit()
    return result.rowcount


async def delete_old_notifications(
    days: int = 30,
    db: Optional[AsyncSession] = None,
) -> int:
    """
    Cleanup: delete notifications older than N days.
    Intended to be called by the scheduler periodically.
    """
    from datetime import datetime, timezone, timedelta

    own_session = db is None
    if own_session:
        session_factory = get_session_factory()
        db = session_factory()

    try:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        result = await db.execute(
            delete(CrawlNotification).where(
                CrawlNotification.created_at < cutoff
            )
        )
        await db.commit()
        count = result.rowcount
        if count:
            logger.info(f"Cleaned up {count} notifications older than {days} days")
        return count
    finally:
        if own_session:
            await db.close()
