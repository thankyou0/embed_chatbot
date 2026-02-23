"""Analytics Service for chatbot metrics

Unanswered Query Classification:
================================

The classification happens at RESPONSE TIME in the chat service, using LLM intelligence.
The LLM adds tags to its response:

1. [[IRRELEVANT]] - Query is OUT OF SCOPE (celebrities, general trivia, unrelated topics)
   - Examples: "who is elon musk?", "what's the weather?", "tell me about Mit Vaghani"
   - These are NOT knowledge gaps - the chatbot was never meant to answer these
   - Stored in metadata as: is_irrelevant = True, was_answered = True

2. [[MISSING_INFO]] - Query is RELEVANT but couldn't be answered (TRUE KNOWLEDGE GAP)
   - Examples: "what's your refund policy?", "do you ship to Canada?"
   - These ARE knowledge gaps - should be added to knowledge base
   - Stored in metadata as: is_missing_info = True, was_answered = False

3. No tag - Query was successfully answered OR was a greeting/pleasantry
   - Stored in metadata as: was_answered = True

Analytics Logic:
- Unanswered Queries = ONLY those with is_missing_info = True
- This uses LLM intelligence to classify, not pattern matching
- Greetings and irrelevant queries are automatically excluded
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID
import sqlalchemy as sa
from sqlalchemy import select, func, and_, or_, cast, Float, update, Integer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import JSONB

from app.models.chat import ChatSession, ChatMessage, MessageRole
from app.models.chatbot import Chatbot
from app.models.user import User
from app.core.exceptions import (
    UnauthorizedError,
    NotFoundError,
    ForbiddenError,
)
from app.schemas.analytics import (
    AnalyticsOverviewResponse,
    UnansweredQueriesResponse,
    UnansweredQuery,
    UnansweredQuerySample,
    ResolveQueriesRequest,
)
from app.services.chatbot_service import ChatbotService
from app.core.logging import get_logger

logger = get_logger(__name__)


class AnalyticsService:
    """
    Analytics service that uses LLM-classified metadata from chat responses.

    The classification is done at response time in chat_service.py where the LLM tags:
    - [[IRRELEVANT]] for out-of-scope queries → is_irrelevant=True, was_answered=True
    - [[MISSING_INFO]] for knowledge gaps → is_missing_info=True, was_answered=False

    Unanswered queries = ONLY those with is_missing_info=True (true knowledge gaps)
    """

    @staticmethod
    def _get_period_start(period: str) -> datetime:
        """Convert period string to datetime"""
        now = datetime.utcnow()
        if period == "7d":
            return now - timedelta(days=7)
        elif period == "30d":
            return now - timedelta(days=30)
        elif period == "90d":
            return now - timedelta(days=90)
        else:
            return now - timedelta(days=30)  # default

    @staticmethod
    async def get_analytics_overview(
        db: AsyncSession,
        tenant_id: int,
        chatbot_id: Optional[UUID],
        user: User,
        period: str = "30d",
    ) -> AnalyticsOverviewResponse:
        """Get analytics overview with deflection and unanswered rates - OPTIMIZED"""

        period_start = AnalyticsService._get_period_start(period)

        # Build base filters
        session_filters = [
            ChatSession.started_at >= period_start,
            ChatSession.is_preview == False,
        ]

        if chatbot_id:
            # Verify access to specific chatbot
            await ChatbotService.get_chatbot(db, tenant_id, chatbot_id, user)

            if not await ChatbotService.has_permission(
                db, chatbot_id, user, "can_view_analytics_billing"
            ):
                raise ForbiddenError("Insufficient permissions to view analytics")

            session_filters.append(ChatSession.chatbot_id == chatbot_id)
        else:
            # Get all chatbot IDs user has access to
            chatbots = await ChatbotService.list_chatbots(db, tenant_id, user)
            chatbot_ids = [c.id for c in chatbots]
            if not chatbot_ids:
                return AnalyticsOverviewResponse(
                    total_sessions=0,
                    total_messages=0,
                    avg_messages_per_session=0.0,
                    deflection_rate=0.0,
                    unanswered_rate=0.0,
                    period=period,
                )
            session_filters.append(ChatSession.chatbot_id.in_(chatbot_ids))

        # OPTIMIZATION: Count sessions directly without loading all data
        total_sessions_result = await db.execute(
            select(func.count(ChatSession.id)).where(and_(*session_filters))
        )
        total_sessions = total_sessions_result.scalar() or 0

        if total_sessions == 0:
            return AnalyticsOverviewResponse(
                total_sessions=0,
                total_messages=0,
                avg_messages_per_session=0.0,
                deflection_rate=0.0,
                unanswered_rate=0.0,
                period=period,
            )

        # OPTIMIZATION: Get session IDs efficiently with subquery
        session_ids_subquery = select(ChatSession.id).where(and_(*session_filters))

        # OPTIMIZATION: Count messages with JOIN instead of loading all
        total_messages_result = await db.execute(
            select(func.count(ChatMessage.id)).where(
                and_(
                    ChatMessage.session_id.in_(session_ids_subquery),
                    ChatMessage.role == MessageRole.USER,
                )
            )
        )
        total_messages = total_messages_result.scalar() or 0

        # OPTIMIZATION: Use database aggregation for deflection and unanswered rates
        # Calculate deflection rate using aggregation (sessions where all bot messages were answered)
        # This is more complex, so we'll use a simplified approach with fewer queries

        # Get statistics from bot messages using JSONB operators
        bot_message_stats_result = await db.execute(
            select(
                func.count().label("total_bot_messages"),
                func.sum(
                    func.cast(
                        (
                            ChatMessage.metadata_json["was_answered"].astext == "true"
                        ).cast(sa.Integer),
                        sa.Integer,
                    )
                ).label("answered_messages"),
                func.sum(
                    func.cast(
                        (
                            ChatMessage.metadata_json["is_irrelevant"].astext == "true"
                        ).cast(sa.Integer),
                        sa.Integer,
                    )
                ).label("irrelevant_messages"),
                func.sum(
                    func.cast(
                        (
                            ChatMessage.metadata_json["is_missing_info"].astext
                            == "true"
                        ).cast(sa.Integer),
                        sa.Integer,
                    )
                ).label("missing_info_messages"),
            ).where(
                and_(
                    ChatMessage.session_id.in_(session_ids_subquery),
                    ChatMessage.role == MessageRole.ASSISTANT,
                )
            )
        )
        bot_stats = bot_message_stats_result.one()

        total_bot_messages = bot_stats.total_bot_messages or 0
        answered_messages = bot_stats.answered_messages or 0
        irrelevant_messages = bot_stats.irrelevant_messages or 0
        missing_info_messages = bot_stats.missing_info_messages or 0

        # Calculate rates
        # Deflection rate = % of bot messages that were answered
        deflection_rate = (
            (answered_messages / total_bot_messages * 100)
            if total_bot_messages > 0
            else 0.0
        )

        # Total meaningful queries = all responses except irrelevant ones
        total_meaningful = total_bot_messages - irrelevant_messages

        # Unanswered rate = % of meaningful queries with missing info
        unanswered_rate = (
            (missing_info_messages / total_meaningful * 100)
            if total_meaningful > 0
            else 0.0
        )

        # Calculate average messages per session
        avg_messages = total_messages / total_sessions if total_sessions > 0 else 0.0

        return AnalyticsOverviewResponse(
            total_sessions=total_sessions,
            total_messages=total_messages,
            avg_messages_per_session=round(avg_messages, 1),
            deflection_rate=round(deflection_rate, 1),
            unanswered_rate=round(unanswered_rate, 1),
            period=period,
        )

    @staticmethod
    async def get_unanswered_queries(
        db: AsyncSession,
        tenant_id: int,
        chatbot_id: UUID,
        user: User,
        period: str = "30d",
        limit: int = 20,
        query_type: Optional[str] = None,  # 'missing_info' or 'reported'
    ) -> UnansweredQueriesResponse:
        """
        Get unanswered queries for a chatbot.

        query_type:
        - 'missing_info': Bot couldn't answer (LLM-classified is_missing_info=True)
        - 'reported': User-reported unsatisfactory answers (user_reported=True)
        - None: All unanswered queries (both types)
        """

        # Verify access
        await ChatbotService.get_chatbot(db, tenant_id, chatbot_id, user)

        if not await ChatbotService.has_permission(
            db, chatbot_id, user, "can_view_analytics_billing"
        ):
            raise ForbiddenError("Insufficient permissions to view analytics")

        period_start = AnalyticsService._get_period_start(period)

        # Get all sessions for this chatbot in the period
        sessions_query = select(ChatSession).where(
            and_(
                ChatSession.chatbot_id == chatbot_id,
                ChatSession.started_at >= period_start,
            )
        )

        sessions_result = await db.execute(sessions_query)
        sessions = sessions_result.scalars().all()
        session_ids = [s.id for s in sessions]

        if not session_ids:
            return UnansweredQueriesResponse(queries=[], total_unanswered=0)

        # Get all messages
        messages_query = (
            select(ChatMessage)
            .where(ChatMessage.session_id.in_(session_ids))
            .order_by(ChatMessage.created_at)
        )

        messages_result = await db.execute(messages_query)
        all_messages = messages_result.scalars().all()

        # Build a per-session ordered list for position-based pairing
        # This avoids timestamp-equality bugs when user+assistant messages
        # are committed in the same transaction (identical created_at).
        session_messages: dict = {}
        for m in all_messages:
            session_messages.setdefault(m.session_id, []).append(m)

        # Find TRUE knowledge gap queries (is_missing_info=True)
        # This excludes:
        # - Greetings (LLM handles these, no tags)
        # - Out-of-scope queries (is_irrelevant=True)
        # - Successfully answered queries (was_answered=True, no is_missing_info)
        unanswered_messages = []

        for sid, msgs in session_messages.items():
            for i, msg in enumerate(msgs):
                if msg.role != MessageRole.USER:
                    continue
                # Find the immediately following assistant message in this session
                bot_response = None
                for j in range(i + 1, len(msgs)):
                    if msgs[j].role == MessageRole.ASSISTANT:
                        bot_response = msgs[j]
                        break

                if not bot_response:
                    continue

                metadata = bot_response.metadata_json or {}

                # Skip if this query has been manually marked as resolved
                if metadata.get("resolved", False):
                    continue

                # Filter based on query_type parameter
                is_missing_info = metadata.get("is_missing_info", False)
                is_reported = metadata.get("user_reported", False)

                # Apply filter based on query_type
                if query_type == "missing_info":
                    if not is_missing_info:
                        continue
                elif query_type == "reported":
                    if not is_reported:
                        continue
                else:
                    # If no type specified, include both
                    if not (is_missing_info or is_reported):
                        continue

                confidence = metadata.get("retrieval_confidence", 0.0)
                unanswered_messages.append(
                    {
                        "message": msg,
                        "bot_response": bot_response.content if bot_response else None,
                        "confidence": confidence,
                    }
                )

        # Group by exact query text (simple grouping, no clustering yet)
        query_groups = {}
        for item in unanswered_messages:
            msg = item["message"]
            query_text = msg.content.strip().lower()

            if query_text not in query_groups:
                query_groups[query_text] = {
                    "original_query": msg.content,
                    "messages": [],
                    "confidences": [],
                }

            query_groups[query_text]["messages"].append(
                {"msg": msg, "bot_response": item["bot_response"]}
            )
            query_groups[query_text]["confidences"].append(item["confidence"])

        # Build response
        queries = []
        for query_text, data in query_groups.items():
            messages = data["messages"]
            confidences = data["confidences"]

            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

            # Get up to 3 sample messages
            samples = [
                UnansweredQuerySample(
                    id=m["msg"].id,
                    content=m["msg"].content,
                    bot_response=m["bot_response"],
                    created_at=m["msg"].created_at,
                )
                for m in messages[:3]
            ]

            queries.append(
                UnansweredQuery(
                    query=data["original_query"],
                    count=len(messages),
                    avg_confidence=round(avg_confidence, 3),
                    first_asked=min(m["msg"].created_at for m in messages),
                    last_asked=max(m["msg"].created_at for m in messages),
                    sample_messages=samples,
                )
            )

        # Sort by count descending
        queries.sort(key=lambda q: q.count, reverse=True)

        return UnansweredQueriesResponse(
            queries=queries[:limit], total_unanswered=len(unanswered_messages)
        )

    @staticmethod
    async def resolve_queries(
        db: AsyncSession,
        tenant_id: int,
        chatbot_id: UUID,
        user: User,
        query_texts: List[str],
    ) -> None:
        """Mark queries as resolved for a chatbot"""
        # Verify access
        # Verify access
        chatbot = await ChatbotService.get_chatbot(db, tenant_id, chatbot_id, user)

        if not await ChatbotService.has_permission(
            db, chatbot_id, user, "can_resolve_queries"
        ):
            raise ForbiddenError("Insufficient permissions to resolve queries")

        # For now, we'll store resolved queries in a simple way
        # In a production system, you'd want a proper resolved_queries table
        # For now, we'll update the messages' metadata to mark them as resolved
        # by updating the assistant messages' metadata

        # Get all sessions for this chatbot
        sessions_query = select(ChatSession).where(ChatSession.chatbot_id == chatbot_id)
        sessions_result = await db.execute(sessions_query)
        sessions = sessions_result.scalars().all()
        session_ids = [s.id for s in sessions]

        if not session_ids:
            return

        # Normalize query texts for comparison (lowercase)
        normalized_queries = [q.strip().lower() for q in query_texts]

        # Find all user messages matching these queries
        messages_query = select(ChatMessage).where(
            and_(
                ChatMessage.session_id.in_(session_ids),
                ChatMessage.role == MessageRole.USER,
            )
        )
        messages_result = await db.execute(messages_query)
        all_user_messages = messages_result.scalars().all()

        # Find matching messages and mark their corresponding assistant responses as resolved
        matching_message_ids = []
        for msg in all_user_messages:
            if msg.content.strip().lower() in normalized_queries:
                matching_message_ids.append(msg.id)

        if not matching_message_ids:
            await db.commit()
            return

        # Update corresponding assistant messages to mark them as resolved
        # Find assistant messages that follow these user messages
        for user_msg_id in matching_message_ids:
            # Get the user message
            user_msg_stmt = select(ChatMessage).where(ChatMessage.id == user_msg_id)
            user_msg_result = await db.execute(user_msg_stmt)
            user_msg = user_msg_result.scalar_one_or_none()

            if not user_msg:
                continue

            # Find the next assistant message for this session
            assistant_msg_stmt = (
                select(ChatMessage)
                .where(
                    and_(
                        ChatMessage.session_id == user_msg.session_id,
                        ChatMessage.role == MessageRole.ASSISTANT,
                        ChatMessage.created_at > user_msg.created_at,
                    )
                )
                .order_by(ChatMessage.created_at)
                .limit(1)
            )

            assistant_result = await db.execute(assistant_msg_stmt)
            assistant_msg = assistant_result.scalar_one_or_none()

            if assistant_msg:
                # Update metadata to mark as resolved
                metadata = assistant_msg.metadata_json or {}
                metadata["resolved"] = True
                metadata["resolved_at"] = datetime.utcnow().isoformat()
                metadata["resolved_by"] = str(user.id)

                await db.execute(
                    update(ChatMessage)
                    .where(ChatMessage.id == assistant_msg.id)
                    .values(metadata_json=metadata)
                )

        await db.commit()
        logger.info(
            f"Resolved {len(matching_message_ids)} queries for chatbot {chatbot_id}"
        )

    @staticmethod
    async def report_message(
        db: AsyncSession, chatbot_id: UUID, session_id: str, message_content: str
    ) -> None:
        """Mark a message as reported by user (unsatisfactory answer)"""

        # Find the session
        session_stmt = select(ChatSession).where(
            and_(
                ChatSession.chatbot_id == chatbot_id, ChatSession.id == UUID(session_id)
            )
        )
        session_result = await db.execute(session_stmt)
        session = session_result.scalar_one_or_none()

        if not session:
            raise ValueError("Session not found")

        # Find the user message with this content (try exact match first, then partial)
        # Exact match
        user_msg_stmt = (
            select(ChatMessage)
            .where(
                and_(
                    ChatMessage.session_id == session.id,
                    ChatMessage.role == MessageRole.USER,
                    ChatMessage.content == message_content,
                )
            )
            .order_by(ChatMessage.created_at.desc())
            .limit(1)
        )

        user_msg_result = await db.execute(user_msg_stmt)
        user_msg = user_msg_result.scalar_one_or_none()

        # If exact match not found, try trimmed match
        if not user_msg:
            user_msg_stmt = (
                select(ChatMessage)
                .where(
                    and_(
                        ChatMessage.session_id == session.id,
                        ChatMessage.role == MessageRole.USER,
                    )
                )
                .order_by(ChatMessage.created_at.desc())
            )

            user_msg_result = await db.execute(user_msg_stmt)
            all_user_msgs = user_msg_result.scalars().all()

            # Find by trimmed content match
            trimmed_content = message_content.strip()
            for msg in all_user_msgs:
                if msg.content.strip() == trimmed_content:
                    user_msg = msg
                    break

        if not user_msg:
            # If still not found, just get the last user message in this session
            user_msg_stmt = (
                select(ChatMessage)
                .where(
                    and_(
                        ChatMessage.session_id == session.id,
                        ChatMessage.role == MessageRole.USER,
                    )
                )
                .order_by(ChatMessage.created_at.desc())
                .limit(1)
            )

            user_msg_result = await db.execute(user_msg_stmt)
            user_msg = user_msg_result.scalar_one_or_none()

            if not user_msg:
                # Streaming failures can leave an empty session; reporting should stay
                # non-fatal for clients in that case.
                logger.warning(
                    f"Report skipped for session {session_id}: no user messages found"
                )
                return

        # Find the corresponding assistant response
        assistant_stmt = (
            select(ChatMessage)
            .where(
                and_(
                    ChatMessage.session_id == session.id,
                    ChatMessage.role == MessageRole.ASSISTANT,
                    ChatMessage.created_at > user_msg.created_at,
                )
            )
            .order_by(ChatMessage.created_at)
            .limit(1)
        )

        assistant_result = await db.execute(assistant_stmt)
        assistant_msg = assistant_result.scalar_one_or_none()

        if not assistant_msg:
            # Try to get the last assistant message if ordering issue
            assistant_stmt = (
                select(ChatMessage)
                .where(
                    and_(
                        ChatMessage.session_id == session.id,
                        ChatMessage.role == MessageRole.ASSISTANT,
                    )
                )
                .order_by(ChatMessage.created_at.desc())
                .limit(1)
            )

            assistant_result = await db.execute(assistant_stmt)
            assistant_msg = assistant_result.scalar_one_or_none()

            if not assistant_msg:
                logger.warning(
                    f"Report skipped for session {session_id}: no assistant messages found"
                )
                return

        # Update the assistant message metadata to mark as reported
        metadata = assistant_msg.metadata_json or {}

        # Don't overwrite if already reported
        if not metadata.get("user_reported"):
            metadata["user_reported"] = True
            metadata["reported_at"] = datetime.utcnow().isoformat()

            await db.execute(
                update(ChatMessage)
                .where(ChatMessage.id == assistant_msg.id)
                .values(metadata_json=metadata)
            )

            await db.commit()
            logger.info(f"Message reported for session {session_id}")
        else:
            logger.info(f"Message already reported for session {session_id}")
