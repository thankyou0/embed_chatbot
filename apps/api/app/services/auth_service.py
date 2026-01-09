from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from app.models.user import User, UserRole
from app.models.tenant import Tenant
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.logging import get_logger
from app.core.exceptions import (
    BadRequestError,
    UnauthorizedError,
    NotFoundError,
)
from app.schemas.auth import SignupRequest, LoginRequest, ChangePasswordRequest
from app.schemas.user import UserResponse
from app.schemas.tenant import TenantResponse

logger = get_logger(__name__)


class AuthService:
    @staticmethod
    async def signup(db: AsyncSession, request: SignupRequest) -> dict:
        """Create a new tenant and admin user"""
        logger.info(f"Signup attempt for email: {request.email}, username: {request.username}")
        
        # Check if email already exists
        result = await db.execute(select(User).where(User.email == request.email))
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise BadRequestError("Email already registered")
        
        # Check if username already exists
        result = await db.execute(select(User).where(User.username == request.username))
        existing_username = result.scalar_one_or_none()
        if existing_username:
            raise BadRequestError("Username already taken")
        
        # Check if tenant email already exists
        result = await db.execute(select(Tenant).where(Tenant.email == request.email))
        existing_tenant = result.scalar_one_or_none()
        if existing_tenant:
            raise BadRequestError("Tenant with this email already exists")
        
        # Create tenant
        tenant = Tenant(
            name=request.tenant_name,
            email=request.email,
        )
        db.add(tenant)
        await db.flush()  # Flush to get tenant.id
        
        # Create admin user (admin users don't have password expiration)
        user = User(
            tenant_id=tenant.id,
            email=request.email,
            username=request.username,
            password_hash=get_password_hash(request.password),
            name=request.name,
            role=UserRole.ADMIN,
            is_active=True,
            must_change_password=False,
            password_expires_at=None,
        )
        db.add(user)
        await db.flush()  # Flush to get user.id
        
        await db.commit()
        await db.refresh(tenant)
        await db.refresh(user)
        
        # Create tokens
        token_data = {
            "sub": str(user.id),
            "tenant_id": tenant.id,
            "email": user.email,
        }
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        logger.success(f"User registered: {user.email} (tenant: {tenant.name})")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": UserResponse.model_validate(user),
            "tenant": TenantResponse.model_validate(tenant),
        }
    
    @staticmethod
    async def login(db: AsyncSession, request: LoginRequest) -> dict:
        """Authenticate user and return tokens"""
        logger.info(f"Login attempt for email: {request.email}")
        
        # Find user by email
        result = await db.execute(select(User).where(User.email == request.email))
        user = result.scalar_one_or_none()
        
        if not user:
            raise UnauthorizedError("Incorrect email or password")
        
        # Check if user is active
        if not user.is_active:
            raise UnauthorizedError("Account is disabled")
        
        # Verify password
        if not verify_password(request.password, user.password_hash):
            raise UnauthorizedError("Incorrect email or password")
        
        # Check if temporary password has expired
        if user.password_expires_at and user.password_expires_at < datetime.now(timezone.utc):
            raise UnauthorizedError("Your temporary password has expired. Please contact your administrator for a new password.")
        
        # Get tenant
        result = await db.execute(select(Tenant).where(Tenant.id == user.tenant_id))
        tenant = result.scalar_one_or_none()
        
        if not tenant:
            raise NotFoundError("Tenant not found")
        
        # Create tokens (include must_change_password flag)
        token_data = {
            "sub": str(user.id),
            "tenant_id": tenant.id,
            "email": user.email,
        }
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        logger.success(f"User logged in: {user.email}")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": UserResponse.model_validate(user),
            "tenant": TenantResponse.model_validate(tenant),
        }
    
    @staticmethod
    async def change_password(db: AsyncSession, user: User, request: ChangePasswordRequest) -> dict:
        """Change user's password"""
        logger.info(f"Password change attempt for: {user.email}")
        
        # Verify current password
        if not verify_password(request.current_password, user.password_hash):
            raise UnauthorizedError("Current password is incorrect")
        
        # Validate new password
        if len(request.new_password) < 8:
            raise BadRequestError("New password must be at least 8 characters")
        
        if request.current_password == request.new_password:
            raise BadRequestError("New password must be different from current password")
        
        # Update password
        user.password_hash = get_password_hash(request.new_password)
        user.must_change_password = False
        user.password_expires_at = None  # Clear expiration after password change
        
        await db.commit()
        await db.refresh(user)
        
        # Get tenant
        result = await db.execute(select(Tenant).where(Tenant.id == user.tenant_id))
        tenant = result.scalar_one_or_none()
        
        logger.success(f"Password changed for: {user.email}")
        
        return {
            "message": "Password changed successfully",
            "user": UserResponse.model_validate(user),
            "tenant": TenantResponse.model_validate(tenant) if tenant else None,
        }
    
    @staticmethod
    async def refresh_token(db: AsyncSession, refresh_token: str) -> dict:
        """Refresh access token using refresh token"""
        payload = decode_token(refresh_token)
        
        if payload is None:
            raise UnauthorizedError("Invalid refresh token")
        
        # Check token type
        if payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid token type")
        
        user_id = payload.get("sub")
        tenant_id = payload.get("tenant_id")
        email = payload.get("email")
        
        if not all([user_id, tenant_id, email]):
            raise UnauthorizedError("Invalid token payload")
        
        # Convert user_id to int (JWT sub must be string, but we need int for DB query)
        try:
            user_id_int = int(user_id) if isinstance(user_id, str) else user_id
        except (ValueError, TypeError):
            raise UnauthorizedError("Invalid token payload")
        
        result = await db.execute(select(User).where(User.id == user_id_int))
        user = result.scalar_one_or_none()
        
        if not user:
            raise UnauthorizedError("User not found")
        
        # Create new access token - ensure sub is always a string
        token_data = {
            "sub": str(user.id),
            "tenant_id": user.tenant_id,
            "email": user.email,
        }
        access_token = create_access_token(token_data)
        
        logger.success(f"Token refreshed for: {user.email}")
        
        return {
            "access_token": access_token,
        }

