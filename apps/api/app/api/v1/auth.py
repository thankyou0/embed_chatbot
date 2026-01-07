from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_tenant
from app.schemas.auth import (
    SignupRequest,
    SignupResponse,
    LoginRequest,
    LoginResponse,
    RefreshRequest,
    RefreshResponse,
    ChangePasswordRequest,
    ChangePasswordResponse,
    MeResponse,
)
from app.services.auth_service import AuthService
from app.models.user import User
from app.models.tenant import Tenant
from app.schemas.user import UserResponse
from app.schemas.tenant import TenantResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=SignupResponse, status_code=201)
async def signup(
    request: SignupRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create a new tenant and admin user"""
    result = await AuthService.signup(db, request)
    return SignupResponse(**result)


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate user and return tokens
    
    Note: If the user has a temporary password that has expired,
    login will fail and they need to contact their administrator.
    """
    result = await AuthService.login(db, request)
    return LoginResponse(**result)


@router.post("/refresh", response_model=RefreshResponse)
async def refresh(
    request: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    """Refresh access token using refresh token"""
    result = await AuthService.refresh_token(db, request.refresh_token)
    return RefreshResponse(**result)


@router.post("/change-password", response_model=ChangePasswordResponse)
async def change_password(
    request: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Change current user's password
    
    This endpoint is used to change the user's password.
    Required when `must_change_password` is true (for temporary passwords).
    After successful password change, the temporary password is cleared.
    """
    result = await AuthService.change_password(db, current_user, request)
    return ChangePasswordResponse(**result)


@router.get("/me", response_model=MeResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """Get current user and tenant information
    
    Returns user details including `must_change_password` flag
    which indicates if the user needs to change their password.
    """
    return MeResponse(
        user=UserResponse.model_validate(current_user),
        tenant=TenantResponse.model_validate(current_tenant),
    )

