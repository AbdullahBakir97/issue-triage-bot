"""Domain interfaces (ports) for Issue Triage Bot."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from src.domain.entities import IssueContext
from src.domain.enums import IssueCategory, Priority

__all__ = [
    "ICategorizer",
    "IPriorityDetector",
    "ICompletenessChecker",
    "IDuplicateDetector",
    "IGitHubClient",
    "IConfigLoader",
]


class ICategorizer(ABC):
    """Interface for issue categorization."""

    @abstractmethod
    async def categorize(self, context: IssueContext) -> tuple[IssueCategory, float]:
        """Categorize an issue and return category with confidence score."""


class IPriorityDetector(ABC):
    """Interface for priority detection."""

    @abstractmethod
    async def detect_priority(self, context: IssueContext, category: IssueCategory) -> Priority:
        """Detect priority level for an issue."""


class ICompletenessChecker(ABC):
    """Interface for issue completeness checking."""

    @abstractmethod
    async def check_completeness(
        self, context: IssueContext, category: IssueCategory
    ) -> tuple[float, list[str]]:
        """Check issue completeness, return score and missing sections."""


class IDuplicateDetector(ABC):
    """Interface for duplicate issue detection."""

    @abstractmethod
    async def find_duplicates(
        self, context: IssueContext, recent_issues: list[dict[str, Any]]
    ) -> int | None:
        """Find potential duplicate issues. Returns issue number or None."""


class IGitHubClient(ABC):
    """Interface for GitHub API operations."""

    @abstractmethod
    async def post_comment(self, repo: str, issue_number: int, body: str) -> None:
        """Post a comment on an issue."""

    @abstractmethod
    async def add_labels(self, repo: str, issue_number: int, labels: list[str]) -> None:
        """Add labels to an issue."""

    @abstractmethod
    async def assign_issue(self, repo: str, issue_number: int, assignees: list[str]) -> None:
        """Assign users to an issue."""

    @abstractmethod
    async def get_recent_issues(self, repo: str, limit: int = 50) -> list[dict[str, Any]]:
        """Get recent issues from the repository."""

    @abstractmethod
    async def close_issue(self, repo: str, issue_number: int) -> None:
        """Close an issue."""

    @abstractmethod
    async def get_file_content(self, repo: str, path: str) -> str | None:
        """Get file content from the repository."""


class IConfigLoader(ABC):
    """Interface for loading bot configuration."""

    @abstractmethod
    async def load_config(self, repo: str) -> dict[str, Any]:
        """Load triage bot configuration for a repository."""
