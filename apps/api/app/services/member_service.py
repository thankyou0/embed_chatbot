from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.models.user import User, UserRole
from app.models.tenant import Tenant
from app.models.chatbot import Chatbot
from app.models.chatbot_permission import ChatbotPermission, PermissionLevel
from app.core.security import get_password_hash
from app.core.logging import get_logger
from app.core.exceptions import (
    BadRequestError,
    NotFoundError,
    ForbiddenError,
)
from app.schemas.member import (
    MemberCreate, 
    MemberUpdate, 
    MemberResponse,
    MemberPasswordReset,
    MemberChatbotPermissionsUpdate,
    MemberChatbotPermissionResponse,
)

logger = get_logger(__name__)


class MemberService:
    @staticmethod
    async def add_member(
        db: AsyncSession,
        tenant_id: int,
        admin_user: User,
        request: MemberCreate
    ) -> MemberResponse:
        """Add a new member to tenant (admin only)"""
        
        # Verify admin has permission
        if admin_user.role != UserRole.ADMIN:
            raise ForbiddenError("Only admins can add members")
        
        # Check if email already exists
        result = await db.execute(select(User).where(User.email == request.email))
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise BadRequestError("Email already registered")
        
        # Determine username
        username = request.username if request.username else request.email

        # Check if username already exists
        result = await db.execute(select(User).where(User.username == username))
        existing_username = result.scalar_one_or_none()
        if existing_username:
            if request.username:
                raise BadRequestError("Username already taken")
            else:
                # If we're using email as username and it's taken (but email check passed),
                # it means someone deliberately set their username to this email. 
                # Rare edge case.
                raise BadRequestError("Username (derived from email) already exists")
        
        # Calculate password expiration
        password_expires_at = datetime.now(timezone.utc) + timedelta(hours=request.password_expiry_hours)
        
        # Create new member with temporary password
        member = User(
            tenant_id=tenant_id,
            email=request.email,
            username=username,
            password_hash=get_password_hash(request.password),
            name=request.name,
            role=request.role,
            is_active=True,
            password_expires_at=password_expires_at,
            must_change_password=True,  # Force password change on first login
            invited_by=admin_user.id,
        )
        db.add(member)
        await db.flush()  # Get the member.id
        
        # Assign chatbot permissions if provided
        if request.chatbot_permissions:
            for perm in request.chatbot_permissions:
                # Verify chatbot exists and belongs to tenant
                result = await db.execute(
                    select(Chatbot).where(
                        Chatbot.id == perm.chatbot_id,
                        Chatbot.tenant_id == tenant_id,
                        Chatbot.deleted_at.is_(None)
                    )
                )
                chatbot = result.scalar_one_or_none()
                if not chatbot:
                    raise BadRequestError(f"Chatbot {perm.chatbot_id} not found")
                
                # Create permission
                permission = ChatbotPermission(
                    user_id=member.id,
                    chatbot_id=perm.chatbot_id,
                    permission_level=perm.permission_level,
                    can_manage_knowledge=perm.can_manage_knowledge,
                    can_manage_appearance=perm.can_manage_appearance,
                    can_resolve_queries=perm.can_resolve_queries,
                    can_view_analytics=perm.can_view_analytics,
                    granted_by=admin_user.id,
                )
                db.add(permission)
        
        await db.commit()
        await db.refresh(member)
        
        # Log team activity to all chatbots in the tenant
        from app.models.chatbot import ChatbotActivity, Chatbot
        
        chatbots_stmt = select(Chatbot.id).where(
            Chatbot.tenant_id == tenant_id,
            Chatbot.deleted_at.is_(None)
        )
        chatbot_ids = (await db.execute(chatbots_stmt)).scalars().all()
        
        for chatbot_id in chatbot_ids:
            activity = ChatbotActivity(
                chatbot_id=chatbot_id,
                user_id=admin_user.id,
                activity_type="team_member_added",
                description=f"New team member added: {member.email} by {admin_user.email}"
            )
            db.add(activity)
        
        if chatbot_ids:
            await db.commit()
        
        logger.success(f"Member added: {member.email} to tenant {tenant_id} with temp password expiring at {password_expires_at}")
        
        # Get chatbot permissions for response
        permissions = await MemberService._get_member_chatbot_permissions(db, member.id)
        
        return MemberService._to_member_response(member, permissions)
    
    @staticmethod
    def _to_member_response(member: User, permissions: Optional[List[MemberChatbotPermissionResponse]] = None) -> MemberResponse:
        """Convert User model to MemberResponse safely avoiding lazy load issues"""
        return MemberResponse(
            id=member.id,
            tenant_id=member.tenant_id,
            email=member.email,
            username=member.username,
            name=member.name,
            role=member.role,
            is_active=member.is_active,
            must_change_password=member.must_change_password,
            password_expires_at=member.password_expires_at,
            invited_by=member.invited_by,
            created_at=member.created_at,
            chatbot_permissions=permissions
        )

    @staticmethod
    async def _get_member_chatbot_permissions(
        db: AsyncSession,
        member_id: int,
    ) -> List[MemberChatbotPermissionResponse]:
        """Get all chatbot permissions for a member"""
        result = await db.execute(
            select(ChatbotPermission, Chatbot)
            .join(Chatbot, ChatbotPermission.chatbot_id == Chatbot.id)
            .where(
                ChatbotPermission.user_id == member_id,
                Chatbot.deleted_at.is_(None)
            )
        )
        rows = result.all()
        
        return [
            MemberChatbotPermissionResponse(
                chatbot_id=perm.chatbot_id,
                chatbot_name=chatbot.name,
                permission_level=perm.permission_level,
                can_manage_knowledge=perm.can_manage_knowledge,
                can_manage_appearance=perm.can_manage_appearance,
                can_resolve_queries=perm.can_resolve_queries,
                can_view_analytics=perm.can_view_analytics
            )
            for perm, chatbot in rows
        ]
    
    @staticmethod
    async def list_members(
        db: AsyncSession,
        tenant_id: int,
        include_permissions: bool = True,
    ) -> List[MemberResponse]:
        """List all members in a tenant"""
        
        result = await db.execute(
            select(User)
            .where(User.tenant_id == tenant_id)
            .order_by(User.created_at.desc())
        )
        members = result.scalars().all()
        
        member_responses = []
        for m in members:
            permissions = None
            if include_permissions:
                try:
                    permissions = await MemberService._get_member_chatbot_permissions(db, m.id)
                except Exception as e:
                    logger.error(f"Error fetching permissions for member {m.id}: {e}")
                    permissions = []
            
            member_responses.append(MemberService._to_member_response(m, permissions))
        
        return member_responses
    
    @staticmethod
    async def get_member(
        db: AsyncSession,
        tenant_id: int,
        member_id: int,
    ) -> MemberResponse:
        """Get a specific member"""
        
        result = await db.execute(
            select(User)
            .where(User.id == member_id, User.tenant_id == tenant_id)
        )
        member = result.scalar_one_or_none()
        
        if not member:
            raise NotFoundError("Member not found")
        
        permissions = await MemberService._get_member_chatbot_permissions(db, member.id)
        return MemberService._to_member_response(member, permissions)
    
    @staticmethod
    async def update_member(
        db: AsyncSession,
        tenant_id: int,
        member_id: int,
        admin_user: User,
        request: MemberUpdate
    ) -> MemberResponse:
        """Update member details (admin only)"""
        
        # Verify admin has permission
        if admin_user.role != UserRole.ADMIN:
            raise ForbiddenError("Only admins can update members")
        
        # Cannot update self via this endpoint
        if member_id == admin_user.id:
            raise BadRequestError("Cannot modify your own account via this endpoint")
        
        result = await db.execute(
            select(User)
            .where(User.id == member_id, User.tenant_id == tenant_id)
        )
        member = result.scalar_one_or_none()
        
        if not member:
            raise NotFoundError("Member not found")
        
        # Update fields
        if request.name is not None:
            member.name = request.name
        if request.role is not None:
            member.role = request.role
        if request.is_active is not None:
            member.is_active = request.is_active
        
        await db.commit()
        await db.refresh(member)
        
        # Log team activity to all chatbots in the tenant
        from app.models.chatbot import ChatbotActivity, Chatbot
        
        chatbots_stmt = select(Chatbot.id).where(
            Chatbot.tenant_id == tenant_id,
            Chatbot.deleted_at.is_(None)
        )
        chatbot_ids = (await db.execute(chatbots_stmt)).scalars().all()
        
        for chatbot_id in chatbot_ids:
            activity = ChatbotActivity(
                chatbot_id=chatbot_id,
                user_id=admin_user.id,
                activity_type="team_member_updated",
                description=f"Team member updated: {member.email} by {admin_user.email}"
            )
            db.add(activity)
        
        if chatbot_ids:
            await db.commit()
            
        logger.success(f"Member updated: {member.email}")
        permissions = await MemberService._get_member_chatbot_permissions(db, member.id)
        return MemberService._to_member_response(member, permissions)
    
    @staticmethod
    async def reset_member_password(
        db: AsyncSession,
        tenant_id: int,
        member_id: int,
        admin_user: User,
        request: MemberPasswordReset
    ) -> MemberResponse:
        """Reset member password with a new temporary one (admin only)"""
        
        # Verify admin has permission
        if admin_user.role != UserRole.ADMIN:
            raise ForbiddenError("Only admins can reset passwords")
        
        # Cannot reset own password via this endpoint
        if member_id == admin_user.id:
            raise BadRequestError("Cannot reset your own password via this endpoint")
        
        result = await db.execute(
            select(User)
            .where(User.id == member_id, User.tenant_id == tenant_id)
        )
        member = result.scalar_one_or_none()
        
        if not member:
            raise NotFoundError("Member not found")
        
        # Update password with new temporary one
        password_expires_at = datetime.now(timezone.utc) + timedelta(hours=request.password_expiry_hours)
        member.password_hash = get_password_hash(request.new_password)
        member.password_expires_at = password_expires_at
        member.must_change_password = True
        
        await db.commit()
        await db.refresh(member)
        
        # Log team activity to all chatbots in the tenant
        from app.models.chatbot import ChatbotActivity, Chatbot
        
        chatbots_stmt = select(Chatbot.id).where(
            Chatbot.tenant_id == tenant_id,
            Chatbot.deleted_at.is_(None)
        )
        chatbot_ids = (await db.execute(chatbots_stmt)).scalars().all()
        
        for chatbot_id in chatbot_ids:
            activity = ChatbotActivity(
                chatbot_id=chatbot_id,
                user_id=admin_user.id,
                activity_type="team_member_password_reset",
                description=f"Team member password reset: {member.email} by {admin_user.email}"
            )
            db.add(activity)
        
        if chatbot_ids:
            await db.commit()
            
        logger.success(f"Password reset for member: {member.email}")
        
        permissions = await MemberService._get_member_chatbot_permissions(db, member.id)
        return MemberService._to_member_response(member, permissions)
    
    @staticmethod
    async def update_member_chatbot_permissions(
        db: AsyncSession,
        tenant_id: int,
        member_id: int,
        admin_user: User,
        request: MemberChatbotPermissionsUpdate
    ) -> MemberResponse:
        """Update member's chatbot permissions (admin only)"""
        
        # Verify admin has permission
        if admin_user.role != UserRole.ADMIN:
            raise ForbiddenError("Only admins can update permissions")
        
        # Cannot update own permissions via this endpoint
        if member_id == admin_user.id:
            raise BadRequestError("Cannot modify your own permissions via this endpoint")
        
        result = await db.execute(
            select(User)
            .where(User.id == member_id, User.tenant_id == tenant_id)
        )
        member = result.scalar_one_or_none()
        
        if not member:
            raise NotFoundError("Member not found")
        
        # Delete all existing permissions for this member
        await db.execute(
            delete(ChatbotPermission).where(ChatbotPermission.user_id == member_id)
        )
        
        # Add new permissions
        for perm in request.permissions:
            # Verify chatbot exists and belongs to tenant
            result = await db.execute(
                select(Chatbot).where(
                    Chatbot.id == perm.chatbot_id,
                    Chatbot.tenant_id == tenant_id,
                    Chatbot.deleted_at.is_(None)
                )
            )
            chatbot = result.scalar_one_or_none()
            if not chatbot:
                raise BadRequestError(f"Chatbot {perm.chatbot_id} not found")
            
            # Create permission
            permission = ChatbotPermission(
                user_id=member_id,
                chatbot_id=perm.chatbot_id,
                permission_level=perm.permission_level,
                can_manage_knowledge=perm.can_manage_knowledge,
                can_manage_appearance=perm.can_manage_appearance,
                can_resolve_queries=perm.can_resolve_queries,
                can_view_analytics=perm.can_view_analytics,
                granted_by=admin_user.id,
            )
            db.add(permission)
        
        await db.commit()
        await db.refresh(member)
        
        # Log team activity to all chatbots in the tenant
        from app.models.chatbot import ChatbotActivity, Chatbot
        
        chatbots_stmt = select(Chatbot.id).where(
            Chatbot.tenant_id == tenant_id,
            Chatbot.deleted_at.is_(None)
        )
        chatbot_ids = (await db.execute(chatbots_stmt)).scalars().all()
        
        for chatbot_id in chatbot_ids:
            activity = ChatbotActivity(
                chatbot_id=chatbot_id,
                user_id=admin_user.id,
                activity_type="team_permissions_updated",
                description=f"Team member permissions updated: {member.email} by {admin_user.email}"
            )
            db.add(activity)
        
        if chatbot_ids:
            await db.commit()
            
        logger.success(f"Permissions updated for member: {member.email}")
        permissions = await MemberService._get_member_chatbot_permissions(db, member.id)
        return MemberService._to_member_response(member, permissions)
    
    @staticmethod
    async def remove_member(
        db: AsyncSession,
        tenant_id: int,
        member_id: int,
        admin_user: User,
    ) -> None:
        """Remove a member from tenant (admin only)"""
        
        # Verify admin has permission
        if admin_user.role != UserRole.ADMIN:
            raise ForbiddenError("Only admins can remove members")
        
        # Cannot delete self
        if member_id == admin_user.id:
            raise BadRequestError("Cannot delete your own account")
        
        result = await db.execute(
            select(User)
            .where(User.id == member_id, User.tenant_id == tenant_id)
        )
        member = result.scalar_one_or_none()
        
        if not member:
            raise NotFoundError("Member not found")
        
        # Delete member's chatbot permissions first
        await db.execute(
            delete(ChatbotPermission).where(ChatbotPermission.user_id == member_id)
        )
        
        # Store member email before deletion
        member_email = member.email
        
        await db.delete(member)
        await db.commit()
        
        # Log team activity to all chatbots in the tenant
        from app.models.chatbot import ChatbotActivity, Chatbot
        
        chatbots_stmt = select(Chatbot.id).where(
            Chatbot.tenant_id == tenant_id,
            Chatbot.deleted_at.is_(None)
        )
        chatbot_ids = (await db.execute(chatbots_stmt)).scalars().all()
        
        for chatbot_id in chatbot_ids:
            activity = ChatbotActivity(
                chatbot_id=chatbot_id,
                user_id=admin_user.id,
                activity_type="team_member_removed",
                description=f"Team member removed: {member_email} by {admin_user.email}"
            )
            db.add(activity)
        
        if chatbot_ids:
            await db.commit()
            
        logger.success(f"Member removed: {member_email} from tenant {tenant_id}")

