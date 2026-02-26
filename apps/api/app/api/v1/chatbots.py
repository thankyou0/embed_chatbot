from fastapi import APIRouter, Depends, BackgroundTasks, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List, Optional
from datetime import datetime, timezone
import io

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
    RecentActivityListResponse,
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
        db=db, tenant_id=current_tenant.id, user=current_user, request=request
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


@router.post(
    "/{chatbot_id}/avatar", response_model=AvatarUploadResponse, status_code=201
)
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
        file=avatar,
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
        request=request,
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


@router.post(
    "/{chatbot_id}/permissions", response_model=PermissionResponse, status_code=201
)
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
        request=request,
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
        request=request,
    )


# ============== Knowledge Base Management ==============


@router.post(
    "/{chatbot_id}/crawl", response_model=KnowledgeSourceResponse, status_code=202
)
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
        background_tasks=background_tasks,
    )


@router.get(
    "/{chatbot_id}/knowledge-sources", response_model=List[KnowledgeSourceResponse]
)
async def list_knowledge_sources(
    chatbot_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """List all knowledge sources for a chatbot"""
    return await ChatbotService.list_knowledge_sources(
        db=db, tenant_id=current_tenant.id, chatbot_id=chatbot_id, user=current_user
    )


@router.get("/{chatbot_id}/knowledge-sources/status-stream")
async def knowledge_sources_status_stream(
    chatbot_id: UUID,
    token: str = Query(..., description="JWT access token for SSE auth"),
):
    """
    SSE endpoint: streams all knowledge-source statuses for a chatbot every 2 s.
    Fires a 'done' event when every source has reached a terminal state
    (completed / failed).  The frontend subscribes here during the 'processing'
    phase so it can avoid polling and instead receive a push notification when
    embedding finishes.
    """
    import asyncio
    import json as _json
    from app.core.security import decode_token
    from app.core.database import get_session_factory
    from app.models.knowledge import KnowledgeSource as KSModel

    # --- validate token outside the generator so we can return early ---
    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        async def _unauthorized():
            yield 'event: error\ndata: {"error":"unauthorized"}\n\n'
        return StreamingResponse(_unauthorized(), media_type="text/event-stream")

    async def event_generator():
        session_factory = get_session_factory()
        from sqlalchemy import select as sqlsel
        max_ticks = 150          # 5 minutes max (2 s × 150)
        tick = 0

        while tick < max_ticks:
            try:
                async with session_factory() as db:
                    res = await db.execute(
                        sqlsel(KSModel).where(KSModel.chatbot_id == chatbot_id)
                    )
                    sources = res.scalars().all()

                sources_data = [
                    {
                        "id": str(s.id),
                        "status": s.status.value if hasattr(s.status, "value") else str(s.status),
                        "source_url": s.source_url,
                        "source_type": s.source_type.value if hasattr(s.source_type, "value") else str(s.source_type),
                        "pages_found": s.pages_found or 0,
                        "error_message": s.error_message,
                        "updated_at": s.updated_at.isoformat() if s.updated_at else None,
                        "crawl_progress": s.crawl_progress,
                    }
                    for s in sources
                ]

                yield f"data: {_json.dumps(sources_data)}\n\n"

                terminal = {"completed", "failed"}
                all_done = len(sources_data) > 0 and all(
                    s["status"] in terminal for s in sources_data
                )
                if all_done:
                    yield "event: done\ndata: {}\n\n"
                    return

            except Exception as exc:
                yield f"event: error\ndata: {_json.dumps({'error': str(exc)[:200]})}\n\n"
                return

            await asyncio.sleep(2)
            tick += 1

        # Reached 5-min limit
        yield "event: timeout\ndata: {}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/knowledge-sources/{source_id}/status", response_model=CrawlStatusResponse)
async def get_knowledge_source_status(
    source_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get status/progress of a knowledge source crawl"""
    return await ChatbotService.get_knowledge_source_status(
        db=db, knowledge_source_id=source_id, user=current_user
    )


@router.post("/knowledge-sources/{source_id}/stop", status_code=200)
async def stop_crawl(
    source_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """Stop an active crawl. Saves pages crawled so far."""
    from app.services.crawler_service import request_crawl_cancel

    cancelled = request_crawl_cancel(str(source_id))
    if not cancelled:
        # May already be done or not started yet
        return {"message": "Crawl is not currently active or already completed."}
    return {"message": "Crawl stop requested. Pages crawled so far will be saved."}


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
        background_tasks=background_tasks,
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
        db=db, tenant_id=current_tenant.id, ks_id=source_id, user=current_user
    )


@router.delete("/pages/{page_id}", status_code=204)
async def delete_crawled_page(
    page_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an individual crawled page"""
    await ChatbotService.delete_crawled_page(db=db, page_id=page_id, user=current_user)


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
        user=current_user,
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
        db=db, page_ids=request.ids, user=current_user
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
        background_tasks=background_tasks,
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
        background_tasks=background_tasks,
    )


