from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone

from app.models.user import User, UserRole
from app.models.chatbot import Chatbot, ChatbotStatus, ChatbotActivity
from app.models.chatbot_permission import ChatbotPermission, PermissionLevel
from app.models.chatbot_appearance import ChatbotAppearance, WidgetPosition
from app.models.knowledge import (
    KnowledgeSource, KnowledgeSourceType, KnowledgeSourceStatus, 
    CrawledPage, UploadedFile, Embedding, QAPair,
    CrawlSchedule, CrawlHistory, ScheduleType, CrawlStatus
)
from app.models.chat import ChatSession, ChatMessage, MessageRole
from app.core.logging import get_logger
from app.core.exceptions import (
    BadRequestError,
    NotFoundError,
    ForbiddenError,
)
from app.schemas.chatbot import (
    ChatbotCreate,
    ChatbotUpdate,
    ChatbotResponse,
    ChatbotWithPermission,
    PermissionAssign,
    PermissionResponse,
    PermissionListResponse,
    ChatbotStatsResponse,
    RecentActivity,
    AnalyticsOverviewResponse,
)
from app.schemas.appearance import (
    ChatbotAppearanceResponse,
    ChatbotAppearanceUpdate,
    WidgetConfigResponse,
    AvatarUploadResponse,
)
from app.schemas.knowledge import (
    KnowledgeSourceCreate,
    KnowledgeSourceResponse,
    CrawlStatusResponse,
    FileUploadResponse,
    UploadedFileResponse,
    QAPairCreate,
    QAPairBulkCreate,
    QAPairResponse,
    CrawlScheduleCreate,
    CrawlScheduleUpdate,
    CrawlScheduleResponse,
    CrawlHistoryResponse,
    TriggerCrawlResponse,
)
from app.services.crawler_service import CrawlerService
from app.services.file_service import FileService
from app.services.embedding_service import EmbeddingService
from app.services.scheduler_service import SchedulerService
from app.core.database import AsyncSessionLocal
from fastapi import BackgroundTasks, UploadFile
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload
import os
import io
import aiofiles
from pathlib import Path
import pandas as pd
import io

logger = get_logger(__name__)


