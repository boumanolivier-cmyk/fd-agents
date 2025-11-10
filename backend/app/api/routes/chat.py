"""Chat endpoint routes"""
import logging
from fastapi import APIRouter, HTTPException

from app.models.schemas import ChatRequest, ChatResponse
from app.agents.chart_agent import analyze_chart_request
from app.services.chart_generator import chart_generator
from app.services.persistence import persistence

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
                logger.error("Chart generation failed: %s", e, exc_info=True)
                
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
        logger.error("Unexpected error in chat endpoint: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/chat/{session_id}")
async def clear_chat_history(session_id: str):
    """Clear chat history for a session"""
    try:
        persistence.clear_chat_history(session_id)
        logger.info("Cleared chat history for session: %s", session_id)
        return {"success": True, "message": "Chat history cleared"}
    except Exception as e:
        logger.error("Failed to clear chat history: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
