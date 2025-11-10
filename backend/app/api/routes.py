"""API routes for chart generation"""
import uuid
import logging
from pathlib import Path
from typing import Literal
from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse

from app.models.schemas import (
    ChatRequest, 
    ChatResponse, 
    UploadResponse, 
    StylePreference
)
from app.agents.chart_agent import analyze_chart_request
from app.services.chart_generator import chart_generator
from app.services.excel_parser import excel_parser
from app.services.persistence import persistence
from app.config.settings import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a chat message and potentially generate a chart
    
    Args:
        request: ChatRequest with message and session_id
    
    Returns:
        ChatResponse with AI response and optional chart URL
    """
    try:
        # Update session last used
        persistence.update_last_used(request.session_id)
        
        # Get style preference
        style = persistence.get_style_preference(request.session_id)
        
        # Get conversation history for context
        conversation_history = persistence.get_chat_history(request.session_id)
        
        # Add user message to history
        persistence.add_to_chat_history(
            request.session_id, 
            "user", 
            request.message
        )
        
        # Analyze the request with the AI agent (with full conversation context)
        chart_data = await analyze_chart_request(request.message, conversation_history)
        
        # Log raw ChartData from agent for troubleshooting
        logger.debug(
            "Agent returned ChartData: is_valid=%s, chart_type=%s, x_labels=%s, y_values=%s, reason=%s",
            chart_data.is_valid, chart_data.chart_type, chart_data.x_labels, 
            chart_data.y_values, chart_data.reason
        )
        
        # Normalise agent output:
        # - If chart_type missing but x_labels+y_values present, infer sensible default
        # - Coerce y_values to floats
        x_labels = chart_data.x_labels or []
        y_values = chart_data.y_values or []
        chart_type = chart_data.chart_type

        if x_labels and y_values and not chart_type:
            # Fallback: prefer line for longer/sequential data, else bar
            chart_type = "line" if len(x_labels) >= 10 else "bar"
            logger.info("Inferred chart_type='%s' from %d x_labels", chart_type, len(x_labels))

        # Try to coerce y_values to floats (agent may return numbers as strings)
        coerced_y = []
        if y_values:
            try:
                for v in y_values:
                    coerced_y.append(float(v))
            except Exception as e:
                # If coercion fails, return a helpful response
                logger.warning("Failed to coerce y_values to floats: %s", e)
                error_msg = "I couldn't interpret the numeric values for the chart. Please provide numbers for the y-axis."
                persistence.add_to_chat_history(request.session_id, "assistant", error_msg)
                return ChatResponse(response=error_msg, chart_url=None, chart_id=None)
        
        # If not a valid chart request, return refusal
        if not chart_data.is_valid:
            response_text = chart_data.reason or "I can only help you create bar or line charts. Please ask me to make a chart with some data!"
            
            # Add assistant response to history
            persistence.add_to_chat_history(
                request.session_id,
                "assistant",
                response_text
            )
            
            return ChatResponse(
                response=response_text,
                chart_url=None,
                chart_id=None
            )
        
        # If valid and we have data, generate chart (use inferred/coerced values)
        if chart_type and x_labels and coerced_y:
            try:
                result = chart_generator.generate_both_formats(
                    chart_type=chart_type,
                    x_labels=x_labels,
                    y_values=coerced_y,
                    title=chart_data.title or "Chart",
                    x_label=chart_data.x_label,
                    y_label=chart_data.y_label,
                    style=style
                )
                
                chart_id = result["png"][0]
                response_text = f"I've created a {chart_type} chart for you!"
                
                # Add assistant response to history with chart metadata
                persistence.add_to_chat_history(
                    request.session_id,
                    "assistant",
                    response_text,
                    metadata={
                        "chart_id": chart_id,
                        "chart_type": chart_type,
                        "x_labels": x_labels,
                        "y_values": coerced_y,
                        "title": chart_data.title
                    }
                )
                
                return ChatResponse(
                    response=response_text,
                    chart_url=f"/charts/{chart_id}.png",
                    chart_id=chart_id
                )
            except Exception as e:
                error_text = f"I understood your request, but encountered an error generating the chart: {str(e)}"
                
                # Add error to history
                persistence.add_to_chat_history(
                    request.session_id,
                    "assistant",
                    error_text
                )
                
                return ChatResponse(
                    response=error_text,
                    chart_url=None,
                    chart_id=None
                )
        else:
            # Graceful fallback if something still missing
            clarification_text = "I understood you want a chart, but I need more information about the data. Could you provide the specific values you want to chart?"
            
            # Add clarification request to history
            persistence.add_to_chat_history(
                request.session_id,
                "assistant",
                clarification_text
            )
            
            return ChatResponse(
                response=clarification_text,
                chart_url=None,
                chart_id=None
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload", response_model=UploadResponse)
async def upload_excel(
    file: UploadFile = File(...),
    session_id: str = Form(...)
):
    """
    Upload an Excel file and generate a chart from it
    
    Args:
        file: Excel file upload
        session_id: Session ID for style preferences
    
    Returns:
        UploadResponse with chart URL
    """
    # Maximum file size: 10MB
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes
    
    try:
        # Validate file type
        if not file.filename.endswith(('.xlsx', '.xls')):
            logger.warning("Invalid file type uploaded: %s", file.filename)
            raise HTTPException(
                status_code=400, 
                detail="Only Excel files (.xlsx, .xls) are supported"
            )
        
        # Read file content and check size
        content = await file.read()
        file_size = len(content)
        
        if file_size > MAX_FILE_SIZE:
            logger.warning("File too large: %s bytes (max %s)", file_size, MAX_FILE_SIZE)
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        logger.info("Received file upload: %s (%d bytes)", file.filename, file_size)
        
        # Update session last used
        persistence.update_last_used(session_id)
        
        # Add upload action to history
        persistence.add_to_chat_history(
            session_id,
            "user",
            f"Uploaded Excel file: {file.filename}"
        )
        
        # Save uploaded file temporarily
        temp_path = settings.DATA_DIR / f"temp_{uuid.uuid4()}_{file.filename}"
        
        try:
            with open(temp_path, "wb") as f:
                f.write(content)
            
            # Parse the Excel file
            parsed = excel_parser.parse_excel(temp_path)
            
            if not parsed["success"]:
                return UploadResponse(
                    response=f"Error reading Excel file: {parsed.get('error', 'Unknown error')}",
                    chart_url=None,
                    chart_id=None
                )
            
            # Try auto-detection first
            auto_data = None
            if "dataframe" in parsed:
                auto_data = excel_parser.auto_detect_chart_data(
                    parsed["dataframe"],
                    filename=file.filename
                )
            
            # Get style preference
            style = persistence.get_style_preference(session_id)
            
            # If auto-detection worked, use it
            if auto_data:
                # Use intelligently determined chart type
                chart_type = auto_data.get("chart_type", "bar")
                
                result = chart_generator.generate_both_formats(
                    chart_type=chart_type,
                    x_labels=auto_data["x_labels"],
                    y_values=auto_data["y_values"],
                    title=f"Chart from {file.filename}",
                    x_label=auto_data.get("x_label"),
                    y_label=auto_data.get("y_label"),
                    style=style
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
                        "source": "excel_auto_detect"
                    }
                )
                
                return UploadResponse(
                    response=response_text,
                    chart_url=f"/charts/{chart_id}.png",
                    chart_id=chart_id
                )
            else:
                # Fall back to AI agent to interpret the data
                # Get conversation history for context
                conversation_history = persistence.get_chat_history(session_id)
                
                chart_data = await analyze_chart_request(
                    f"Create a chart from this Excel data:\n{parsed['text']}",
                    conversation_history
                )
                
                if chart_data.is_valid and chart_data.chart_type and chart_data.x_labels and chart_data.y_values:
                    result = chart_generator.generate_both_formats(
                        chart_type=chart_data.chart_type,
                        x_labels=chart_data.x_labels,
                        y_values=chart_data.y_values,
                        title=chart_data.title or f"Chart from {file.filename}",
                        x_label=chart_data.x_label,
                        y_label=chart_data.y_label,
                        style=style
                    )
                    
                    chart_id = result["png"][0]
                    response_text = f"I've created a {chart_data.chart_type} chart from your Excel file!"
                    
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
                            "source": "excel_ai_interpret"
                        }
                    )
                    
                    return UploadResponse(
                        response=response_text,
                        chart_url=f"/charts/{chart_id}.png",
                        chart_id=chart_id
                    )
                else:
                    error_text = "I couldn't automatically determine how to chart this data. The Excel file should have clear columns with labels and numeric values."
                    
                    # Add error to history
                    persistence.add_to_chat_history(
                        session_id,
                        "assistant",
                        error_text
                    )
                    
                    return UploadResponse(
                        response=error_text,
                        chart_url=None,
                        chart_id=None
                    )
        
        finally:
            # Clean up temp file
            if temp_path.exists():
                temp_path.unlink()
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/preferences/{session_id}")
async def get_preferences(session_id: str):
    """Get style preferences for a session"""
    style = persistence.get_style_preference(session_id)
    return {"style": style}


@router.post("/preferences/{session_id}")
async def set_preferences(session_id: str, preference: StylePreference):
    """Set style preferences for a session"""
    persistence.set_style_preference(session_id, preference.style)
    return {"success": True, "style": preference.style}


@router.delete("/chat/{session_id}")
async def clear_chat_history(session_id: str):
    """Clear chat history for a session"""
    persistence.clear_chat_history(session_id)
    return {"success": True, "message": "Chat history cleared"}


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
        raise HTTPException(status_code=404, detail="Chart not found")
    
    media_type = "image/png" if format == "png" else "image/svg+xml"
    
    return FileResponse(
        file_path,
        media_type=media_type,
        filename=f"chart.{format}"
    )
