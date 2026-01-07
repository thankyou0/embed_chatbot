"""Analytics Service for chatbot metrics"""
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, func, and_, or_, cast, Float
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import JSONB

from app.models.chat import ChatSession, ChatMessage, MessageRole
from app.models.user import User
from app.schemas.analytics import (
    AnalyticsOverviewResponse,
    UnansweredQueriesResponse,
    UnansweredQuery,
    UnansweredQuerySample
)
from app.services.chatbot_service import ChatbotService
from app.core.logging import get_logger

logger = get_logger(__name__)


class AnalyticsService:
    
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
        period: str = "30d"
    ) -> AnalyticsOverviewResponse:
        """Get analytics overview with deflection and unanswered rates"""
        
        period_start = AnalyticsService._get_period_start(period)
        
        # Build base query for sessions
        query = select(ChatSession).where(
            ChatSession.started_at >= period_start
        )
        
        if chatbot_id:
            # Verify access to specific chatbot
            await ChatbotService.get_chatbot(db, tenant_id, chatbot_id, user)
            query = query.where(ChatSession.chatbot_id == chatbot_id)
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
                    period=period
                )
            query = query.where(ChatSession.chatbot_id.in_(chatbot_ids))
        
        # Get sessions
        sessions_result = await db.execute(query)
        sessions = sessions_result.scalars().all()
        total_sessions = len(sessions)
        
        if total_sessions == 0:
            return AnalyticsOverviewResponse(
                total_sessions=0,
                total_messages=0,
                avg_messages_per_session=0.0,
                deflection_rate=0.0,
                unanswered_rate=0.0,
                period=period
            )
        
        session_ids = [s.id for s in sessions]
        
        # Get all messages for these sessions
        messages_query = select(ChatMessage).where(
            ChatMessage.session_id.in_(session_ids)
        ).order_by(ChatMessage.created_at)
        
        messages_result = await db.execute(messages_query)
        all_messages = messages_result.scalars().all()
        total_messages = len(all_messages)
        
        # Calculate deflection rate
        # A session is "deflected" if all bot responses have was_answered=true
        deflected_sessions = 0
        for session_id in session_ids:
            session_messages = [m for m in all_messages if m.session_id == session_id]
            bot_messages = [m for m in session_messages if m.role == MessageRole.ASSISTANT]
            
            if not bot_messages:
                continue
            
            # Check if all bot messages were answered
            all_answered = all(
                m.metadata_json.get("was_answered", False) 
                for m in bot_messages
            )
            
            if all_answered:
                deflected_sessions += 1
        
        deflection_rate = (deflected_sessions / total_sessions * 100) if total_sessions > 0 else 0.0
        
        # Calculate unanswered rate
        # Count user messages where the bot response has was_answered=false
        user_messages = [m for m in all_messages if m.role == MessageRole.USER]
        unanswered_count = 0
        
        for user_msg in user_messages:
            # Find the next bot message after this user message
            bot_response = next(
                (m for m in all_messages 
                 if m.session_id == user_msg.session_id 
                 and m.role == MessageRole.ASSISTANT 
                 and m.created_at > user_msg.created_at),
                None
            )
            
            if bot_response and not bot_response.metadata_json.get("was_answered", False):
                unanswered_count += 1
        
        unanswered_rate = (unanswered_count / len(user_messages) * 100) if user_messages else 0.0
        
        # Calculate average messages per session
        avg_messages = total_messages / total_sessions if total_sessions > 0 else 0.0
        
        return AnalyticsOverviewResponse(
            total_sessions=total_sessions,
            total_messages=total_messages,
            avg_messages_per_session=round(avg_messages, 1),
            deflection_rate=round(deflection_rate, 1),
            unanswered_rate=round(unanswered_rate, 1),
            period=period
        )
    
    @staticmethod
    async def get_unanswered_queries(
        db: AsyncSession,
        tenant_id: int,
        chatbot_id: UUID,
        user: User,
        period: str = "30d",
        limit: int = 20
    ) -> UnansweredQueriesResponse:
        """Get unanswered queries for a chatbot"""
        
        # Verify access
        await ChatbotService.get_chatbot(db, tenant_id, chatbot_id, user)
        
        period_start = AnalyticsService._get_period_start(period)
        
        # Get all sessions for this chatbot in the period
        sessions_query = select(ChatSession).where(
            and_(
                ChatSession.chatbot_id == chatbot_id,
                ChatSession.started_at >= period_start
            )
        )
        
        sessions_result = await db.execute(sessions_query)
        sessions = sessions_result.scalars().all()
        session_ids = [s.id for s in sessions]
        
        if not session_ids:
            return UnansweredQueriesResponse(queries=[], total_unanswered=0)
        
        # Get all messages
        messages_query = select(ChatMessage).where(
            ChatMessage.session_id.in_(session_ids)
        ).order_by(ChatMessage.created_at)
        
        messages_result = await db.execute(messages_query)
        all_messages = messages_result.scalars().all()
        
        # Find unanswered user queries
        unanswered_messages = []
        user_messages = [m for m in all_messages if m.role == MessageRole.USER]
        
        for user_msg in user_messages:
            # Find the next bot message
            bot_response = next(
                (m for m in all_messages 
                 if m.session_id == user_msg.session_id 
                 and m.role == MessageRole.ASSISTANT 
                 and m.created_at > user_msg.created_at),
                None
            )
            
            if bot_response and not bot_response.metadata_json.get("was_answered", False):
                confidence = bot_response.metadata_json.get("retrieval_confidence", 0.0)
                unanswered_messages.append({
                    "message": user_msg,
                    "confidence": confidence
                })
        
        # Group by exact query text (simple grouping, no clustering yet)
        query_groups = {}
        for item in unanswered_messages:
            msg = item["message"]
            query_text = msg.content.strip().lower()
            
            if query_text not in query_groups:
                query_groups[query_text] = {
                    "original_query": msg.content,
                    "messages": [],
                    "confidences": []
                }
            
            query_groups[query_text]["messages"].append(msg)
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
                    id=m.id,
                    content=m.content,
                    created_at=m.created_at
                )
                for m in messages[:3]
            ]
            
            queries.append(UnansweredQuery(
                query=data["original_query"],
                count=len(messages),
                avg_confidence=round(avg_confidence, 3),
                first_asked=min(m.created_at for m in messages),
                last_asked=max(m.created_at for m in messages),
                sample_messages=samples
            ))
        
        # Sort by count descending
        queries.sort(key=lambda q: q.count, reverse=True)
        
        return UnansweredQueriesResponse(
            queries=queries[:limit],
            total_unanswered=len(unanswered_messages)
        )

