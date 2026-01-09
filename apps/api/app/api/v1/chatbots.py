from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List, Optional

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_tenant
from app.models.user import User
from app.models.tenant import Tenant
from app.services.chatbot_service import ChatbotService
from app.services.analytics_service import AnalyticsService
from app.schemas.chatbot import (
    ChatbotCreate,
    ChatbotUpdate,
    ChatbotWithPermission,
    ChatbotListResponse,
    PermissionAssign,
    PermissionResponse,
    PermissionListResponse,
    ChatbotStatsResponse,
    AnalyticsOverviewResponse,
)
from app.schemas.analytics import UnansweredQueriesResponse, ResolveQueriesRequest
from app.schemas.appearance import (
    ChatbotAppearanceResponse,
    ChatbotAppearanceUpdate,
    AvatarUploadResponse,
)
from app.schemas.knowledge import (
    KnowledgeSourceCreate,
    KnowledgeSourceResponse,
    CrawlStatusResponse,
    FileUploadResponse,
    QAPairCreate,
    QAPairResponse,
    BulkDeleteRequest,
    CrawlScheduleCreate,
    CrawlScheduleUpdate,
    CrawlScheduleResponse,
    CrawlHistoryResponse,
    TriggerCrawlResponse,
)
from fastapi import APIRouter, Depends, BackgroundTasks, UploadFile, File

router = APIRouter(prefix="/chatbots", tags=["chatbots"])


# ============== Chatbot CRUD ==============

