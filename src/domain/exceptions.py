"""Domain exceptions for Issue Triage Bot."""

__all__ = [
    "TriageBotError",
    "CategoryDetectionError",
    "PriorityDetectionError",
    "GitHubClientError",
    "ConfigurationError",
    "WebhookValidationError",
]


class TriageBotError(Exception):
    """Base exception for Issue Triage Bot."""


class CategoryDetectionError(TriageBotError):
    """Raised when category detection fails."""


class PriorityDetectionError(TriageBotError):
    """Raised when priority detection fails."""


class GitHubClientError(TriageBotError):
    """Raised when GitHub API operations fail."""


class ConfigurationError(TriageBotError):
    """Raised when configuration is invalid or missing."""


class WebhookValidationError(TriageBotError):
    """Raised when webhook signature validation fails."""
