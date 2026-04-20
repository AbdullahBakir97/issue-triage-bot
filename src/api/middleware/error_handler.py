"""Global error handlers for the API."""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.domain.exceptions import (
    GitHubClientError,
    TriageBotError,
    WebhookValidationError,
)

__all__ = ["register_error_handlers"]

logger = logging.getLogger(__name__)


def register_error_handlers(app: FastAPI) -> None:
    """Register global exception handlers on the FastAPI application."""

    @app.exception_handler(WebhookValidationError)
    async def webhook_validation_handler(
        request: Request, exc: WebhookValidationError
    ) -> JSONResponse:
        """Handle webhook validation errors with 401."""
        logger.warning("Webhook validation failed: %s", exc)
        return JSONResponse(
            status_code=401,
            content={"error": "webhook_validation_failed", "message": str(exc)},
        )

    @app.exception_handler(GitHubClientError)
    async def github_client_handler(request: Request, exc: GitHubClientError) -> JSONResponse:
        """Handle GitHub API errors with 502."""
        logger.error("GitHub API error: %s", exc)
        return JSONResponse(
            status_code=502,
            content={"error": "github_api_error", "message": str(exc)},
        )

    @app.exception_handler(TriageBotError)
    async def triage_bot_handler(request: Request, exc: TriageBotError) -> JSONResponse:
        """Handle general triage bot errors with 500."""
        logger.error("Triage bot error: %s", exc)
        return JSONResponse(
            status_code=500,
            content={"error": "internal_error", "message": str(exc)},
        )

    @app.exception_handler(Exception)
    async def general_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle unexpected errors with 500."""
        logger.exception("Unexpected error: %s", exc)
        return JSONResponse(
            status_code=500,
            content={"error": "unexpected_error", "message": "An internal error occurred"},
        )
