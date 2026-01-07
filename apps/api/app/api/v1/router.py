from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.members import router as members_router
from app.api.v1.chatbots import router as chatbots_router
from app.api.v1.chat import router as chat_router

api_router = APIRouter()

# Include routers
api_router.include_router(auth_router)
api_router.include_router(members_router)
api_router.include_router(chatbots_router)
api_router.include_router(chat_router)


@api_router.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Chatbot API v1"}

