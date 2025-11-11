"""Pydantic models for request/response schemas"""
from typing import Literal, Optional
from pydantic import BaseModel, Field


class ChartData(BaseModel):
    """Structured chart data extracted by the AI agent"""
    is_valid: bool = Field(description="Whether this is a valid chart request")
    reason: Optional[str] = Field(None, description="Reason for refusal if not valid")
    chart_type: Optional[Literal["bar", "line"]] = Field(None, description="Type of chart to generate")
    title: Optional[str] = Field(None, description="Chart title")
    x_label: Optional[str] = Field(None, description="X-axis label")
    y_label: Optional[str] = Field(None, description="Y-axis label")
    x_labels: Optional[list[str]] = Field(None, description="X-axis category labels")
    y_values: Optional[list[float]] = Field(None, description="Y-axis numerical values")
    color_scheme: Optional[Literal["fd", "bnr"]] = Field(None, description="Color scheme determined by context")


class ChatRequest(BaseModel):
    """Request to chat endpoint"""
    message: str = Field(description="User's message or chart request")
    session_id: str = Field(description="Session ID for tracking preferences")


class ChatResponse(BaseModel):
    """Response from chat endpoint"""
    response: str = Field(description="AI agent's text response")
    chart_url: Optional[str] = Field(None, description="URL to generated chart if applicable")
    chart_id: Optional[str] = Field(None, description="Chart ID for downloading")
    color_scheme: Optional[Literal["fd", "bnr"]] = Field(None, description="Color scheme used for the chart")


class UploadResponse(BaseModel):
    """Response from file upload endpoint"""
    response: str = Field(description="AI agent's text response")
    chart_url: Optional[str] = Field(None, description="URL to generated chart if applicable")
    chart_id: Optional[str] = Field(None, description="Chart ID for downloading")
    color_scheme: Optional[Literal["fd", "bnr"]] = Field(None, description="Color scheme used for the chart")


class StylePreference(BaseModel):
    """User's style preference"""
    style: Literal["fd", "bnr"] = Field(description="Preferred chart style")


class SessionData(BaseModel):
    """Session data stored in persistence"""
    session_id: str
    style: Literal["fd", "bnr"] = "fd"
    created_at: str
    last_used: str