@router.get("/{chatbot_id}/qa", response_model=List[QAPairResponse])
async def list_qa_pairs(
    chatbot_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    return await ChatbotService.list_qa_pairs(
        db=db, tenant_id=current_tenant.id, chatbot_id=chatbot_id, user=current_user
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
        background_tasks=background_tasks,
    )


@router.delete("/qa/{qa_id}", status_code=204)
async def delete_qa_pair(
    qa_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await ChatbotService.delete_qa_pair(db=db, qa_id=qa_id, user=current_user)


@router.post("/{chatbot_id}/qa/bulk-delete", status_code=204)
async def bulk_delete_qa_pairs(
    chatbot_id: UUID,
    request: BulkDeleteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Bulk delete QA pairs"""
    await ChatbotService.bulk_delete_qa_pairs(
        db=db, qa_ids=request.ids, user=current_user
    )


# ============== Crawl Scheduling ==============


@router.get(
    "/knowledge-sources/{source_id}/schedule", response_model=CrawlScheduleResponse
)
async def get_crawl_schedule(
    source_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get crawl schedule for a knowledge source"""
    return await ChatbotService.get_crawl_schedule(
        db=db, knowledge_source_id=source_id, user=current_user
    )


@router.post(
    "/knowledge-sources/{source_id}/schedule", response_model=CrawlScheduleResponse
)
async def create_or_update_schedule(
    source_id: UUID,
    request: CrawlScheduleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create or update crawl schedule for a knowledge source"""
    return await ChatbotService.create_or_update_schedule(
        db=db, knowledge_source_id=source_id, user=current_user, request=request
    )


@router.patch(
    "/knowledge-sources/{source_id}/schedule", response_model=CrawlScheduleResponse
)
async def update_schedule(
    source_id: UUID,
    request: CrawlScheduleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update crawl schedule for a knowledge source"""
    return await ChatbotService.update_schedule(
        db=db, knowledge_source_id=source_id, user=current_user, request=request
    )


@router.post(
    "/knowledge-sources/{source_id}/crawl-now", response_model=TriggerCrawlResponse
)
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
        background_tasks=background_tasks,
    )


@router.get(
    "/knowledge-sources/{source_id}/crawl-history",
    response_model=List[CrawlHistoryResponse],
)
async def get_crawl_history(
    source_id: UUID,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get crawl history for a knowledge source"""
    return await ChatbotService.get_crawl_history(
        db=db, knowledge_source_id=source_id, user=current_user, limit=limit
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


@router.get("/{chatbot_id}/activities", response_model=RecentActivityListResponse)
async def get_chatbot_recent_activity(
    chatbot_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """Get paginated recent activity for a chatbot."""
    return await ChatbotService.get_recent_activity(
        db=db,
        tenant_id=current_tenant.id,
        chatbot_id=chatbot_id,
        user=current_user,
        page=page,
        page_size=page_size,
    )


@router.get("/{chatbot_id}/activities/export")
async def export_chatbot_recent_activity(
    chatbot_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """Export all chatbot activities as CSV."""
    csv_content = await ChatbotService.export_recent_activity_csv(
        db=db,
        tenant_id=current_tenant.id,
        chatbot_id=chatbot_id,
        user=current_user,
    )

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"chatbot_activities_{chatbot_id}_{timestamp}.csv"

    return StreamingResponse(
        io.BytesIO(csv_content.encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/analytics/overview", response_model=AnalyticsOverviewResponse)
async def get_all_analytics_overview(
    chatbot_id: Optional[UUID] = None,
    period: str = "30d",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """Get analytics overview for all chatbots or a specific one

    Only admins can view analytics overview for all chatbots.
    Members must specify a chatbot_id and must have analytics permission for that chatbot.
    """
    from app.models.user import UserRole
    from app.core.exceptions import ForbiddenError

    # If no chatbot_id specified, only admins can access
    if not chatbot_id and current_user.role != UserRole.ADMIN:
        raise ForbiddenError(
            "Only admins can view analytics for all chatbots. Please specify a chatbot_id."
        )

    return await AnalyticsService.get_analytics_overview(
        db=db,
        tenant_id=current_tenant.id,
        chatbot_id=chatbot_id,
        user=current_user,
        period=period,
    )


@router.get(
    "/{chatbot_id}/analytics/unanswered", response_model=UnansweredQueriesResponse
)
async def get_unanswered_queries(
    chatbot_id: UUID,
    period: str = "30d",
    limit: int = 20,
    query_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """Get unanswered queries for a chatbot. query_type: 'missing_info' or 'reported'"""
    return await AnalyticsService.get_unanswered_queries(
        db=db,
        tenant_id=current_tenant.id,
        chatbot_id=chatbot_id,
        user=current_user,
        period=period,
        limit=limit,
        query_type=query_type,
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
        query_texts=request.queries,
    )


@router.get("/files/{file_id}/preview")
async def preview_file(
    file_id: UUID,
    token: str = Query(..., description="Auth token"),
    db: AsyncSession = Depends(get_db),
):
    """
    Stream the original file (PDF, DOCX, etc.) for browser preview.
    Returns the raw file with proper Content-Type so browsers can display it inline.
    Requires authentication token in query parameter (for new tab viewing).
    """
    from app.models.knowledge import UploadedFile, KnowledgeSource
    from app.models.user import User as UserModel
    from app.models.tenant import Tenant as TenantModel
    from sqlalchemy import select
    from fastapi import HTTPException, status
    from fastapi.responses import Response
    from app.core.security import decode_token
    import httpx
    import os
    import aiofiles

    # Validate token
    try:
        payload = decode_token(token)
        if not payload or payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token")

        user_id = int(payload.get("sub"))
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Get tenant
        stmt = select(TenantModel).where(TenantModel.id == user.tenant_id)
        result = await db.execute(stmt)
        tenant = result.scalar_one_or_none()

        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token format")
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Token validation failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # Fetch the uploaded file
    stmt = select(UploadedFile).where(UploadedFile.id == file_id)
    result = await db.execute(stmt)
    file_record = result.scalar_one_or_none()

    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )

    # Get the knowledge source to find the chatbot
    stmt = select(KnowledgeSource).where(
        KnowledgeSource.id == file_record.knowledge_source_id
    )
    result = await db.execute(stmt)
    knowledge_source = result.scalar_one_or_none()

    if not knowledge_source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge source not found"
        )

    # Verify user has access to this chatbot
    chatbot = await ChatbotService.get_chatbot(
        db=db,
        tenant_id=tenant.id,
        chatbot_id=knowledge_source.chatbot_id,
        user=user,
    )

    file_path = file_record.file_path

    # Check if file is stored remotely (Supabase/S3) or locally
    if file_path.startswith(("http://", "https://")):
        # File is on Supabase/S3 - fetch and stream it
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(file_path)
                response.raise_for_status()
                file_content = response.content
        except Exception as e:
            logger.error(f"Failed to fetch file from remote storage: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not retrieve file from storage",
            )
    else:
        # File is stored locally
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="File not found on disk"
            )
        async with aiofiles.open(file_path, "rb") as f:
            file_content = await f.read()

    # Return file with proper headers for browser inline display
    return Response(
        content=file_content,
        media_type=file_record.mime_type,
        headers={
            "Content-Disposition": f'inline; filename="{file_record.filename}"',
            "Content-Length": str(len(file_content)),
        },
    )


# ============== Developer Logs ==============


@router.get("/developer/knowledge-failures")
async def get_knowledge_failures(
    severity: str = Query("all", description="Filter by severity: all, error, warning"),
    days: str = Query("14", description="Number of days to look back"),
    limit: int = Query(200, description="Maximum number of incidents to return"),
    chatbot_id: Optional[UUID] = Query(None, description="Filter by specific chatbot"),
    search: str = Query("", description="Search in URL, message, or chatbot name"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """
    Get knowledge source failures and warnings for developer debugging.
    Shows crawl failures, file processing errors, embedding failures, API key errors etc.
    """
    from app.models.knowledge import KnowledgeSource, KnowledgeSourceStatus, CrawledPage
    from app.models.chatbot import Chatbot
    from app.models.tenant import Tenant as TenantModel
    from sqlalchemy import select, or_, and_, func
    from datetime import timedelta

    try:
        days_int = int(days)
    except ValueError:
        days_int = 14

    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_int)

    # Build the query for knowledge sources with issues
    stmt = (
        select(
            KnowledgeSource,
            Chatbot.name.label("chatbot_name"),
            TenantModel.name.label("tenant_name"),
        )
        .join(Chatbot, Chatbot.id == KnowledgeSource.chatbot_id)
        .join(TenantModel, TenantModel.id == Chatbot.tenant_id)
        .where(
            Chatbot.tenant_id == current_tenant.id,
            KnowledgeSource.updated_at >= cutoff_date,
        )
    )

    # Filter by severity
    if severity == "error":
        stmt = stmt.where(
            or_(
                KnowledgeSource.status == KnowledgeSourceStatus.FAILED,
                KnowledgeSource.error_message.isnot(None),
            )
        )
    elif severity == "warning":
        stmt = stmt.where(
            and_(
                KnowledgeSource.status != KnowledgeSourceStatus.FAILED,
                KnowledgeSource.error_message.isnot(None),
            )
        )
    else:  # "all" - show anything with an error or failed status
        stmt = stmt.where(
            or_(
                KnowledgeSource.status == KnowledgeSourceStatus.FAILED,
                KnowledgeSource.error_message.isnot(None),
            )
        )

    # Filter by specific chatbot
    if chatbot_id:
        stmt = stmt.where(KnowledgeSource.chatbot_id == chatbot_id)

    # Search filter
    if search.strip():
        search_pattern = f"%{search.strip()}%"
        stmt = stmt.where(
            or_(
                KnowledgeSource.source_url.ilike(search_pattern),
                KnowledgeSource.error_message.ilike(search_pattern),
                Chatbot.name.ilike(search_pattern),
            )
        )

    # Order by most recent first
    stmt = stmt.order_by(KnowledgeSource.updated_at.desc()).limit(limit)

    result = await db.execute(stmt)
    rows = result.fetchall()

    incidents = []
    for row in rows:
        ks = row[0]
        chatbot_name = row[1]
        tenant_name = row[2]

        # Determine severity
        if ks.status == KnowledgeSourceStatus.FAILED:
            incident_severity = "error"
        else:
            incident_severity = "warning"

        # Get last crawl info if available
        last_crawl_status = None
        last_crawl_completed_at = None

        # Build message with more context
        message = ks.error_message or f"Status: {ks.status.value}"

        # Add helpful context for common errors
        if ks.error_message:
            error_lower = ks.error_message.lower()
            if (
                "api key" in error_lower
                or "401" in error_lower
                or "unauthorized" in error_lower
            ):
                message = f"[API KEY ERROR] {ks.error_message}"
            elif "rate limit" in error_lower or "429" in error_lower:
                message = f"[RATE LIMIT] {ks.error_message}"
            elif "timeout" in error_lower:
                message = f"[TIMEOUT] {ks.error_message}"
            elif "connection" in error_lower or "network" in error_lower:
                message = f"[NETWORK] {ks.error_message}"
            elif "quota" in error_lower:
                message = f"[QUOTA] {ks.error_message}"
            elif "embedding" in error_lower:
                message = f"[EMBEDDING] {ks.error_message}"

        incidents.append(
            {
                "knowledge_source_id": str(ks.id),
                "tenant_id": current_tenant.id,
                "tenant_name": tenant_name,
                "chatbot_id": str(ks.chatbot_id),
                "chatbot_name": chatbot_name,
                "source_type": ks.source_type.value,
                "source_url": ks.source_url,
                "status": ks.status.value,
                "severity": incident_severity,
                "message": message,
                "pages_found": ks.pages_found or 0,
                "created_at": ks.created_at.isoformat() if ks.created_at else None,
                "updated_at": ks.updated_at.isoformat() if ks.updated_at else None,
                "last_crawl_status": last_crawl_status,
                "last_crawl_completed_at": last_crawl_completed_at,
            }
        )

    return {"incidents": incidents, "total": len(incidents)}


# ============== Crawl Notifications (Persistent) ==============


@router.get("/{chatbot_id}/notifications")
async def get_notifications(
    chatbot_id: UUID,
    unread_only: bool = Query(True, description="Only return unread notifications"),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get persistent crawl notifications for a chatbot.
    Returns unread notifications by default so the frontend can display
    them as banners/toasts even if the user was away when the event happened.
    """
    from app.services.notification_service import (
        get_unread_notifications,
        get_all_notifications,
    )

    if unread_only:
        notifications = await get_unread_notifications(chatbot_id, db, limit)
    else:
        notifications = await get_all_notifications(chatbot_id, db, limit)

    return {
        "notifications": [
            {
                "id": str(n.id),
                "knowledge_source_id": str(n.knowledge_source_id),
                "notification_type": n.notification_type,
                "message": n.message,
                "severity": n.severity,
                "is_read": n.is_read,
                "created_at": n.created_at.isoformat() if n.created_at else None,
            }
            for n in notifications
        ],
        "total": len(notifications),
    }


@router.post("/{chatbot_id}/notifications/mark-read")
async def mark_notifications_read(
    chatbot_id: UUID,
    notification_ids: List[str] = Query(
        None, description="Specific notification IDs to mark read"
    ),
    mark_all: bool = Query(False, description="Mark all notifications read"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mark notifications as read. Either provide specific IDs or set mark_all=true.
    """
    from app.services.notification_service import (
        mark_notifications_read as _mark_read,
        mark_all_read_for_chatbot,
    )

    if mark_all:
        count = await mark_all_read_for_chatbot(chatbot_id, db)
    elif notification_ids:
        count = await _mark_read(notification_ids, db)
    else:
        count = 0

    return {"marked_read": count}

