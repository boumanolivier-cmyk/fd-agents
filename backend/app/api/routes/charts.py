"""Chart retrieval endpoint routes"""

import logging
from typing import Literal

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.config.settings import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/charts/{chart_id}.{format}")
async def get_chart(chart_id: str, format: Literal["png", "svg"]):
    """
    Download a generated chart

    Args:
        chart_id: UUID of the chart
        format: File format (png or svg)

    Returns:
        FileResponse with the chart file
    """
    file_path = settings.CHARTS_DIR / f"{chart_id}.{format}"

    if not file_path.exists():
        logger.warning("Chart not found: %s", file_path)
        raise HTTPException(status_code=404, detail="Chart not found")

    media_type = "image/png" if format == "png" else "image/svg+xml"

    logger.debug("Serving chart: %s.%s", chart_id, format)
    return FileResponse(file_path, media_type=media_type, filename=f"chart.{format}")
