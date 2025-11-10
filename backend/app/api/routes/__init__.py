"""API route modules"""
from fastapi import APIRouter
from app.api.routes import chat, upload, charts, preferences

# Create main API router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(chat.router, tags=["chat"])
api_router.include_router(upload.router, tags=["upload"])
api_router.include_router(charts.router, tags=["charts"])
api_router.include_router(preferences.router, tags=["preferences"])

__all__ = ["api_router"]
