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


class ProductInfo(BaseModel):
    """Product information for display in chat carousel."""
    name: str
    url: str
    price: Optional[str] = None
    currency: Optional[str] = None
    image: Optional[str] = None
    brand: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None


class ChatMessageResponse(BaseModel):
    session_id: str
    message: str
    sources: List[ChatSource] = []
    suggestions: List[str] = []
    image_analysis: Optional[ImageAnalysisResult] = None
    products: List[ProductInfo] = []  # Product carousel data


class ReportMessageRequest(BaseModel):
    """Request model for reporting an unsatisfactory answer."""
    session_id: str = Field(..., description="Session ID of the chat")
    message_content: str = Field(..., min_length=1, description="Content of the user message that got unsatisfactory response")

