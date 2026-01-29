from typing import Optional
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.core.database import get_db
from app.core.security import decode_token
from app.core.exceptions import UnauthorizedError, NotFoundError
from app.models.user import User
from app.models.tenant import Tenant

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Dependency to get the current authenticated user"""
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload is None:
        raise UnauthorizedError("Invalid authentication credentials")
    
    # Check token type
    if payload.get("type") != "access":
        raise UnauthorizedError("Invalid token type")
    
    # Get user_id and convert from string to int
    sub = payload.get("sub")
    if sub is None:
        raise UnauthorizedError("Invalid token payload")
    
    try:
        user_id = int(sub)
    except (ValueError, TypeError):
        raise UnauthorizedError("Invalid token payload")
    
    # Fetch user from database with tenant joined to avoid extra query
    result = await db.execute(
        select(User).where(User.id == user_id).options(joinedload(User.tenant))
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise UnauthorizedError("User not found")
    
    return user


async def get_current_tenant(
    current_user: User = Depends(get_current_user),
) -> Tenant:
    """Dependency to get the current user's tenant"""
    # Tenant is already loaded by get_current_user dependency via joinedload
    tenant = current_user.tenant
    
    if tenant is None:
        raise NotFoundError("Tenant not found")
    
    return tenant

