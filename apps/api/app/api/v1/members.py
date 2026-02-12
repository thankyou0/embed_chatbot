from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_tenant
from app.models.user import User
from app.models.tenant import Tenant
from app.services.member_service import MemberService
from app.schemas.member import (
    MemberCreate,
    MemberUpdate,
    MemberResponse,
    MemberListResponse,
    MemberPasswordReset,
    MemberChatbotPermissionsUpdate,
)

router = APIRouter(prefix="/members", tags=["members"])


@router.post("", response_model=MemberResponse, status_code=201)
async def add_member(
    request: MemberCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """Add a new member to tenant (admin only)
    
    Creates a new member with a temporary password that expires after the specified hours.
    The member will be required to change their password on first login.
    """
    return await MemberService.add_member(
        db=db,
        tenant_id=current_tenant.id,
        admin_user=current_user,
        request=request
    )


@router.get("", response_model=MemberListResponse)
async def list_members(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """List all members in tenant with their chatbot permissions"""
    members = await MemberService.list_members(
        db=db,
        tenant_id=current_tenant.id,
    )
    return MemberListResponse(members=members, total=len(members))


@router.get("/{member_id}", response_model=MemberResponse)
async def get_member(
    member_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """Get a specific member with their chatbot permissions"""
    return await MemberService.get_member(
        db=db,
        tenant_id=current_tenant.id,
        member_id=member_id,
    )


@router.patch("/{member_id}", response_model=MemberResponse)
async def update_member(
    member_id: int,
    request: MemberUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """Update member details (admin only)"""
    return await MemberService.update_member(
        db=db,
        tenant_id=current_tenant.id,
        member_id=member_id,
        admin_user=current_user,
        request=request
    )


@router.post("/{member_id}/reset-password", response_model=MemberResponse)
async def reset_member_password(
    member_id: int,
    request: MemberPasswordReset,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """Reset a member's password with a new temporary one (admin only)
    
    The member will be required to change their password on next login.
    """
    return await MemberService.reset_member_password(
        db=db,
        tenant_id=current_tenant.id,
        member_id=member_id,
        admin_user=current_user,
        request=request
    )


@router.put("/{member_id}/permissions", response_model=MemberResponse)
async def update_member_permissions(
    member_id: int,
    request: MemberChatbotPermissionsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """Update member's chatbot permissions (admin only)
    
    Replaces all existing permissions with the new set.
    Each permission specifies a chatbot and the access level for that member.
    """
    return await MemberService.update_member_chatbot_permissions(
        db=db,
        tenant_id=current_tenant.id,
        member_id=member_id,
        admin_user=current_user,
        request=request
    )


@router.delete("/{member_id}", status_code=204)
async def remove_member(
    member_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """Remove a member from tenant (admin only)
    
    This also removes all chatbot permissions for the member.
    """
    await MemberService.remove_member(
        db=db,
        tenant_id=current_tenant.id,
        member_id=member_id,
        admin_user=current_user,
    )

