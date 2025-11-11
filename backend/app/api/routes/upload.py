"""File upload endpoint routes"""

import logging
import uuid

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.agents.chart_agent import analyze_chart_request
from app.config.settings import settings
from app.models.schemas import UploadResponse
from app.services.chart_generator import chart_generator
from app.services.excel_parser import excel_parser
from app.services.persistence import persistence

router = APIRouter()
logger = logging.getLogger(__name__)

# Maximum file size: 10MB
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes


@router.post("/upload", response_model=UploadResponse)
async def upload_excel(file: UploadFile = File(...), session_id: str = Form(...)):
    """
    Upload an Excel file and generate a chart from it

    Args:
        file: Excel file upload
        session_id: Session ID for style preferences

    Returns:
        UploadResponse with chart URL
    """
    try:
        # Validate file type
        if not file.filename.endswith((".xlsx", ".xls")):
            logger.warning("Invalid file type uploaded: %s", file.filename)
            raise HTTPException(
                status_code=400, detail="Only Excel files (.xlsx, .xls) are supported"
            )

        # Read file content and check size
        content = await file.read()
        file_size = len(content)

        if file_size > MAX_FILE_SIZE:
            logger.warning("File too large: %s bytes (max %s)", file_size, MAX_FILE_SIZE)
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB",
            )

        logger.info("Received file upload: %s (%d bytes)", file.filename, file_size)

        # Update session last used
        persistence.update_last_used(session_id)

        # Add upload action to history with metadata
        persistence.add_to_chat_history(
            session_id,
            "user",
            f"Uploaded Excel file: {file.filename}",
            metadata={"type": "file_upload", "filename": file.filename, "file_size": file_size},
        )

        # Save uploaded file temporarily
        temp_path = settings.DATA_DIR / f"temp_{uuid.uuid4()}_{file.filename}"

        try:
            with open(temp_path, "wb") as f:
                f.write(content)

            # Parse the Excel file
            parsed = excel_parser.parse_excel(temp_path)

            if not parsed["success"]:
                logger.warning("Failed to parse Excel file: %s", parsed.get("error"))
                return UploadResponse(
                    response=f"Error reading Excel file: {parsed.get('error', 'Unknown error')}",
                    chart_url=None,
                    chart_id=None,
                    color_scheme=None,
                )

            # Try auto-detection first
            auto_data = None
            if "dataframe" in parsed:
                auto_data = excel_parser.auto_detect_chart_data(
                    parsed["dataframe"], filename=file.filename
                )

            # Get style preference from session
            session_style = persistence.get_style_preference(session_id)

            # If auto-detection worked, use it
            if auto_data:
                chart_type = auto_data.get("chart_type", "bar")
                logger.info("Auto-detected chart type: %s", chart_type)

                # For auto-detected data, use session style or persistent memory
                style = session_style or persistence.get_persistent_color_scheme() or "fd"

                result = chart_generator.generate_both_formats(
                    chart_type=chart_type,
                    x_labels=auto_data["x_labels"],
                    y_values=auto_data["y_values"],
                    title=f"Chart from {file.filename}",
                    x_label=auto_data.get("x_label"),
                    y_label=auto_data.get("y_label"),
                    style=style,
                )

                chart_id = result["png"][0]
                response_text = f"I've created a chart from your Excel file!"

                # Add assistant response to history
                persistence.add_to_chat_history(
                    session_id,
                    "assistant",
                    response_text,
                    metadata={
                        "chart_id": chart_id,
                        "chart_type": chart_type,
                        "x_labels": auto_data["x_labels"],
                        "y_values": auto_data["y_values"],
                        "source": "excel_auto_detect",
                    },
                )

                return UploadResponse(
                    response=response_text,
                    chart_url=f"/charts/{chart_id}.png",
                    chart_id=chart_id,
                    color_scheme=style,
                )
            else:
                # Fall back to AI agent to interpret the data
                logger.info("Auto-detection failed, using AI agent to interpret data")
                conversation_history = persistence.get_chat_history(session_id)

                chart_data = await analyze_chart_request(
                    f"Create a chart from this Excel data:\n{parsed['text']}", conversation_history
                )

                if (
                    chart_data.is_valid
                    and chart_data.chart_type
                    and chart_data.x_labels
                    and chart_data.y_values
                ):
                    # Determine color scheme: agent's decision > session > persistent memory > default
                    style = (
                        chart_data.color_scheme
                        or session_style
                        or persistence.get_persistent_color_scheme()
                        or "fd"
                    )

                    # If agent decided on a color scheme, persist it
                    if chart_data.color_scheme:
                        persistence.set_persistent_color_scheme(chart_data.color_scheme)
                        logger.info("Agent selected color scheme: %s", chart_data.color_scheme)

                    result = chart_generator.generate_both_formats(
                        chart_type=chart_data.chart_type,
                        x_labels=chart_data.x_labels,
                        y_values=chart_data.y_values,
                        title=chart_data.title or f"Chart from {file.filename}",
                        x_label=chart_data.x_label,
                        y_label=chart_data.y_label,
                        style=style,
                    )

                    chart_id = result["png"][0]
                    response_text = (
                        f"I've created a {chart_data.chart_type} chart from your Excel file!"
                    )

                    # Add assistant response to history
                    persistence.add_to_chat_history(
                        session_id,
                        "assistant",
                        response_text,
                        metadata={
                            "chart_id": chart_id,
                            "chart_type": chart_data.chart_type,
                            "x_labels": chart_data.x_labels,
                            "y_values": chart_data.y_values,
                            "source": "excel_ai_interpret",
                        },
                    )

                    return UploadResponse(
                        response=response_text,
                        chart_url=f"/charts/{chart_id}.png",
                        chart_id=chart_id,
                        color_scheme=style,
                    )
                else:
                    error_text = "I couldn't automatically determine how to chart this data. The Excel file should have clear columns with labels and numeric values."

                    # Add error to history
                    persistence.add_to_chat_history(session_id, "assistant", error_text)

                    return UploadResponse(
                        response=error_text, chart_url=None, chart_id=None, color_scheme=None
                    )

        finally:
            # Clean up temp file
            if temp_path.exists():
                temp_path.unlink()
                logger.debug("Cleaned up temporary file: %s", temp_path)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error in upload endpoint: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
