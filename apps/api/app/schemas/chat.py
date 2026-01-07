from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID


class ChatMessageRequest(BaseModel):
    """Request model for JSON-based chat messages (no image)."""
    message: str = Field(..., min_length=1)
    session_id: Optional[str] = None


class ImageAnalysisResult(BaseModel):
    """Result of image analysis from vision model."""
    product_type: str = ""
    category: str = ""
    color: str = ""
    style: str = ""
    other_attributes: str = ""
    confidence: float = 0.0
    needs_clarification: bool = False


class ChatSource(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None


class ChatMessageResponse(BaseModel):
    session_id: str
    message: str
    sources: List[ChatSource] = []
    suggestions: List[str] = []
    image_analysis: Optional[ImageAnalysisResult] = None

