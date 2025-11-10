"""User preferences endpoint routes"""
import logging
from fastapi import APIRouter, HTTPException

from app.models.schemas import StylePreference
from app.services.persistence import persistence

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/preferences/{session_id}")
async def get_preferences(session_id: str):
    """Get style preferences for a session"""
    try:
        style = persistence.get_style_preference(session_id)
        logger.debug("Retrieved preferences for session %s: %s", session_id, style)
        return {"style": style}
    except Exception as e:
        logger.error("Failed to get preferences: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/preferences/{session_id}")
async def set_preferences(session_id: str, preference: StylePreference):
    """Set style preferences for a session"""
    try:
        persistence.set_style_preference(session_id, preference.style)
        logger.info("Updated preferences for session %s: %s", session_id, preference.style)
        return {"success": True, "style": preference.style}
    except Exception as e:
        logger.error("Failed to set preferences: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