@router.post("", response_model=ChatbotWithPermission, status_code=201)
async def create_chatbot(
    request: ChatbotCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """Create a new chatbot"""
    return await ChatbotService.create_chatbot(
        db=db,
        tenant_id=current_tenant.id,
        user=current_user,
        request=request
    )


@router.get("", response_model=ChatbotListResponse)
async def list_chatbots(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """List chatbots user has access to.
    
    - Admins see all chatbots in tenant
    - Regular users see only chatbots they have permission for
    """
    chatbots = await ChatbotService.list_chatbots(
        db=db,
        tenant_id=current_tenant.id,
        user=current_user,
    )
    return ChatbotListResponse(chatbots=chatbots, total=len(chatbots))


@router.get("/{chatbot_id}", response_model=ChatbotWithPermission)
async def get_chatbot(
    chatbot_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """Get a specific chatbot"""
    return await ChatbotService.get_chatbot(
        db=db,
        tenant_id=current_tenant.id,
        chatbot_id=chatbot_id,
        user=current_user,
    )

@router.post("/{chatbot_id}/avatar", response_model=AvatarUploadResponse, status_code=201)
async def upload_avatar(
    chatbot_id: UUID,
    avatar: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """Upload a custom avatar for a chatbot"""
    return await ChatbotService.upload_avatar(
        db=db,
        tenant_id=current_tenant.id,
        chatbot_id=chatbot_id,
        user=current_user,
        file=avatar
    )


@router.patch("/{chatbot_id}", response_model=ChatbotWithPermission)
async def update_chatbot(
    chatbot_id: UUID,
    request: ChatbotUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """Update chatbot (requires EDITOR+ permission)"""
    return await ChatbotService.update_chatbot(
        db=db,
        tenant_id=current_tenant.id,
        chatbot_id=chatbot_id,
        user=current_user,
        request=request
    )


@router.delete("/{chatbot_id}", status_code=204)
async def delete_chatbot(
    chatbot_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """Delete chatbot (requires OWNER or tenant ADMIN)"""
    await ChatbotService.delete_chatbot(
        db=db,
        tenant_id=current_tenant.id,
        chatbot_id=chatbot_id,
        user=current_user,
    )


# ============== Permission Management ==============

@router.post("/{chatbot_id}/permissions", response_model=PermissionResponse, status_code=201)
async def assign_permission(
    chatbot_id: UUID,
    request: PermissionAssign,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """Assign permission to a user for this chatbot (requires OWNER/ADMIN permission)"""
    return await ChatbotService.assign_permission(
        db=db,
        tenant_id=current_tenant.id,
        chatbot_id=chatbot_id,
        user=current_user,
        request=request
    )


@router.get("/{chatbot_id}/permissions", response_model=PermissionListResponse)
async def list_permissions(
    chatbot_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """List all permissions for this chatbot"""
    permissions = await ChatbotService.list_permissions(
        db=db,
        tenant_id=current_tenant.id,
        chatbot_id=chatbot_id,
        user=current_user,
    )
    return PermissionListResponse(permissions=permissions, total=len(permissions))


@router.delete("/{chatbot_id}/permissions/{user_id}", status_code=204)
async def remove_permission(
    chatbot_id: UUID,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """Remove user's permission from chatbot (requires OWNER/ADMIN permission)"""
    await ChatbotService.remove_permission(
        db=db,
        tenant_id=current_tenant.id,
        chatbot_id=chatbot_id,
        target_user_id=user_id,
        user=current_user,
    )


# ============== Appearance Management ==============

@router.get("/{chatbot_id}/appearance", response_model=ChatbotAppearanceResponse)
async def get_appearance(
    chatbot_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """Get chatbot appearance settings (creates default if doesn't exist)"""
    return await ChatbotService.get_appearance(
        db=db,
        tenant_id=current_tenant.id,
        chatbot_id=chatbot_id,
        user=current_user,
    )


@router.patch("/{chatbot_id}/appearance", response_model=ChatbotAppearanceResponse)
async def update_appearance(
    chatbot_id: UUID,
    request: ChatbotAppearanceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """Update chatbot appearance settings (requires EDITOR+ permission)"""
    return await ChatbotService.update_appearance(
        db=db,
        tenant_id=current_tenant.id,
        chatbot_id=chatbot_id,
        user=current_user,
        request=request
    )


# ============== Knowledge Base Management ==============

@router.post("/{chatbot_id}/crawl", response_model=KnowledgeSourceResponse, status_code=202)
async def start_crawl(
    chatbot_id: UUID,
    request: KnowledgeSourceCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """Start crawling a website for chatbot knowledge"""
    return await ChatbotService.create_crawl_source(
        db=db,
        tenant_id=current_tenant.id,
        chatbot_id=chatbot_id,
        user=current_user,
        request=request,
        background_tasks=background_tasks
    )


@router.get("/{chatbot_id}/knowledge-sources", response_model=List[KnowledgeSourceResponse])
async def list_knowledge_sources(
    chatbot_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """List all knowledge sources for a chatbot"""
    return await ChatbotService.list_knowledge_sources(
        db=db,
        tenant_id=current_tenant.id,
        chatbot_id=chatbot_id,
        user=current_user
    )


@router.get("/knowledge-sources/{source_id}/status", response_model=CrawlStatusResponse)
async def get_knowledge_source_status(
    source_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get status/progress of a knowledge source crawl"""
    return await ChatbotService.get_knowledge_source_status(
        db=db,
        knowledge_source_id=source_id,
        user=current_user
    )


@router.post("/{chatbot_id}/upload", response_model=FileUploadResponse, status_code=202)
async def upload_file(
    chatbot_id: UUID,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """Upload a file to train the chatbot"""
    return await ChatbotService.upload_file(
        db=db,
        tenant_id=current_tenant.id,
        chatbot_id=chatbot_id,
        user=current_user,
        file=file,
        background_tasks=background_tasks
    )


@router.delete("/knowledge-sources/{source_id}", status_code=204)
async def delete_knowledge_source(
    source_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """Delete a knowledge source and its associated embeddings"""
    await ChatbotService.delete_knowledge_source(
        db=db,
        tenant_id=current_tenant.id,
        ks_id=source_id,
        user=current_user
    )


@router.delete("/pages/{page_id}", status_code=204)
async def delete_crawled_page(
    page_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an individual crawled page"""
    await ChatbotService.delete_crawled_page(
        db=db,
        page_id=page_id,
        user=current_user
    )


@router.post("/{chatbot_id}/knowledge-sources/bulk-delete", status_code=204)
async def bulk_delete_knowledge_sources(
    chatbot_id: UUID,
    request: BulkDeleteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """Bulk delete knowledge sources"""
    await ChatbotService.bulk_delete_knowledge_sources(
        db=db,
        tenant_id=current_tenant.id,
        chatbot_id=chatbot_id,
        source_ids=request.ids,
        user=current_user
    )


@router.post("/{chatbot_id}/pages/bulk-delete", status_code=204)
async def bulk_delete_pages(
    chatbot_id: UUID,
    request: BulkDeleteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Bulk delete individual pages"""
    await ChatbotService.bulk_delete_pages(
        db=db,
        page_ids=request.ids,
        user=current_user
    )


# ============== QA Pair Management ==============

@router.post("/{chatbot_id}/qa", response_model=QAPairResponse)
async def create_qa_pair(
    chatbot_id: UUID,
    request: QAPairCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    return await ChatbotService.create_qa_pair(
        db=db,
        tenant_id=current_tenant.id,
        chatbot_id=chatbot_id,
        user=current_user,
        request=request,
        background_tasks=background_tasks
    )


@router.post("/{chatbot_id}/qa/upload", response_model=KnowledgeSourceResponse)
async def upload_qa_xlsx(
    chatbot_id: UUID,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    return await ChatbotService.upload_qa_xlsx(
        db=db,
        tenant_id=current_tenant.id,
        chatbot_id=chatbot_id,
        user=current_user,
        file=file,
        background_tasks=background_tasks
    )


@router.get("/{chatbot_id}/qa", response_model=List[QAPairResponse])
async def list_qa_pairs(
    chatbot_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    return await ChatbotService.list_qa_pairs(
        db=db,
        tenant_id=current_tenant.id,
        chatbot_id=chatbot_id,
        user=current_user
    )


@router.patch("/qa/{qa_id}", response_model=QAPairResponse)
async def update_qa_pair(
    qa_id: UUID,
    request: QAPairCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await ChatbotService.update_qa_pair(
        db=db,
        qa_id=qa_id,
        user=current_user,
        request=request,
        background_tasks=background_tasks
    )


@router.delete("/qa/{qa_id}", status_code=204)
async def delete_qa_pair(
    qa_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await ChatbotService.delete_qa_pair(
        db=db,
        qa_id=qa_id,
        user=current_user
    )


@router.post("/{chatbot_id}/qa/bulk-delete", status_code=204)
async def bulk_delete_qa_pairs(
    chatbot_id: UUID,
    request: BulkDeleteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Bulk delete QA pairs"""
    await ChatbotService.bulk_delete_qa_pairs(
        db=db,
        qa_ids=request.ids,
        user=current_user
    )


# ============== Crawl Scheduling ==============

@router.get("/knowledge-sources/{source_id}/schedule", response_model=CrawlScheduleResponse)
async def get_crawl_schedule(
    source_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get crawl schedule for a knowledge source"""
    return await ChatbotService.get_crawl_schedule(
        db=db,
        knowledge_source_id=source_id,
        user=current_user
    )


@router.post("/knowledge-sources/{source_id}/schedule", response_model=CrawlScheduleResponse)
async def create_or_update_schedule(
    source_id: UUID,
    request: CrawlScheduleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create or update crawl schedule for a knowledge source"""
    return await ChatbotService.create_or_update_schedule(
        db=db,
        knowledge_source_id=source_id,
        user=current_user,
        request=request
    )


@router.patch("/knowledge-sources/{source_id}/schedule", response_model=CrawlScheduleResponse)
async def update_schedule(
    source_id: UUID,
    request: CrawlScheduleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update crawl schedule for a knowledge source"""
    return await ChatbotService.update_schedule(
        db=db,
        knowledge_source_id=source_id,
        user=current_user,
        request=request
    )


@router.post("/knowledge-sources/{source_id}/crawl-now", response_model=TriggerCrawlResponse)
async def trigger_crawl_now(
    source_id: UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Trigger an immediate re-crawl of a knowledge source"""
    return await ChatbotService.trigger_crawl_now(
        db=db,
        knowledge_source_id=source_id,
        user=current_user,
        background_tasks=background_tasks
    )


@router.get("/knowledge-sources/{source_id}/crawl-history", response_model=List[CrawlHistoryResponse])
async def get_crawl_history(
    source_id: UUID,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get crawl history for a knowledge source"""
    return await ChatbotService.get_crawl_history(
        db=db,
        knowledge_source_id=source_id,
        user=current_user,
        limit=limit
    )


# ============== Stats & Analytics ==============

@router.get("/{chatbot_id}/stats", response_model=ChatbotStatsResponse)
async def get_chatbot_stats(
    chatbot_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """Get overview statistics for a specific chatbot"""
    return await ChatbotService.get_overview_stats(
        db=db,
        tenant_id=current_tenant.id,
        chatbot_id=chatbot_id,
        user=current_user,
    )


@router.get("/analytics/overview", response_model=AnalyticsOverviewResponse)
async def get_all_analytics_overview(
    chatbot_id: Optional[UUID] = None,
    period: str = "30d",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """Get analytics overview for all chatbots or a specific one"""
    return await AnalyticsService.get_analytics_overview(
        db=db,
        tenant_id=current_tenant.id,
        chatbot_id=chatbot_id,
        user=current_user,
        period=period
    )


@router.get("/{chatbot_id}/analytics/unanswered", response_model=UnansweredQueriesResponse)
async def get_unanswered_queries(
    chatbot_id: UUID,
    period: str = "30d",
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """Get unanswered queries for a chatbot"""
    return await AnalyticsService.get_unanswered_queries(
        db=db,
        tenant_id=current_tenant.id,
        chatbot_id=chatbot_id,
        user=current_user,
        period=period,
        limit=limit
    )


@router.post("/{chatbot_id}/analytics/unanswered/resolve", status_code=204)
async def resolve_unanswered_queries(
    chatbot_id: UUID,
    request: ResolveQueriesRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """Mark unanswered queries as resolved"""
    await AnalyticsService.resolve_queries(
        db=db,
        tenant_id=current_tenant.id,
        chatbot_id=chatbot_id,
        user=current_user,
        query_texts=request.queries
    )

