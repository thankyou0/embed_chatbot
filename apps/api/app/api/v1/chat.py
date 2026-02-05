from fastapi import APIRouter, Depends, HTTPException, Request, Form, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional
from app.core.database import get_db
from app.schemas.chat import ChatMessageRequest, ChatMessageResponse, ReportMessageRequest
from app.schemas.appearance import WidgetConfigResponse
from app.services.chat_service import ChatService
from app.services.chatbot_service import ChatbotService
from app.services.analytics_service import AnalyticsService
from app.core.error_sanitizer import sanitize_error_message
import time
import json
from collections import defaultdict

router = APIRouter(prefix="/chat", tags=["chat"])

# Simple in-memory rate limiting: IP -> [timestamps]
rate_limits = defaultdict(list)

# Max image size: 10MB
MAX_IMAGE_SIZE = 10 * 1024 * 1024
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}


def check_rate_limit(request: Request):
    ip = request.client.host
    now = time.time()
    # Filter out timestamps older than 60 seconds
    rate_limits[ip] = [t for t in rate_limits[ip] if now - t < 60]
    
    if len(rate_limits[ip]) >= 30:
        raise HTTPException(status_code=429, detail="Too many requests. Please wait a minute.")
    
    rate_limits[ip].append(now)


@router.post("/{chatbot_id}/message/stream")
async def send_message_stream(
    chatbot_id: UUID,
    req: Request,
    db: AsyncSession = Depends(get_db),
    message: Optional[str] = Form(None),
    session_id: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    is_preview: bool = Form(False)
):
    """
    Public endpoint for chatbot messages with SSE streaming support.
    
    Streams the response as Server-Sent Events for progressive rendering.
    
    Accepts multipart form data:
    - message: The user's text message (required)
    - session_id: Optional session ID for conversation continuity
    - image: Optional image file for visual search
    - is_preview: Whether this is a preview chat (default: false)
    
    No authentication required.
    Rate limited to 30 requests/minute per IP.
    """
    # Rate limiting
    check_rate_limit(req)
    
    # Process image if provided
    image_bytes = None
    if image:
        # Validate content type
        if image.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid image type. Allowed: {', '.join(ALLOWED_IMAGE_TYPES)}"
            )
        
        # Read and validate size
        image_bytes = await image.read()
        if len(image_bytes) > MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Image too large. Max size: {MAX_IMAGE_SIZE // (1024*1024)}MB"
            )
    
    async def event_generator():
        try:
            async for chunk in ChatService.get_response_stream(
                db=db,
                chatbot_id=chatbot_id,
                message=message,
                session_id=session_id,
                image_bytes=image_bytes,
                is_preview=is_preview
            ):
                yield f"data: {json.dumps(chunk)}\n\n"
        except Exception as e:
            public_error = sanitize_error_message(
                str(e),
                fallback="Something went wrong. Please try again."
            )
            error_chunk = {
                "type": "error",
                "error": public_error
            }
            yield f"data: {json.dumps(error_chunk)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )


@router.get("/{chatbot_id}/config", response_model=WidgetConfigResponse)
async def get_widget_config(
    chatbot_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Public endpoint for widget configuration.
    No authentication required.
    Returns appearance settings for the chatbot widget.
    """
    try:
        config = await ChatbotService.get_widget_config(
            db=db,
            chatbot_id=chatbot_id
        )
        return config
    except Exception as e:
        detail = sanitize_error_message(
            str(e),
            fallback="Chatbot not found."
        )
        raise HTTPException(status_code=404, detail=detail)


@router.post("/{chatbot_id}/report", status_code=204)
async def report_message(
    chatbot_id: UUID,
    request: ReportMessageRequest,
    req: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Public endpoint for reporting unsatisfactory bot responses.
    
    Allows users to flag answers they're not satisfied with.
    These will appear in analytics under 'Reported' queries.
    
    No authentication required.
    Rate limited to 30 requests/minute per IP.
    """
    # Rate limiting
    check_rate_limit(req)
    
    try:
        await AnalyticsService.report_message(
            db=db,
            chatbot_id=chatbot_id,
            session_id=request.session_id,
            message_content=request.message_content
        )
    except Exception as e:
        detail = sanitize_error_message(
            str(e),
            fallback="Unable to report the message. Please try again."
        )
        raise HTTPException(status_code=400, detail=detail)

