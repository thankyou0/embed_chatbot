from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.members import router as members_router
from app.api.v1.chatbots import router as chatbots_router
from app.api.v1.chat import router as chat_router
from app.api.v1.billing import router as billing_router
from app.api.v1.usage import router as usage_router
from app.api.v1.endpoints.crawl_preview import router as crawl_preview_router

api_router = APIRouter()

# Include routers
api_router.include_router(auth_router)
api_router.include_router(members_router)
api_router.include_router(chatbots_router)
api_router.include_router(chat_router)
api_router.include_router(billing_router)
api_router.include_router(usage_router)
api_router.include_router(crawl_preview_router, prefix="/crawl", tags=["crawl-preview"])


@api_router.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Chatbot API v1"}

