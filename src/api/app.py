"""FastAPI application factory."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from src.api.middleware.error_handler import register_error_handlers
from src.api.middleware.logging import LoggingMiddleware
from src.api.routes import analyze, health, webhook

__all__ = ["create_app"]


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Includes:
    - CORS middleware
    - Logging middleware
    - Error handlers
    - Route registration
    - Static file serving for dashboard
    """
    app = FastAPI(
        title="Issue Triage Bot",
        description="Auto-categorizes, labels, and routes GitHub issues",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(LoggingMiddleware)

    # Error handlers
    register_error_handlers(app)

    # Routes
    app.include_router(health.router, tags=["health"])
    app.include_router(webhook.router, prefix="/api", tags=["webhook"])
    app.include_router(analyze.router, prefix="/api", tags=["analyze"])

    # Dashboard static files
    app.mount("/dashboard", StaticFiles(directory="dashboard", html=True), name="dashboard")

    @app.get("/", include_in_schema=False)
    async def root_redirect() -> RedirectResponse:
        """Redirect root to dashboard."""
        return RedirectResponse(url="/dashboard")

    return app
