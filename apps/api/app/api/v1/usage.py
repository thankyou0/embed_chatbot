"""Usage tracking API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.exceptions import NotFoundError, ForbiddenError
from app.models.user import User, UserRole
from app.models.chatbot import Chatbot
from app.models.chat import ChatSession, ChatMessage, MessageRole
from app.models.subscription import Subscription
from app.models.knowledge import KnowledgeSource, CrawledPage, UploadedFile, QAPair
from app.schemas.billing import UsageOverviewResponse, ChatbotUsage
from app.core.logging import get_logger
from app.core.error_sanitizer import sanitize_error_message
from datetime import datetime, timezone

logger = get_logger(__name__)

router = APIRouter(prefix="/usage", tags=["usage"])


@router.get("/overview", response_model=UsageOverviewResponse)
async def get_usage_overview(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    chatbot_id: str = None
):
    """
    Get usage overview including global message count and per-chatbot breakdown
    
    Admins can view all usage information.
    Members can view usage only for chatbots they have analytics permission for.
    """
    from uuid import UUID
    from app.services.chatbot_service import ChatbotService
    
    # Non-admins must specify a chatbot_id and have analytics permission
    if current_user.role != UserRole.ADMIN:
        if not chatbot_id:
            raise ForbiddenError("Members must specify a chatbot_id to view usage information")
        
        # Verify user has analytics permission for this chatbot
        try:
            chatbot_uuid = UUID(chatbot_id)
            if not await ChatbotService.has_permission(db, chatbot_uuid, current_user, "can_view_analytics_billing"):
                raise ForbiddenError("Insufficient permissions to view usage for this chatbot")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid chatbot_id format")
    
    try:
        # Get subscription with global message count
        sub_stmt = select(Subscription).where(
            Subscription.tenant_id == current_user.tenant_id
        )
        sub_result = await db.execute(sub_stmt)
        subscription = sub_result.scalar_one()
        
        if not subscription:
            raise NotFoundError("Subscription not found")
        
        # Get chatbots based on user role and permissions
        if current_user.role == UserRole.ADMIN:
            # Admins see all chatbots
            chatbots_stmt = select(Chatbot).where(
                and_(
                    Chatbot.tenant_id == current_user.tenant_id,
                    Chatbot.deleted_at.is_(None)
                )
            )
            # If chatbot_id specified, filter to that chatbot
            if chatbot_id:
                chatbots_stmt = chatbots_stmt.where(Chatbot.id == UUID(chatbot_id))
        else:
            # Members only see the specific chatbot they requested
            chatbots_stmt = select(Chatbot).where(
                and_(
                    Chatbot.id == UUID(chatbot_id),
                    Chatbot.tenant_id == current_user.tenant_id,
                    Chatbot.deleted_at.is_(None)
                )
            )
        
        chatbots_result = await db.execute(chatbots_stmt)
        chatbots = chatbots_result.scalars().all()
        
        # Build per-chatbot usage
        per_chatbot_usage = []
        for chatbot in chatbots:
            # Count conversations for this chatbot
            conv_stmt = select(func.count(ChatSession.id)).where(
                and_(
                    ChatSession.chatbot_id == chatbot.id,
                    ChatSession.is_preview == False
                )
            )
            conv_result = await db.execute(conv_stmt)
            conversation_count = conv_result.scalar() or 0
            
            # Count knowledge pages (CrawledPage + QAPair)
            pages_stmt = select(func.count(CrawledPage.id)).where(
                CrawledPage.knowledge_source_id.in_(
                    select(KnowledgeSource.id).where(
                        KnowledgeSource.chatbot_id == chatbot.id
                    )
                ),
                CrawledPage.is_removed == False
            )
            pages_result = await db.execute(pages_stmt)
            pages_count = pages_result.scalar() or 0
            
            qa_stmt = select(func.count(QAPair.id)).where(
                QAPair.knowledge_source_id.in_(
                    select(KnowledgeSource.id).where(
                        KnowledgeSource.chatbot_id == chatbot.id
                    )
                )
            )
            qa_result = await db.execute(qa_stmt)
            qa_count = qa_result.scalar() or 0
            
            knowledge_pages_count = pages_count + qa_count
            
            # Calculate storage (sum of file sizes)
            storage_stmt = select(func.coalesce(func.sum(UploadedFile.file_size), 0)).where(
                UploadedFile.knowledge_source_id.in_(
                    select(KnowledgeSource.id).where(
                        KnowledgeSource.chatbot_id == chatbot.id
                    )
                )
            )
            storage_result = await db.execute(storage_stmt)
            storage_bytes = storage_result.scalar() or 0
            storage_mb = round(storage_bytes / (1024 * 1024), 2)
            
            per_chatbot_usage.append(
                ChatbotUsage(
                    chatbot_id=str(chatbot.id),
                    chatbot_name=chatbot.name,
                    message_count=chatbot.message_count,
                    conversation_count=conversation_count,
                    knowledge_pages_count=knowledge_pages_count,
                    storage_mb=storage_mb,
                    created_at=chatbot.created_at
                )
            )
        
        # Calculate total conversations and storage
        total_conv_stmt = select(func.count(ChatSession.id)).where(
            and_(
                Chatbot.tenant_id == current_user.tenant_id,
                ChatSession.is_preview == False,
                Chatbot.deleted_at.is_(None)
            )
        ).select_from(Chatbot).join(ChatSession)
        total_conv_result = await db.execute(total_conv_stmt)
        total_conversations = total_conv_result.scalar() or 0
        
        # Calculate account-wide totals for KB pages, files, and storage
        # Get all knowledge source IDs for this tenant's chatbots
        tenant_ks_ids = select(KnowledgeSource.id).where(
            KnowledgeSource.chatbot_id.in_(
                select(Chatbot.id).where(
                    and_(
                        Chatbot.tenant_id == current_user.tenant_id,
                        Chatbot.deleted_at.is_(None)
                    )
                )
            )
        )
        
        # Count total pages (CrawledPage + QAPair)
        total_pages_stmt = select(func.count(CrawledPage.id)).where(
            CrawledPage.knowledge_source_id.in_(tenant_ks_ids),
            CrawledPage.is_removed == False
        )
        total_pages_result = await db.execute(total_pages_stmt)
        total_pages = total_pages_result.scalar() or 0
        
        total_qa_stmt = select(func.count(QAPair.id)).where(
            QAPair.knowledge_source_id.in_(tenant_ks_ids)
        )
        total_qa_result = await db.execute(total_qa_stmt)
        total_qa = total_qa_result.scalar() or 0
        
        total_knowledge_pages = total_pages + total_qa
        
        # Count total files
        total_files_stmt = select(func.count(UploadedFile.id)).where(
            UploadedFile.knowledge_source_id.in_(tenant_ks_ids)
        )
        total_files_result = await db.execute(total_files_stmt)
        total_knowledge_files = total_files_result.scalar() or 0
        
        # Calculate total storage
        total_storage_stmt = select(func.coalesce(func.sum(UploadedFile.file_size), 0)).where(
            UploadedFile.knowledge_source_id.in_(tenant_ks_ids)
        )
        total_storage_result = await db.execute(total_storage_stmt)
        total_storage_bytes = total_storage_result.scalar() or 0
        total_storage_mb = round(total_storage_bytes / (1024 * 1024), 2)
        
        # Filter by chatbot if specified
        if chatbot_id:
            per_chatbot_usage = [usage for usage in per_chatbot_usage if usage.chatbot_id == chatbot_id]
        
        return UsageOverviewResponse(
            global_message_count=subscription.global_message_count,
            total_conversations=total_conversations,
            total_knowledge_pages=total_knowledge_pages,
            total_knowledge_files=total_knowledge_files,
            total_storage_mb=total_storage_mb,
            per_chatbot_usage=per_chatbot_usage,
            period_start=subscription.current_period_start,
            period_end=subscription.current_period_end
        )
    except Exception as e:
        logger.error(f"Error getting usage overview: {e}", exc_info=True)
        detail = sanitize_error_message(
            str(e),
            fallback="Unable to load usage data. Please try again."
        )
        raise HTTPException(status_code=400, detail=detail)


@router.get("/chatbot/{chatbot_id}", response_model=ChatbotUsage)
async def get_chatbot_usage(
    chatbot_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get usage for a specific chatbot
    """
    try:
        # Verify chatbot belongs to user's tenant
        chatbot_stmt = select(Chatbot).where(
            and_(
                Chatbot.id == chatbot_id,
                Chatbot.tenant_id == current_user.tenant_id
            )
        )
        chatbot_result = await db.execute(chatbot_stmt)
        chatbot = chatbot_result.scalar_one()
        
        if not chatbot:
            raise HTTPException(status_code=404, detail="Chatbot not found")
        
        # Count conversations for this chatbot
        conv_stmt = select(func.count(ChatSession.id)).where(
            and_(
                ChatSession.chatbot_id == chatbot.id,
                ChatSession.is_preview == False
            )
        )
        conv_result = await db.execute(conv_stmt)
        conversation_count = conv_result.scalar() or 0
        
        return ChatbotUsage(
            chatbot_id=str(chatbot.id),
            chatbot_name=chatbot.name,
            message_count=chatbot.message_count,
            conversation_count=conversation_count,
            created_at=chatbot.created_at
        )
    except Exception as e:
        logger.error(f"Error getting chatbot usage: {e}", exc_info=True)
        detail = sanitize_error_message(
            str(e),
            fallback="Unable to load chatbot usage. Please try again."
        )
        raise HTTPException(status_code=400, detail=detail)
