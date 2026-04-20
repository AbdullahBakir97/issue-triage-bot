"""API request and response schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field

__all__ = ["AnalyzeRequest", "AnalyzeResponse"]


class AnalyzeRequest(BaseModel):
    """Request body for the demo analyze endpoint."""

    title: str = Field(..., description="Issue title", min_length=1)
    body: str = Field(default="", description="Issue body/description")


class AnalyzeResponse(BaseModel):
    """Response from the analyze endpoint."""

    category: str = Field(..., description="Detected issue category")
    priority: str = Field(..., description="Detected priority level")
    confidence: float = Field(..., description="Confidence score 0.0-1.0")
    completeness_score: float = Field(..., description="Completeness score 0.0-1.0")
    missing_sections: list[str] = Field(
        default_factory=list, description="Missing required sections"
    )
