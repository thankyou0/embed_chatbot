from fastapi import APIRouter, Depends, HTTPException, Request, Form, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional
from app.core.database import get_db
from app.schemas.chat import ChatMessageRequest, ChatMessageResponse
from app.schemas.appearance import WidgetConfigResponse
from app.services.chat_service import ChatService
from app.services.chatbot_service import ChatbotService
import time
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


@router.post("/{chatbot_id}/message", response_model=ChatMessageResponse)
async def send_message(
    chatbot_id: UUID,
    req: Request,
    db: AsyncSession = Depends(get_db),
    message: Optional[str] = Form(None),
    session_id: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None)
):
    """
    Public endpoint for chatbot messages with optional image upload.
    
    Accepts multipart form data:
    - message: The user's text message (required)
    - session_id: Optional session ID for conversation continuity
    - image: Optional image file for visual search
    
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
    
    try:
        response = await ChatService.get_response(
            db=db,
            chatbot_id=chatbot_id,
            message=message,
            session_id=session_id,
            image_bytes=image_bytes
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


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
        raise HTTPException(status_code=404, detail=str(e))

