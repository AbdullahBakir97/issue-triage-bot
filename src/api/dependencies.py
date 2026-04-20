"""Dependency injection for API routes."""

from __future__ import annotations

from functools import lru_cache

from src.application.webhook_handler import WebhookHandler
from src.container import Container
from src.infrastructure.github.webhook import WebhookVerifier

__all__ = ["get_webhook_handler", "get_webhook_verifier"]


@lru_cache(maxsize=1)
def get_container() -> Container:
    """Get the application container singleton."""
    return Container()


def get_webhook_handler() -> WebhookHandler:
    """Get the webhook handler from the container."""
    container = get_container()
    return container.webhook_handler


def get_webhook_verifier() -> WebhookVerifier | None:
    """Get the webhook verifier from the container."""
    container = get_container()
    return container.webhook_verifier
