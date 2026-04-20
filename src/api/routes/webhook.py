"""Webhook route for receiving GitHub events."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Header, Request

from src.api.dependencies import get_webhook_handler, get_webhook_verifier
from src.domain.exceptions import WebhookValidationError

__all__ = ["router"]

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/webhook", status_code=200)
async def handle_webhook(
    request: Request,
    x_hub_signature_256: str | None = Header(default=None),
    x_github_event: str | None = Header(default=None),
) -> dict[str, Any]:
    """Handle incoming GitHub webhook events.

    Verifies the webhook signature and routes the event
    to the appropriate handler.
    """
    body = await request.body()

    # Verify signature
    verifier = get_webhook_verifier()
    if verifier:
        try:
            verifier.verify(body, x_hub_signature_256 or "")
        except WebhookValidationError as exc:
            logger.warning("Webhook verification failed: %s", exc)
            return {"status": "error", "message": "Invalid signature"}

    # Parse payload
    payload = await request.json()

    # Route event
    if x_github_event == "issues":
        handler = get_webhook_handler()
        result = await handler.handle_issue_event(payload)
        if result:
            return {
                "status": "processed",
                "category": result.category.value,
                "priority": result.priority.value,
                "actions": [a.value for a in result.actions],
            }
        return {"status": "skipped", "reason": "Event not actionable"}

    if x_github_event == "ping":
        return {"status": "ok", "message": "pong"}

    return {"status": "ignored", "event": x_github_event}
