"""Health check route."""

from __future__ import annotations

from fastapi import APIRouter

__all__ = ["router"]

router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint for monitoring and load balancers."""
    return {"status": "healthy", "service": "issue-triage-bot"}
