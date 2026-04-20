"""Dependency injection container."""

from __future__ import annotations

from src.analyzers.categorizer import KeywordCategorizer
from src.analyzers.completeness_checker import CompletenessChecker
from src.analyzers.duplicate_detector import KeywordOverlapDuplicateDetector
from src.analyzers.priority_detector import KeywordPriorityDetector
from src.analyzers.response_generator import ResponseGenerator
from src.application.orchestrator import TriageOrchestrator
from src.application.webhook_handler import WebhookHandler
from src.config.settings import Settings
from src.generators.comment_builder import CommentBuilder
from src.generators.label_manager import LabelManager
from src.infrastructure.github.auth import GitHubAppAuth
from src.infrastructure.github.client import GitHubClient
from src.infrastructure.github.webhook import WebhookVerifier

__all__ = ["Container"]


class Container:
    """Application dependency container.

    Wires together all components with their dependencies.
    """

    def __init__(self, settings: Settings | None = None) -> None:
        """Initialize the container with application settings."""
        self._settings = settings or Settings()
        self._webhook_handler: WebhookHandler | None = None
        self._webhook_verifier: WebhookVerifier | None = None

    @property
    def settings(self) -> Settings:
        """Get application settings."""
        return self._settings

    @property
    def webhook_verifier(self) -> WebhookVerifier | None:
        """Get the webhook verifier (None if no secret configured)."""
        if self._webhook_verifier is None and self._settings.github_webhook_secret:
            self._webhook_verifier = WebhookVerifier(self._settings.github_webhook_secret)
        return self._webhook_verifier

    @property
    def webhook_handler(self) -> WebhookHandler:
        """Get the webhook handler with all dependencies wired."""
        if self._webhook_handler is None:
            # Auth
            auth = GitHubAppAuth(
                app_id=self._settings.github_app_id,
                private_key=self._settings.github_private_key,
            )

            # GitHub client
            github_client = GitHubClient(
                auth=auth,
                installation_id=self._settings.github_installation_id,
            )

            # Analyzers
            categorizer = KeywordCategorizer()
            priority_detector = KeywordPriorityDetector()
            completeness_checker = CompletenessChecker()
            duplicate_detector = KeywordOverlapDuplicateDetector(
                threshold=self._settings.duplicate_threshold
            )
            response_generator = ResponseGenerator()

            # Generators
            label_manager = LabelManager()
            comment_builder = CommentBuilder()

            # Orchestrator
            orchestrator = TriageOrchestrator(
                categorizer=categorizer,
                priority_detector=priority_detector,
                completeness_checker=completeness_checker,
                duplicate_detector=duplicate_detector,
                github_client=github_client,
                label_manager=label_manager,
                comment_builder=comment_builder,
                response_generator=response_generator,
                auto_label=self._settings.auto_label,
                auto_comment=self._settings.auto_comment,
                auto_assign=self._settings.auto_assign,
            )

            self._webhook_handler = WebhookHandler(orchestrator)

        return self._webhook_handler
