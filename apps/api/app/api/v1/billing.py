"""Billing API endpoints"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.exceptions import ForbiddenError
from app.models.user import User, UserRole
from app.services.billing_service import BillingService
from app.schemas.billing import (
    BillingOverviewResponse,
    ChangePlanRequest,
    ChangePlanResponse
)

router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/overview", response_model=BillingOverviewResponse)
async def get_billing_overview(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get billing overview including subscription, usage, and billing history
    
    Only admins can view billing information
    """
    # Check if user is admin
    if current_user.role != UserRole.ADMIN:
        raise ForbiddenError("Only admins can view billing information")
    
    return await BillingService.get_billing_overview(
        db=db,
        tenant_id=current_user.tenant_id,
        user=current_user
    )


@router.post("/change-plan", response_model=ChangePlanResponse)
async def change_plan(
    request: ChangePlanRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Change subscription plan (admin only)
    """
    return await BillingService.change_plan(
        db=db,
        tenant_id=current_user.tenant_id,
        user=current_user,
        request=request
    )
