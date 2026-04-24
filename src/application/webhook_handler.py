"""Webhook event handler for GitHub issue events."""

from __future__ import annotations

import logging
from typing import Any

from src.application.orchestrator import TriageOrchestrator
from src.domain.entities import IssueContext, TriageResult

__all__ = ["WebhookHandler"]

logger = logging.getLogger(__name__)

SUPPORTED_ACTIONS = {"opened", "edited"}


class WebhookHandler:
    """Handles incoming GitHub webhook events for issues."""

    def __init__(self, orchestrator: TriageOrchestrator) -> None:
        """Initialize with the triage orchestrator."""
        self._orchestrator = orchestrator

    async def handle_issue_event(self, payload: dict[str, Any]) -> TriageResult | None:
        """Handle an issues webhook event.

        Processes issues.opened and issues.edited events.
        Returns the triage result or None if the event is not handled.
        """
        action = payload.get("action", "")

        if action not in SUPPORTED_ACTIONS:
            logger.debug("Ignoring issue event with action: %s", action)
            return None

        issue = payload.get("issue", {})
        repository = payload.get("repository", {})

        if issue.get("pull_request"):
            logger.debug("Ignoring pull request event")
            return None

        # Set installation ID dynamically from the webhook payload
        installation_id = payload.get("installation", {}).get("id")
        if installation_id and hasattr(self._orchestrator, "_github_client"):
            self._orchestrator._github_client._installation_id = installation_id

        context = IssueContext(
            issue_number=issue.get("number", 0),
            title=issue.get("title", ""),
            body=issue.get("body", "") or "",
            author=issue.get("user", {}).get("login", ""),
            repo_owner=repository.get("owner", {}).get("login", ""),
            repo_name=repository.get("name", ""),
            labels=[label.get("name", "") for label in issue.get("labels", [])],
            is_pull_request=False,
        )

        logger.info(
            "Processing %s event for issue #%d in %s",
            action,
            context.issue_number,
            context.repo_full_name,
        )

        return await self._orchestrator.triage(context)