class ChatbotService:
    
    # ============== Chatbot CRUD ==============
    
    @staticmethod
    async def create_chatbot(
        db: AsyncSession,
        tenant_id: int,
        user: User,
        request: ChatbotCreate
    ) -> ChatbotWithPermission:
        """Create a new chatbot"""
        
        # #region agent log
        # with open(r'e:\e_com_Chatbot\.cursor\debug.log', 'a') as f: f.write('{"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"chatbot_service.py:42","message":"Before creating chatbot","data":{"status_enum_name":"' + str(ChatbotStatus.DRAFT.name) + '","status_enum_value":"' + str(ChatbotStatus.DRAFT.value) + '","status_repr":"' + repr(ChatbotStatus.DRAFT) + '"},"timestamp":' + str(__import__('time').time() * 1000) + '}\n')
        # #endregion
        
        # Create chatbot
        chatbot = Chatbot(
            tenant_id=tenant_id,
            name=request.name,
            welcome_message=request.welcome_message,
            created_by=user.id,
            status=ChatbotStatus.DRAFT,
        )
        
        # #region agent log
        # with open(r'e:\e_com_Chatbot\.cursor\debug.log', 'a') as f: f.write('{"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"chatbot_service.py:50","message":"After creating chatbot object","data":{"chatbot_status":"' + str(chatbot.status) + '","chatbot_status_type":"' + str(type(chatbot.status).__name__) + '","chatbot_status_value":"' + str(chatbot.status.value if hasattr(chatbot.status, "value") else "N/A") + '"},"timestamp":' + str(__import__('time').time() * 1000) + '}\n')
        # #endregion
        
        db.add(chatbot)
        
        # #region agent log
        # with open(r'e:\e_com_Chatbot\.cursor\debug.log', 'a') as f: f.write('{"sessionId":"debug-session","runId":"run1","hypothesisId":"B","location":"chatbot_service.py:54","message":"Before flush - checking status attribute","data":{"has_status":"' + str(hasattr(chatbot, "status")) + '","status_value":"' + str(getattr(chatbot, "status", "NOT_SET")) + '"},"timestamp":' + str(__import__('time').time() * 1000) + '}\n')
        # #endregion
        
        await db.flush()
        
        # Auto-assign OWNER permission to creator
        permission = ChatbotPermission(
            user_id=user.id,
            chatbot_id=chatbot.id,
            permission_level=PermissionLevel.OWNER,
            can_manage_knowledge=True,
            can_manage_appearance=True,
            can_resolve_queries=True,
            can_view_analytics=True,
            granted_by=user.id,
        )
        db.add(permission)

        # Log creation activity
        activity = ChatbotActivity(
            chatbot_id=chatbot.id,
            user_id=user.id,
            activity_type="chatbot_created",
            description=f"Chatbot created by {user.name or user.email}"
        )
        db.add(activity)
        
        await db.commit()
        await db.refresh(chatbot)
        
        logger.success(f"Chatbot created: {chatbot.name} by user {user.email}")
        
        return ChatbotWithPermission(
            **ChatbotResponse.model_validate(chatbot).model_dump(),
            permission_level=PermissionLevel.OWNER
        )
    
    @staticmethod
    async def list_chatbots(
        db: AsyncSession,
        tenant_id: int,
        user: User,
    ) -> List[ChatbotWithPermission]:
        """List chatbots user has access to"""
        
        # Admin sees all chatbots in tenant
        if user.role == UserRole.ADMIN:
            result = await db.execute(
                select(Chatbot)
                .where(
                    Chatbot.tenant_id == tenant_id,
                    Chatbot.deleted_at.is_(None),
                )
                .order_by(Chatbot.created_at.desc())
            )
            chatbots = result.scalars().all()
            
            # Get permissions for admin
            chatbot_list = []
            for chatbot in chatbots:
                # Check if admin has permission, if not they're implicit ADMIN
                perm_result = await db.execute(
                    select(ChatbotPermission)
                    .where(
                        ChatbotPermission.chatbot_id == chatbot.id,
                        ChatbotPermission.user_id == user.id
                    )
                )
                permission = perm_result.scalar_one_or_none()
                
                if permission:
                    perm_level = permission.permission_level
                    flags = {
                        "can_manage_knowledge": permission.can_manage_knowledge,
                        "can_manage_appearance": permission.can_manage_appearance,
                        "can_resolve_queries": permission.can_resolve_queries,
                        "can_view_analytics": permission.can_view_analytics
                    }
                else:
                    perm_level = PermissionLevel.ADMIN
                    flags = {
                        "can_manage_knowledge": True,
                        "can_manage_appearance": True,
                        "can_resolve_queries": True,
                        "can_view_analytics": True
                    }
                
                chatbot_list.append(ChatbotWithPermission(
                    **ChatbotResponse.model_validate(chatbot).model_dump(),
                    permission_level=perm_level,
                    **flags
                ))
            
            return chatbot_list
        
        # Regular users only see chatbots they have explicit permission for
        result = await db.execute(
            select(Chatbot, ChatbotPermission)
            .join(ChatbotPermission, Chatbot.id == ChatbotPermission.chatbot_id)
            .where(
                Chatbot.tenant_id == tenant_id,
                Chatbot.deleted_at.is_(None),
                ChatbotPermission.user_id == user.id,
            )
            .order_by(Chatbot.created_at.desc())
        )
        rows = result.all()
        
        return [
            ChatbotWithPermission(
                **ChatbotResponse.model_validate(chatbot).model_dump(),
                permission_level=permission.permission_level,
                can_manage_knowledge=permission.can_manage_knowledge,
                can_manage_appearance=permission.can_manage_appearance,
                can_resolve_queries=permission.can_resolve_queries,
                can_view_analytics=permission.can_view_analytics
            )
            for chatbot, permission in rows
        ]
    
    @staticmethod
    async def get_chatbot(
        db: AsyncSession,
        tenant_id: int,
        chatbot_id: UUID,
        user: User,
    ) -> ChatbotWithPermission:
        """Get a specific chatbot"""
        
        result = await db.execute(
            select(Chatbot)
            .where(
                Chatbot.id == chatbot_id,
                Chatbot.tenant_id == tenant_id,
                Chatbot.deleted_at.is_(None),
            )
        )
        chatbot = result.scalar_one_or_none()
        
        if not chatbot:
            raise NotFoundError("Chatbot not found")
        
        # Check permission
        permission = await ChatbotService._get_permission_record(db, chatbot_id, user)
        if not permission and user.role != UserRole.ADMIN:
            raise ForbiddenError("You don't have access to this chatbot")
        
        if user.role == UserRole.ADMIN:
            perm_level = permission.permission_level if permission else PermissionLevel.ADMIN
            flags = {
                "can_manage_knowledge": permission.can_manage_knowledge if permission else True,
                "can_manage_appearance": permission.can_manage_appearance if permission else True,
                "can_resolve_queries": permission.can_resolve_queries if permission else True,
                "can_view_analytics": permission.can_view_analytics if permission else True,
            }
        else:
            perm_level = permission.permission_level
            flags = {
                "can_manage_knowledge": permission.can_manage_knowledge,
                "can_manage_appearance": permission.can_manage_appearance,
                "can_resolve_queries": permission.can_resolve_queries,
                "can_view_analytics": permission.can_view_analytics,
            }

        return ChatbotWithPermission(
            **ChatbotResponse.model_validate(chatbot).model_dump(),
            permission_level=perm_level,
            **flags
        )
    
    @staticmethod
    async def update_chatbot(
        db: AsyncSession,
        tenant_id: int,
        chatbot_id: UUID,
        user: User,
        request: ChatbotUpdate
    ) -> ChatbotWithPermission:
        """Update chatbot (requires EDITOR+ permission)"""
        
        result = await db.execute(
            select(Chatbot)
            .where(
                Chatbot.id == chatbot_id,
                Chatbot.tenant_id == tenant_id,
                Chatbot.deleted_at.is_(None),
            )
        )
        chatbot = result.scalar_one_or_none()
        
        if not chatbot:
            raise NotFoundError("Chatbot not found")
        
        # Check permission (need at least EDITOR or specific flag)
        if not await ChatbotService.has_permission(db, chatbot_id, user, "can_manage_knowledge"): # Using knowledge flag as proxy for general settings
             # We might want a dedicated can_manage_settings flag, but for now EDITOR is knowledge/qa
             pass
        
        # More precise check:
        permission_level = await ChatbotService._get_permission_level(db, chatbot_id, user)
        if not permission_level or permission_level == PermissionLevel.VIEWER:
            raise ForbiddenError("You need EDITOR or higher permission to update this chatbot")
        
        # Update fields
        if request.name is not None:
            chatbot.name = request.name
        if request.status is not None:
            old_status = chatbot.status
            chatbot.status = request.status
            if old_status != request.status:
                activity = ChatbotActivity(
                    chatbot_id=chatbot_id,
                    user_id=user.id,
                    activity_type="status_change",
                    description=f"Status changed from {old_status} to {request.status} by {user.name or user.email}"
                )
                db.add(activity)
        
        if request.welcome_message is not None:
            chatbot.welcome_message = request.welcome_message
        
        await db.commit()
        await db.refresh(chatbot)
        
        logger.success(f"Chatbot updated: {chatbot.name}")
        
        return ChatbotWithPermission(
            **ChatbotResponse.model_validate(chatbot).model_dump(),
            permission_level=permission_level
        )
    
    @staticmethod
    async def delete_chatbot(
        db: AsyncSession,
        tenant_id: int,
        chatbot_id: UUID,
        user: User,
    ) -> None:
        """Delete chatbot (requires OWNER or tenant ADMIN)"""
        
        result = await db.execute(
            select(Chatbot)
            .where(
                Chatbot.id == chatbot_id,
                Chatbot.tenant_id == tenant_id,
                Chatbot.deleted_at.is_(None),
            )
        )
        chatbot = result.scalar_one_or_none()
        
        if not chatbot:
            raise NotFoundError("Chatbot not found")
        
        # Check permission (need OWNER or be tenant ADMIN)
        permission_level = await ChatbotService._get_permission_level(db, chatbot_id, user)
        if permission_level != PermissionLevel.OWNER and user.role != UserRole.ADMIN:
            raise ForbiddenError("Only OWNER or tenant ADMIN can delete this chatbot")
        
        chatbot.deleted_at = datetime.now(timezone.utc)
        chatbot.status = ChatbotStatus.PAUSED
        await db.commit()
        
        logger.success(f"Chatbot deleted: {chatbot.name}")
    
    # ============== Permission Management ==============
    
    @staticmethod
    async def assign_permission(
        db: AsyncSession,
        tenant_id: int,
        chatbot_id: UUID,
        user: User,
        request: PermissionAssign
    ) -> PermissionResponse:
        """Assign permission to a user for a chatbot (requires OWNER/ADMIN permission)"""
        
        # Verify chatbot exists and belongs to tenant
        result = await db.execute(
            select(Chatbot)
            .where(
                Chatbot.id == chatbot_id,
                Chatbot.tenant_id == tenant_id,
                Chatbot.deleted_at.is_(None),
            )
        )
        chatbot = result.scalar_one_or_none()
        
        if not chatbot:
            raise NotFoundError("Chatbot not found")
        
        # Check if assigner has OWNER/ADMIN permission or is tenant ADMIN
        assigner_level = await ChatbotService._get_permission_level(db, chatbot_id, user)
        can_assign = (
            assigner_level in [PermissionLevel.OWNER, PermissionLevel.ADMIN]
            or user.role == UserRole.ADMIN
        )
        
        if not can_assign:
            raise ForbiddenError("You need OWNER or ADMIN permission to assign permissions")
        
        # Default flags based on level if not provided (custom is handled separately)
        if request.permission_level == PermissionLevel.ADMIN:
            request.can_manage_knowledge = True
            request.can_manage_appearance = True
            request.can_resolve_queries = True
            request.can_view_analytics = True
        elif request.permission_level == PermissionLevel.EDITOR:
            request.can_manage_knowledge = True
            request.can_resolve_queries = True
            request.can_view_analytics = True
        elif request.permission_level == PermissionLevel.VIEWER:
            request.can_manage_knowledge = False
            request.can_manage_appearance = False
            request.can_resolve_queries = False
            request.can_view_analytics = True

        # Verify target user exists and belongs to same tenant
        result = await db.execute(
            select(User)
            .where(User.id == request.user_id, User.tenant_id == tenant_id)
        )
        target_user = result.scalar_one_or_none()
        
        if not target_user:
            raise NotFoundError("User not found in this tenant")
        
        # Check if permission already exists
        result = await db.execute(
            select(ChatbotPermission)
            .where(
                ChatbotPermission.chatbot_id == chatbot_id,
                ChatbotPermission.user_id == request.user_id
            )
        )
        existing_permission = result.scalar_one_or_none()
        
        if existing_permission:
            # Update existing permission
            existing_permission.permission_level = request.permission_level
            existing_permission.can_manage_knowledge = request.can_manage_knowledge
            existing_permission.can_manage_appearance = request.can_manage_appearance
            existing_permission.can_resolve_queries = request.can_resolve_queries
            existing_permission.can_view_analytics = request.can_view_analytics
            existing_permission.granted_by = user.id
            await db.commit()
            await db.refresh(existing_permission)
            
            logger.success(f"Permission updated for user {target_user.email} on chatbot {chatbot.name}")
            
            return PermissionResponse(
                id=existing_permission.id,
                user_id=existing_permission.user_id,
                chatbot_id=existing_permission.chatbot_id,
                permission_level=existing_permission.permission_level,
                can_manage_knowledge=existing_permission.can_manage_knowledge,
                can_manage_appearance=existing_permission.can_manage_appearance,
                can_resolve_queries=existing_permission.can_resolve_queries,
                can_view_analytics=existing_permission.can_view_analytics,
                granted_by=existing_permission.granted_by,
                created_at=existing_permission.created_at,
                user_email=target_user.email,
                user_name=target_user.name,
            )
        
        # Create new permission
        permission = ChatbotPermission(
            user_id=request.user_id,
            chatbot_id=chatbot_id,
            permission_level=request.permission_level,
            can_manage_knowledge=request.can_manage_knowledge,
            can_manage_appearance=request.can_manage_appearance,
            can_resolve_queries=request.can_resolve_queries,
            can_view_analytics=request.can_view_analytics,
            granted_by=user.id,
        )
        db.add(permission)
        await db.commit()
        await db.refresh(permission)
        
        logger.success(f"Permission granted to user {target_user.email} on chatbot {chatbot.name}")
        
        return PermissionResponse(
            id=permission.id,
            user_id=permission.user_id,
            chatbot_id=permission.chatbot_id,
            permission_level=permission.permission_level,
            can_manage_knowledge=permission.can_manage_knowledge,
            can_manage_appearance=permission.can_manage_appearance,
            can_resolve_queries=permission.can_resolve_queries,
            can_view_analytics=permission.can_view_analytics,
            granted_by=permission.granted_by,
            created_at=permission.created_at,
            user_email=target_user.email,
            user_name=target_user.name,
        )
    
    @staticmethod
    async def list_permissions(
        db: AsyncSession,
        tenant_id: int,
        chatbot_id: UUID,
        user: User,
    ) -> List[PermissionResponse]:
        """List all permissions for a chatbot"""
        
        # Verify chatbot exists
        result = await db.execute(
            select(Chatbot)
            .where(
                Chatbot.id == chatbot_id,
                Chatbot.tenant_id == tenant_id,
                Chatbot.deleted_at.is_(None),
            )
        )
        chatbot = result.scalar_one_or_none()
        
        if not chatbot:
            raise NotFoundError("Chatbot not found")
        
        # Check if user has access to view permissions
        permission_level = await ChatbotService._get_user_permission(db, chatbot_id, user)
        if not permission_level:
            raise ForbiddenError("You don't have access to this chatbot")
        
        # Get all permissions with user info
        result = await db.execute(
            select(ChatbotPermission, User)
            .join(User, ChatbotPermission.user_id == User.id)
            .where(ChatbotPermission.chatbot_id == chatbot_id)
        )
        rows = result.all()
        
        return [
            PermissionResponse(
                id=perm.id,
                user_id=perm.user_id,
                chatbot_id=perm.chatbot_id,
                permission_level=perm.permission_level,
                can_manage_knowledge=perm.can_manage_knowledge,
                can_manage_appearance=perm.can_manage_appearance,
                can_resolve_queries=perm.can_resolve_queries,
                can_view_analytics=perm.can_view_analytics,
                granted_by=perm.granted_by,
                created_at=perm.created_at,
                user_email=target_user.email,
                user_name=target_user.name,
            )
            for perm, target_user in rows
        ]
    
    @staticmethod
    async def remove_permission(
        db: AsyncSession,
        tenant_id: int,
        chatbot_id: UUID,
        target_user_id: int,
        user: User,
    ) -> None:
        """Remove user's permission from chatbot"""
        
        # Verify chatbot exists
        result = await db.execute(
            select(Chatbot)
            .where(
                Chatbot.id == chatbot_id,
                Chatbot.tenant_id == tenant_id,
                Chatbot.deleted_at.is_(None),
            )
        )
        chatbot = result.scalar_one_or_none()
        
        if not chatbot:
            raise NotFoundError("Chatbot not found")
        
        # Check if remover has OWNER/ADMIN permission or is tenant ADMIN
        remover_permission = await ChatbotService._get_permission_level(db, chatbot_id, user)
        can_remove = (
            remover_permission in [PermissionLevel.OWNER, PermissionLevel.ADMIN]
            or user.role == UserRole.ADMIN
        )
        
        if not can_remove:
            raise ForbiddenError("You need OWNER or ADMIN permission to remove permissions")
        
        # Find the permission
        result = await db.execute(
            select(ChatbotPermission)
            .where(
                ChatbotPermission.chatbot_id == chatbot_id,
                ChatbotPermission.user_id == target_user_id
            )
        )
        permission = result.scalar_one_or_none()
        
        if not permission:
            raise NotFoundError("Permission not found")
        
        # Cannot remove OWNER's permission
        if permission.permission_level == PermissionLevel.OWNER:
            raise BadRequestError("Cannot remove OWNER permission. Transfer ownership first.")
        
        await db.delete(permission)
        await db.commit()
        
        logger.success(f"Permission removed for user {target_user_id} on chatbot {chatbot.name}")
    
    # ============== Helper Methods ==============
    
    @staticmethod
    async def has_permission(
        db: AsyncSession,
        chatbot_id: UUID,
        user: User,
        required_flag: str = None
    ) -> bool:
        """Check if user has specific granular permission"""
        
        # Tenant ADMIN has implicit full access to all chatbots
        if user.role == UserRole.ADMIN:
            return True
        
        permission = await ChatbotService._get_permission_record(db, chatbot_id, user)
        if not permission:
            return False
            
        # OWNER has all permissions
        if permission.permission_level == PermissionLevel.OWNER:
            return True
            
        if required_flag:
            return getattr(permission, required_flag, False)
            
        return True

    @staticmethod
    async def _get_permission_record(
        db: AsyncSession,
        chatbot_id: UUID,
        user: User,
    ) -> Optional[ChatbotPermission]:
        """Get user's permission record for a chatbot"""
        result = await db.execute(
            select(ChatbotPermission)
            .where(
                ChatbotPermission.chatbot_id == chatbot_id,
                ChatbotPermission.user_id == user.id
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def _get_permission_level(
        db: AsyncSession,
        chatbot_id: UUID,
        user: User,
    ) -> Optional[PermissionLevel]:
        """Get user's permission level for a chatbot"""
        permission = await ChatbotService._get_permission_record(db, chatbot_id, user)
        if permission:
            return permission.permission_level
        
        if user.role == UserRole.ADMIN:
            return PermissionLevel.ADMIN
            
        return None

    @staticmethod
    async def _get_user_permission(
        db: AsyncSession,
        chatbot_id: UUID,
        user: User,
    ) -> Optional[PermissionLevel]:
        """Deprecated: Use _get_permission_level instead"""
        return await ChatbotService._get_permission_level(db, chatbot_id, user)
    
    # ============== Appearance Management ==============
    
    @staticmethod
    async def get_appearance(
        db: AsyncSession,
        tenant_id: int,
        chatbot_id: UUID,
        user: User,
    ) -> ChatbotAppearanceResponse:
        """Get chatbot appearance settings (create default if doesn't exist)"""
        
        # Verify chatbot exists and user has access
        result = await db.execute(
            select(Chatbot)
            .where(Chatbot.id == chatbot_id, Chatbot.tenant_id == tenant_id)
        )
        chatbot = result.scalar_one_or_none()
        
        if not chatbot:
            raise NotFoundError("Chatbot not found")
        
        # Check permission
        permission_level = await ChatbotService._get_user_permission(db, chatbot_id, user)
        if not permission_level:
            raise ForbiddenError("You don't have access to this chatbot")
        
        # Get or create appearance
        result = await db.execute(
            select(ChatbotAppearance)
            .where(ChatbotAppearance.chatbot_id == chatbot_id)
        )
        appearance = result.scalar_one_or_none()
        
        if not appearance:
            # Create default appearance
            appearance = ChatbotAppearance(chatbot_id=chatbot_id)
            db.add(appearance)
            await db.commit()
            await db.refresh(appearance)
            
            logger.info(f"Created default appearance for chatbot {chatbot_id}")
        
        return ChatbotAppearanceResponse.model_validate(appearance)
    
    @staticmethod
    async def upload_avatar(
        db: AsyncSession,
        tenant_id: int,
        chatbot_id: UUID,
        user: User,
        file: UploadFile,
    ) -> AvatarUploadResponse:
        """Upload a custom avatar image for the chatbot appearance"""
        # Permission check: require at least can_manage_appearance
        if not await ChatbotService.has_permission(db, chatbot_id, user, "can_manage_appearance"):
            raise ForbiddenError("You need permission to manage appearance to upload an avatar")

        # Validate image mime type
        allowed_types = {"image/png", "image/jpeg", "image/webp", "image/gif"}
        if file.content_type not in allowed_types:
            raise BadRequestError(
                f"Unsupported image type: {file.content_type}. Allowed: {', '.join(allowed_types)}"
            )

        # Read content and save to disk
        content = await file.read()
        ext = Path(file.filename).suffix.lower()
        if ext not in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
            ext = ".png"

        tenant_dir = os.path.join("uploads", str(tenant_id))
        chatbot_dir = os.path.join(tenant_dir, str(chatbot_id))
        os.makedirs(chatbot_dir, exist_ok=True)
        avatar_filename = f"avatar{ext}"
        avatar_path = os.path.join(chatbot_dir, avatar_filename)

        async with aiofiles.open(avatar_path, "wb") as out_file:
            await out_file.write(content)

        avatar_url = f"/uploads/{tenant_id}/{chatbot_id}/{avatar_filename}"

        # Update or create appearance with avatar_url
        result = await db.execute(
            select(ChatbotAppearance).where(ChatbotAppearance.chatbot_id == chatbot_id)
        )
        appearance = result.scalar_one_or_none()
        if not appearance:
            appearance = ChatbotAppearance(chatbot_id=chatbot_id)
            db.add(appearance)
            await db.flush()

        appearance.avatar_url = avatar_url
        db.add(appearance)
        await db.commit()

        return AvatarUploadResponse(chatbot_id=chatbot_id, avatar_url=avatar_url)
    @staticmethod
    async def update_appearance(
        db: AsyncSession,
        tenant_id: int,
        chatbot_id: UUID,
        user: User,
        request: ChatbotAppearanceUpdate
    ) -> ChatbotAppearanceResponse:
        """Update chatbot appearance settings (requires can_manage_appearance permission)"""
        
        # Verify chatbot exists
        result = await db.execute(
            select(Chatbot)
            .where(Chatbot.id == chatbot_id, Chatbot.tenant_id == tenant_id)
        )
        chatbot = result.scalar_one_or_none()
        
        if not chatbot:
            raise NotFoundError("Chatbot not found")
        
        # Check permission
        if not await ChatbotService.has_permission(db, chatbot_id, user, "can_manage_appearance"):
            raise ForbiddenError("You need permission to manage appearance to update appearance settings")
        
        # Get or create appearance
        result = await db.execute(
            select(ChatbotAppearance)
            .where(ChatbotAppearance.chatbot_id == chatbot_id)
        )
        appearance = result.scalar_one_or_none()
        
        if not appearance:
            # Create with provided values
            appearance = ChatbotAppearance(chatbot_id=chatbot_id)
            db.add(appearance)
        
        # Update fields
        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(appearance, field, value)
        
        # Update timestamp
        appearance.updated_at = datetime.now(timezone.utc)
        
        await db.commit()
        await db.refresh(appearance)
        
        logger.success(f"Appearance updated for chatbot {chatbot_id}")
        
        return ChatbotAppearanceResponse.model_validate(appearance)
    
    @staticmethod
    async def get_widget_config(
        db: AsyncSession,
        chatbot_id: UUID,
    ) -> WidgetConfigResponse:
        """Get widget configuration (public, no auth required)"""
        
        # Verify chatbot exists (no tenant check needed for public endpoint)
        result = await db.execute(
            select(Chatbot)
            .where(Chatbot.id == chatbot_id)
        )
        chatbot = result.scalar_one_or_none()
        
        if not chatbot:
            raise NotFoundError("Chatbot not found")
        
        # Get or create appearance
        result = await db.execute(
            select(ChatbotAppearance)
            .where(ChatbotAppearance.chatbot_id == chatbot_id)
        )
        appearance = result.scalar_one_or_none()
        
        if not appearance:
            # Create default appearance
            appearance = ChatbotAppearance(chatbot_id=chatbot_id)
            db.add(appearance)
            await db.commit()
            await db.refresh(appearance)
            
            logger.info(f"Created default appearance for chatbot {chatbot_id}")
        
        # Convert to widget config response (position as string)
        return WidgetConfigResponse(
            display_name=chatbot.name,
            primary_color=appearance.primary_color,
            header_text=appearance.header_text,
            avatar_url=appearance.avatar_url,
            position=appearance.position.value if isinstance(appearance.position, WidgetPosition) else str(appearance.position),
            offset_x=appearance.offset_x,
            offset_y=appearance.offset_y,
            welcome_message=appearance.welcome_message,
            initial_suggestions=appearance.initial_suggestions or [],
            show_branding=appearance.show_branding,
        )

    # ============== Knowledge Base Management ==============

    @staticmethod
    async def create_crawl_source(
        db: AsyncSession,
        tenant_id: int,
        chatbot_id: UUID,
        user: User,
        request: KnowledgeSourceCreate,
        background_tasks: BackgroundTasks
    ) -> KnowledgeSourceResponse:
        """Create a new crawl-based knowledge source and start crawling"""
        
        # Verify chatbot access and check permissions
        if not await ChatbotService.has_permission(db, chatbot_id, user, "can_manage_knowledge"):
            raise ForbiddenError("Insufficient permissions to add knowledge source")

        # Check if this URL is already a knowledge source for this chatbot
        stmt = select(KnowledgeSource).where(
            KnowledgeSource.chatbot_id == chatbot_id,
            KnowledgeSource.source_type == KnowledgeSourceType.CRAWLED_URL,
            KnowledgeSource.source_url == request.base_url
        )
        existing_ks = (await db.execute(stmt)).scalar_one_or_none()
        
        if existing_ks:
            # If already exists, just trigger a re-crawl
            background_tasks.add_task(
                CrawlerService.start_crawl,
                knowledge_source_id=existing_ks.id,
                base_url=request.base_url,
                max_pages=request.max_pages,
                is_recrawl=True
            )
            return KnowledgeSourceResponse.model_validate(existing_ks)

        # Create knowledge source
        ks = KnowledgeSource(
            chatbot_id=chatbot_id,
            source_type=KnowledgeSourceType.CRAWLED_URL,
            source_url=request.base_url,
            status=KnowledgeSourceStatus.PENDING,
            pages_found=0
        )
        db.add(ks)

        # Log activity
        activity = ChatbotActivity(
            chatbot_id=chatbot_id,
            user_id=user.id,
            activity_type="knowledge_source",
            description=f"Added website knowledge source: {request.base_url} by {user.name or user.email}"
        )
        db.add(activity)

        await db.commit()
        
        # Fetch with loaded relationships to avoid MissingGreenlet during validation
        stmt = select(KnowledgeSource).options(
            selectinload(KnowledgeSource.files),
            selectinload(KnowledgeSource.qa_pairs),
            selectinload(KnowledgeSource.pages)
        ).where(KnowledgeSource.id == ks.id)
        ks = (await db.execute(stmt)).scalar_one()

        # Start background crawl
        background_tasks.add_task(
            CrawlerService.start_crawl,
            knowledge_source_id=ks.id,
            base_url=request.base_url,
            max_pages=request.max_pages
        )

        return KnowledgeSourceResponse.model_validate(ks)

    @staticmethod
    async def list_knowledge_sources(
        db: AsyncSession,
        tenant_id: int,
        chatbot_id: UUID,
        user: User
    ) -> List[KnowledgeSourceResponse]:
        """List all knowledge sources for a chatbot"""
        
        # Verify chatbot access
        await ChatbotService.get_chatbot(db, tenant_id, chatbot_id, user)
        
        stmt = select(KnowledgeSource).options(
            selectinload(KnowledgeSource.files),
            selectinload(KnowledgeSource.qa_pairs),
            selectinload(KnowledgeSource.pages)
        ).where(KnowledgeSource.chatbot_id == chatbot_id).order_by(KnowledgeSource.created_at.desc())
        result = await db.execute(stmt)
        sources = result.scalars().all()
        
        return [KnowledgeSourceResponse.model_validate(s) for s in sources]

    @staticmethod
    async def get_knowledge_source_status(
        db: AsyncSession,
        knowledge_source_id: UUID,
        user: User
    ) -> CrawlStatusResponse:
        """Get the status of a specific knowledge source"""
        
        # Find the source and verify user has access to the chatbot it belongs to
        stmt = select(KnowledgeSource).where(KnowledgeSource.id == knowledge_source_id)
        result = await db.execute(stmt)
        ks = result.scalar_one_or_none()
        
        if not ks:
            raise NotFoundError("Knowledge source not found")
            
        # Verify access to the parent chatbot
        if user.role != UserRole.ADMIN:
            permission_level = await ChatbotService._get_user_permission(db, ks.chatbot_id, user)
            if not permission_level:
                raise ForbiddenError("Access to this knowledge source is denied")

        return CrawlStatusResponse.model_validate(ks)

    @staticmethod
    async def upload_file(
        db: AsyncSession,
        tenant_id: int,
        chatbot_id: UUID,
        user: User,
        file: UploadFile,
        background_tasks: BackgroundTasks
    ) -> FileUploadResponse:
        """Upload a file, extract text, and start embedding"""
        
        # 1. Verify chatbot access and permissions (can_manage_knowledge)
        if not await ChatbotService.has_permission(db, chatbot_id, user, "can_manage_knowledge"):
            raise ForbiddenError("Insufficient permissions to upload files")

        # 2. Validate file type
        allowed_extensions = {'.pdf', '.docx', '.txt', '.md'}
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in allowed_extensions:
            raise BadRequestError(f"Unsupported file type: {ext}. Allowed: {', '.join(allowed_extensions)}")

        # 3. Save file locally
        upload_dir = os.path.join("uploads", str(tenant_id), str(chatbot_id))
        content = await file.read()
        file_path = await FileService.save_file(content, upload_dir, file.filename)

        # 4. Create KnowledgeSource
        ks = KnowledgeSource(
            chatbot_id=chatbot_id,
            source_type=KnowledgeSourceType.UPLOADED_FILE,
            status=KnowledgeSourceStatus.PENDING,
            pages_found=1
        )
        db.add(ks)
        await db.flush()

        # 5. Create UploadedFile record
        uploaded_file = UploadedFile(
            knowledge_source_id=ks.id,
            filename=file.filename,
            file_path=file_path,
            file_size=len(content),
            mime_type=file.content_type
        )
        db.add(uploaded_file)

        # Log activity
        activity = ChatbotActivity(
            chatbot_id=chatbot_id,
            user_id=user.id,
            activity_type="knowledge_source",
            description=f"Uploaded document: {file.filename} by {user.name or user.email}"
        )
        db.add(activity)

        await db.commit()
        
        # Fetch with loaded relationships to avoid MissingGreenlet during validation
        stmt = select(KnowledgeSource).options(
            selectinload(KnowledgeSource.files),
            selectinload(KnowledgeSource.qa_pairs),
            selectinload(KnowledgeSource.pages)
        ).where(KnowledgeSource.id == ks.id)
        ks = (await db.execute(stmt)).scalar_one()

        # 6. Extract text and embed in background
        background_tasks.add_task(
            ChatbotService._process_uploaded_file,
            ks.id,
            file_path,
            file.content_type
        )

        return FileUploadResponse(
            knowledge_source_id=ks.id,
            filename=file.filename,
            status=ks.status
        )

    @staticmethod
    async def _process_uploaded_file(ks_id: UUID, file_path: str, mime_type: str):
        """Background task to extract text from file and generate embeddings"""
        async with AsyncSessionLocal() as db:
            try:
                # Update status
                await db.execute(
                    update(KnowledgeSource)
                    .where(KnowledgeSource.id == ks_id)
                    .values(status=KnowledgeSourceStatus.CRAWLING)
                )
                await db.commit()

                # Extract text
                text = FileService.extract_text(file_path, mime_type)
                if not text:
                    raise Exception("Failed to extract text from file")

                # Create a "virtual page" for the file content so embedding service can use it
                # Or we can modify embedding service to handle raw text. 
                # For now, let's create a CrawledPage entry as it's the expected input for EmbeddingService
                stmt = select(KnowledgeSource).where(KnowledgeSource.id == ks_id)
                ks = (await db.execute(stmt)).scalar_one()
                
                crawled_page = CrawledPage(
                    knowledge_source_id=ks_id,
                    url=f"file://{os.path.basename(file_path)}",
                    title=os.path.basename(file_path),
                    content=text
                )
                db.add(crawled_page)
                await db.commit()

                # Run embedding pipeline
                await EmbeddingService.process_knowledge_source(ks_id)

                # Final update
                await db.execute(
                    update(KnowledgeSource)
                    .where(KnowledgeSource.id == ks_id)
                    .values(status=KnowledgeSourceStatus.COMPLETED)
                )
                await db.commit()
                logger.success(f"Successfully processed uploaded file for KS: {ks_id}")

            except Exception as e:
                logger.error(f"Error processing uploaded file {ks_id}: {str(e)}")
                await db.execute(
                    update(KnowledgeSource)
                    .where(KnowledgeSource.id == ks_id)
                    .values(status=KnowledgeSourceStatus.FAILED)
                )
                await db.commit()

    @staticmethod
    async def delete_knowledge_source(
        db: AsyncSession,
        tenant_id: int,
        ks_id: UUID,
        user: User
    ) -> None:
        """Delete a knowledge source and all its associated data (pages, embeddings, files)"""
        
        # 1. Find knowledge source
        stmt = select(KnowledgeSource).options(selectinload(KnowledgeSource.files)).where(KnowledgeSource.id == ks_id)
        result = await db.execute(stmt)
        ks = result.scalar_one_or_none()
        
        if not ks:
            raise NotFoundError("Knowledge source not found")

        # 2. Verify permission (can_manage_knowledge)
        if not await ChatbotService.has_permission(db, ks.chatbot_id, user, "can_manage_knowledge"):
            raise ForbiddenError("Insufficient permissions to delete knowledge")

        # 3. If it's a file, delete the actual file from disk
        for file_record in ks.files:
            try:
                if os.path.exists(file_record.file_path):
                    os.remove(file_record.file_path)
            except Exception as e:
                logger.error(f"Failed to delete file from disk: {file_record.file_path} - {e}")

        # 4. Delete from database (cascade will handle pages, embeddings, files)
        await db.execute(delete(KnowledgeSource).where(KnowledgeSource.id == ks_id))
        await db.commit()
        logger.success(f"Deleted knowledge source {ks_id}")

    @staticmethod
    async def delete_crawled_page(
        db: AsyncSession,
        page_id: UUID,
        user: User
    ) -> None:
        """Delete an individual crawled page and its embeddings"""
        
        # 1. Find page
        stmt = select(CrawledPage).where(CrawledPage.id == page_id)
        result = await db.execute(stmt)
        page = result.scalar_one_or_none()
        
        if not page:
            raise NotFoundError("Page not found")

        # 2. Find parent knowledge source to check permissions
        stmt = select(KnowledgeSource).where(KnowledgeSource.id == page.knowledge_source_id)
        result = await db.execute(stmt)
        ks = result.scalar_one()

        # 3. Verify permission (can_manage_knowledge)
        if not await ChatbotService.has_permission(db, ks.chatbot_id, user, "can_manage_knowledge"):
            raise ForbiddenError("Insufficient permissions to delete page")

        # 4. Delete associated embeddings
        await db.execute(delete(Embedding).where(
            Embedding.knowledge_source_id == ks.id,
            Embedding.metadata_json['page_id'].as_string() == str(page_id)
        ))

        # 5. Delete page
        await db.delete(page)
        
        # 6. Update pages_found count in KnowledgeSource
        ks.pages_found = max(0, ks.pages_found - 1)
        
        await db.commit()
        logger.success(f"Deleted crawled page {page_id}")

    @staticmethod
    async def bulk_delete_knowledge_sources(
        db: AsyncSession,
        tenant_id: int,
        chatbot_id: UUID,
        source_ids: List[UUID],
        user: User
    ) -> None:
        """Bulk delete knowledge sources"""
        for source_id in source_ids:
            try:
                await ChatbotService.delete_knowledge_source(db, tenant_id, source_id, user)
            except Exception as e:
                logger.error(f"Failed to delete source {source_id}: {e}")
        await db.commit()

    @staticmethod
    async def bulk_delete_qa_pairs(
        db: AsyncSession,
        qa_ids: List[UUID],
        user: User
    ) -> None:
        """Bulk delete QA pairs"""
        for qa_id in qa_ids:
            try:
                await ChatbotService.delete_qa_pair(db, qa_id, user)
            except Exception as e:
                logger.error(f"Failed to delete QA pair {qa_id}: {e}")
        await db.commit()

    @staticmethod
    async def bulk_delete_pages(
        db: AsyncSession,
        page_ids: List[UUID],
        user: User
    ) -> None:
        """Bulk delete individual pages"""
        for page_id in page_ids:
            try:
                await ChatbotService.delete_crawled_page(db, page_id, user)
            except Exception as e:
                logger.error(f"Failed to delete page {page_id}: {e}")
        await db.commit()

    # ============== QA Pair Management ==============

    @staticmethod
    async def create_qa_pair(
        db: AsyncSession,
        tenant_id: int,
        chatbot_id: UUID,
        user: User,
        request: QAPairCreate,
        background_tasks: BackgroundTasks
    ) -> QAPairResponse:
        """Create a single QA pair and re-embed"""
        
        # Verify access and permission (can_manage_knowledge)
        if not await ChatbotService.has_permission(db, chatbot_id, user, "can_manage_knowledge"):
            raise ForbiddenError("Insufficient permissions to manage QA pairs")

        # Get or create a "Manual QA" KnowledgeSource for this chatbot
        stmt = select(KnowledgeSource).where(
            KnowledgeSource.chatbot_id == chatbot_id,
            KnowledgeSource.source_type == KnowledgeSourceType.QA_PAIR,
            KnowledgeSource.source_url == "manual"
        )
        ks = (await db.execute(stmt)).scalar_one_or_none()
        
        if not ks:
            ks = KnowledgeSource(
                chatbot_id=chatbot_id,
                source_type=KnowledgeSourceType.QA_PAIR,
                source_url="manual",
                status=KnowledgeSourceStatus.COMPLETED
            )
            db.add(ks)
            await db.flush()

        qa = QAPair(
            knowledge_source_id=ks.id,
            question=request.question,
            answer=request.answer
        )
        db.add(qa)

        # Log activity
        activity = ChatbotActivity(
            chatbot_id=chatbot_id,
            user_id=user.id,
            activity_type="knowledge_source",
            description=f"Added Q&A pair by {user.name or user.email}"
        )
        db.add(activity)

        await db.commit()
        await db.refresh(qa)

        # Trigger re-embedding for the whole source (simplest for now)
        background_tasks.add_task(EmbeddingService.process_knowledge_source, ks.id)

        return QAPairResponse.model_validate(qa)

    @staticmethod
    async def upload_qa_xlsx(
        db: AsyncSession,
        tenant_id: int,
        chatbot_id: UUID,
        user: User,
        file: UploadFile,
        background_tasks: BackgroundTasks
    ) -> KnowledgeSourceResponse:
        """Bulk upload QA pairs from XLSX"""
        
        await ChatbotService.get_chatbot(db, tenant_id, chatbot_id, user)
        
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise BadRequestError("Please upload an Excel file (.xlsx or .xls)")

        content = await file.read()
        try:
            df = pd.read_excel(io.BytesIO(content))
            
            # Normalize column names: lowercase and strip spaces
            original_cols = list(df.columns)
            df.columns = [str(col).lower().strip() for col in df.columns]
            
            # Map potential column names to standard names
            col_map = {}
            for col in df.columns:
                if col in ['question', 'q', 'queries', 'query']:
                    col_map[col] = 'question'
                elif col in ['answer', 'a', 'responses', 'response']:
                    col_map[col] = 'answer'
            
            if 'question' in col_map.values() and 'answer' in col_map.values():
                # Rename the identified columns to 'question' and 'answer'
                rename_dict = {k: v for k, v in col_map.items()}
                df = df.rename(columns=rename_dict)
            else:
                raise BadRequestError(
                    f"Excel must contain 'question' and 'answer' columns (or 'q' and 'a'). "
                    f"Found columns: {original_cols}"
                )
        except BadRequestError:
            raise
        except Exception as e:
            raise BadRequestError(f"Failed to parse Excel: {str(e)}")

        ks = KnowledgeSource(
            chatbot_id=chatbot_id,
            source_type=KnowledgeSourceType.QA_PAIR,
            source_url=file.filename,
            status=KnowledgeSourceStatus.CRAWLING
        )
        db.add(ks)
        await db.flush()

        count = 0
        for _, row in df.iterrows():
            q = str(row['question']).strip()
            a = str(row['answer']).strip()
            if q and a:
                qa = QAPair(knowledge_source_id=ks.id, question=q, answer=a)
                db.add(qa)
                count += 1

        ks.pages_found = count
        await db.commit()
        
        # Fetch with loaded relationships to avoid MissingGreenlet during validation
        stmt = select(KnowledgeSource).options(
            selectinload(KnowledgeSource.files),
            selectinload(KnowledgeSource.qa_pairs),
            selectinload(KnowledgeSource.pages)
        ).where(KnowledgeSource.id == ks.id)
        ks = (await db.execute(stmt)).scalar_one()

        # Re-embed everything in this new source
        background_tasks.add_task(EmbeddingService.process_knowledge_source, ks.id)
        
        return KnowledgeSourceResponse.model_validate(ks)

    @staticmethod
    async def list_qa_pairs(
        db: AsyncSession,
        tenant_id: int,
        chatbot_id: UUID,
        user: User
    ) -> List[QAPairResponse]:
        """List all QA pairs for a chatbot across all QA sources"""
        await ChatbotService.get_chatbot(db, tenant_id, chatbot_id, user)
        
        stmt = select(QAPair).join(KnowledgeSource).where(KnowledgeSource.chatbot_id == chatbot_id)
        result = await db.execute(stmt)
        return [QAPairResponse.model_validate(qa) for qa in result.scalars().all()]

    @staticmethod
    async def update_qa_pair(
        db: AsyncSession,
        qa_id: UUID,
        user: User,
        request: QAPairCreate,
        background_tasks: BackgroundTasks
    ) -> QAPairResponse:
        stmt = select(QAPair).where(QAPair.id == qa_id)
        qa = (await db.execute(stmt)).scalar_one_or_none()
        if not qa: raise NotFoundError("QA pair not found")
        
        # Verify access to parent chatbot... (simplified for now)
        
        qa.question = request.question
        qa.answer = request.answer
        await db.commit()
        await db.refresh(qa)
        
        # Re-embed source
        background_tasks.add_task(EmbeddingService.process_knowledge_source, qa.knowledge_source_id)
        return QAPairResponse.model_validate(qa)

    @staticmethod
    async def delete_qa_pair(
        db: AsyncSession,
        qa_id: UUID,
        user: User
    ) -> None:
        stmt = select(QAPair).where(QAPair.id == qa_id)
        qa = (await db.execute(stmt)).scalar_one_or_none()
        if not qa: raise NotFoundError("QA pair not found")
        
        ks_id = qa.knowledge_source_id
        await db.delete(qa)
        await db.commit()
        
        # We also need to delete the specific embedding for this QA
        # Instead of re-embedding everything (slow), let's just delete the embedding record
        # Embedding metadata contains "qa_id"
        # However, for simplicity and consistency, let's just re-embed the source in background if it has many pairs
        # Or just delete the embedding directly.
        
        await db.execute(delete(Embedding).where(
            Embedding.knowledge_source_id == ks_id,
            Embedding.metadata_json['qa_id'].as_string() == str(qa_id)
        ))
        await db.commit()

    @staticmethod
    async def get_overview_stats(
        db: AsyncSession,
        tenant_id: int,
        chatbot_id: UUID,
        user: User
    ) -> ChatbotStatsResponse:
        """Get overview statistics for a chatbot"""
        # Verify access and permission (can_view_analytics)
        if not await ChatbotService.has_permission(db, chatbot_id, user, "can_view_analytics"):
            raise ForbiddenError("Insufficient permissions to view stats")

        # 1. Total Conversations (Sessions with actual messages)
        # Only count sessions that have at least one user message
        sessions_with_messages_stmt = select(func.count(func.distinct(ChatMessage.session_id))).where(
            ChatMessage.session_id.in_(
                select(ChatSession.id).where(ChatSession.chatbot_id == chatbot_id)
            )
        ).where(ChatMessage.role == MessageRole.USER)
        sessions_count = (await db.execute(sessions_with_messages_stmt)).scalar() or 0

        # 2. Knowledge Sources
        ks_stmt = select(KnowledgeSource).where(KnowledgeSource.chatbot_id == chatbot_id)
        ks_result = await db.execute(ks_stmt)
        ks_list = ks_result.scalars().all()
        
        total_ks = len(ks_list)
        active_ks = len([ks for ks in ks_list if ks.status == KnowledgeSourceStatus.COMPLETED])

        # 2.5. Calculate total knowledge base size
        total_kb_size = 0

        if ks_list:
            ks_ids = [ks.id for ks in ks_list]
            
            # Sum uploaded file sizes
            uploaded_files_stmt = select(func.sum(UploadedFile.file_size)).where(
                UploadedFile.knowledge_source_id.in_(ks_ids)
            )
            uploaded_size = (await db.execute(uploaded_files_stmt)).scalar() or 0
            total_kb_size += uploaded_size

            # Estimate crawled content size (average ~2KB per page)
            crawled_pages_stmt = select(func.count(CrawledPage.id)).where(
                CrawledPage.knowledge_source_id.in_(ks_ids)
            )
            crawled_pages_count = (await db.execute(crawled_pages_stmt)).scalar() or 0
            total_kb_size += crawled_pages_count * 2000  # Estimate 2KB per page

            # Estimate QA pairs size (average ~500 bytes per pair)
            qa_pairs_stmt = select(func.count(QAPair.id)).where(
                QAPair.knowledge_source_id.in_(ks_ids)
            )
            qa_pairs_count = (await db.execute(qa_pairs_stmt)).scalar() or 0
            total_kb_size += qa_pairs_count * 500  # Estimate 500 bytes per QA pair

        # 3. Recent Activity (Knowledge additions and Status changes)
        activity = []
        
        # Fetch explicit activities from database
        activity_stmt = select(ChatbotActivity).where(ChatbotActivity.chatbot_id == chatbot_id).order_by(ChatbotActivity.created_at.desc()).limit(10)
        db_activities = (await db.execute(activity_stmt)).scalars().all()
        
        for db_act in db_activities:
            activity.append(RecentActivity(
                id=db_act.id,
                type=db_act.activity_type,
                description=db_act.description,
                created_at=db_act.created_at
            ))

        # Sort combined activity by date
        activity.sort(key=lambda x: x.created_at, reverse=True)

        return ChatbotStatsResponse(
            total_conversations=sessions_count,
            total_knowledge_sources=total_ks,
            active_knowledge_sources=active_ks,
            total_kb_size=total_kb_size,
            recent_activity=activity[:10]
        )

    @staticmethod
    async def get_analytics_overview(
        db: AsyncSession,
        tenant_id: int,
        chatbot_id: Optional[UUID],
        user: User
    ) -> AnalyticsOverviewResponse:
        """Get analytics overview for all chatbots or a specific one"""
        # For now, we'll aggregate from chat_sessions and chat_messages
        # In a real app, you'd have an analytics_events table
        
        query = select(ChatSession)
        if chatbot_id:
            # Verify access to specific chatbot
            await ChatbotService.get_chatbot(db, tenant_id, chatbot_id, user)
            query = query.where(ChatSession.chatbot_id == chatbot_id)
        else:
            # Verify access to tenant's chatbots (implicit in tenant_id)
            # Find all chatbot IDs user has access to
            chatbots = await ChatbotService.list_chatbots(db, tenant_id, user)
            chatbot_ids = [c.id for c in chatbots]
            query = query.where(ChatSession.chatbot_id.in_(chatbot_ids))

        sessions = (await db.execute(query)).scalars().all()
        total_sessions = len(sessions)
        
        session_ids = [s.id for s in sessions]
        if not session_ids:
            return AnalyticsOverviewResponse(
                total_sessions=0,
                total_messages=0,
                avg_messages_per_session=0.0
            )

        messages_stmt = select(func.count(ChatMessage.id)).where(ChatMessage.session_id.in_(session_ids))
        total_messages = (await db.execute(messages_stmt)).scalar() or 0
        
        avg_msgs = total_messages / total_sessions if total_sessions > 0 else 0

        return AnalyticsOverviewResponse(
            total_sessions=total_sessions,
            total_messages=total_messages,
            avg_messages_per_session=round(avg_msgs, 1)
        )

    # ============== Crawl Scheduling ==============

    @staticmethod
    async def get_crawl_schedule(
        db: AsyncSession,
        knowledge_source_id: UUID,
        user: User
    ) -> CrawlScheduleResponse:
        """Get crawl schedule for a knowledge source"""
        # Verify access
        stmt = select(KnowledgeSource).where(KnowledgeSource.id == knowledge_source_id)
        ks = (await db.execute(stmt)).scalar_one_or_none()
        if not ks:
            raise NotFoundError("Knowledge source not found")
        
        if user.role != UserRole.ADMIN:
            perm = await ChatbotService._get_user_permission(db, ks.chatbot_id, user)
            if not perm:
                raise ForbiddenError("Access denied")
        
        # Get schedule
        stmt = select(CrawlSchedule).where(CrawlSchedule.knowledge_source_id == knowledge_source_id)
        schedule = (await db.execute(stmt)).scalar_one_or_none()
        
        if not schedule:
            # Return default manual schedule
            schedule = CrawlSchedule(
                knowledge_source_id=knowledge_source_id,
                schedule_type=ScheduleType.MANUAL,
                preferred_hour=2,
                is_active=False
            )
            db.add(schedule)
            await db.commit()
            await db.refresh(schedule)
        
        return CrawlScheduleResponse.model_validate(schedule)

    @staticmethod
    async def create_or_update_schedule(
        db: AsyncSession,
        knowledge_source_id: UUID,
        user: User,
        request: CrawlScheduleCreate
    ) -> CrawlScheduleResponse:
        """Create or update crawl schedule"""
        # Verify access
        stmt = select(KnowledgeSource).where(KnowledgeSource.id == knowledge_source_id)
        ks = (await db.execute(stmt)).scalar_one_or_none()
        if not ks:
            raise NotFoundError("Knowledge source not found")
        
        if user.role != UserRole.ADMIN:
            perm = await ChatbotService._get_user_permission(db, ks.chatbot_id, user)
            if not perm or perm not in [PermissionLevel.EDITOR, PermissionLevel.OWNER]:
                raise ForbiddenError("Insufficient permissions")
        
        # Only allow scheduling for crawled URLs
        if ks.source_type != KnowledgeSourceType.CRAWLED_URL:
            raise BadRequestError("Scheduling is only available for crawled URLs")
        
        schedule = await SchedulerService.create_or_update_schedule(
            db=db,
            knowledge_source_id=str(knowledge_source_id),
            schedule_type=request.schedule_type,
            day_of_week=request.day_of_week,
            preferred_hour=request.preferred_hour,
            is_active=request.is_active
        )
        
        return CrawlScheduleResponse.model_validate(schedule)

    @staticmethod
    async def update_schedule(
        db: AsyncSession,
        knowledge_source_id: UUID,
        user: User,
        request: CrawlScheduleUpdate
    ) -> CrawlScheduleResponse:
        """Update crawl schedule"""
        # Verify access
        stmt = select(KnowledgeSource).where(KnowledgeSource.id == knowledge_source_id)
        ks = (await db.execute(stmt)).scalar_one_or_none()
        if not ks:
            raise NotFoundError("Knowledge source not found")
        
        if user.role != UserRole.ADMIN:
            perm = await ChatbotService._get_user_permission(db, ks.chatbot_id, user)
            if not perm or perm not in [PermissionLevel.EDITOR, PermissionLevel.OWNER]:
                raise ForbiddenError("Insufficient permissions")
        
        # Get existing schedule
        stmt = select(CrawlSchedule).where(CrawlSchedule.knowledge_source_id == knowledge_source_id)
        schedule = (await db.execute(stmt)).scalar_one_or_none()
        
        if not schedule:
            raise NotFoundError("Schedule not found")
        
        # Update fields
        if request.schedule_type is not None:
            schedule.schedule_type = request.schedule_type
        if request.day_of_week is not None:
            schedule.day_of_week = request.day_of_week
        if request.preferred_hour is not None:
            schedule.preferred_hour = request.preferred_hour
        if request.is_active is not None:
            schedule.is_active = request.is_active
        
        # Recalculate next crawl time
        if schedule.schedule_type != ScheduleType.MANUAL and schedule.is_active:
            schedule.next_crawl_at = SchedulerService.calculate_next_crawl(schedule)
        else:
            schedule.next_crawl_at = None
        
        await db.commit()
        await db.refresh(schedule)
        
        return CrawlScheduleResponse.model_validate(schedule)

    @staticmethod
    async def trigger_crawl_now(
        db: AsyncSession,
        knowledge_source_id: UUID,
        user: User,
        background_tasks: BackgroundTasks
    ) -> TriggerCrawlResponse:
        """Trigger an immediate re-crawl"""
        # Verify access
        stmt = select(KnowledgeSource).where(KnowledgeSource.id == knowledge_source_id)
        ks = (await db.execute(stmt)).scalar_one_or_none()
        if not ks:
            raise NotFoundError("Knowledge source not found")
        
        if user.role != UserRole.ADMIN:
            perm = await ChatbotService._get_user_permission(db, ks.chatbot_id, user)
            if not perm or perm not in [PermissionLevel.EDITOR, PermissionLevel.OWNER]:
                raise ForbiddenError("Insufficient permissions")
        
        # Only allow for crawled URLs
        if ks.source_type != KnowledgeSourceType.CRAWLED_URL:
            raise BadRequestError("Manual crawl is only available for crawled URLs")
        
        # Check if already crawling
        if ks.status == KnowledgeSourceStatus.CRAWLING:
            raise BadRequestError("Crawl already in progress")
        
        # Create crawl history entry
        crawl_history = CrawlHistory(
            knowledge_source_id=knowledge_source_id,
            started_at=datetime.now(timezone.utc),
            status=CrawlStatus.SUCCESS,
            pages_checked=0,
            pages_added=0,
            pages_updated=0,
            pages_removed=0
        )
        db.add(crawl_history)
        await db.commit()
        await db.refresh(crawl_history)
        
        # Trigger crawl in background
        background_tasks.add_task(
            CrawlerService.start_crawl,
            knowledge_source_id=str(knowledge_source_id),
            base_url=ks.source_url,
            max_pages=500,
            is_recrawl=True,
            crawl_history_id=str(crawl_history.id)
        )
        
        return TriggerCrawlResponse(
            message="Crawl started",
            crawl_history_id=crawl_history.id
        )

    @staticmethod
    async def get_crawl_history(
        db: AsyncSession,
        knowledge_source_id: UUID,
        user: User,
        limit: int = 20
    ) -> List[CrawlHistoryResponse]:
        """Get crawl history for a knowledge source"""
        # Verify access
        stmt = select(KnowledgeSource).where(KnowledgeSource.id == knowledge_source_id)
        ks = (await db.execute(stmt)).scalar_one_or_none()
        if not ks:
            raise NotFoundError("Knowledge source not found")
        
        if user.role != UserRole.ADMIN:
            perm = await ChatbotService._get_user_permission(db, ks.chatbot_id, user)
            if not perm:
                raise ForbiddenError("Access denied")
        
        # Get history
        stmt = select(CrawlHistory).where(
            CrawlHistory.knowledge_source_id == knowledge_source_id
        ).order_by(CrawlHistory.started_at.desc()).limit(limit)
        
        result = await db.execute(stmt)
        history = result.scalars().all()
        
        return [CrawlHistoryResponse.model_validate(h) for h in history]