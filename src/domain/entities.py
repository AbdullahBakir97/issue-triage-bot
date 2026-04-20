"""Domain entities for Issue Triage Bot."""

from __future__ import annotations

from dataclasses import dataclass, field

from src.domain.enums import IssueCategory, Priority, TriageAction

__all__ = ["TriageResult", "IssueContext"]


@dataclass
class IssueContext:
    """Context information about a GitHub issue."""

    issue_number: int
    title: str
    body: str
    author: str
    repo_owner: str
    repo_name: str
    labels: list[str] = field(default_factory=list)
    is_pull_request: bool = False

    @property
    def full_text(self) -> str:
        """Combine title and body for analysis."""
        return f"{self.title}\n{self.body}"

    @property
    def repo_full_name(self) -> str:
        """Get the full repository name."""
        return f"{self.repo_owner}/{self.repo_name}"


@dataclass
class TriageResult:
    """Result of triaging a GitHub issue."""

    category: IssueCategory
    priority: Priority
    confidence: float
    actions: list[TriageAction] = field(default_factory=list)
    labels: list[str] = field(default_factory=list)
    assignees: list[str] = field(default_factory=list)
    comment: str | None = None
    duplicate_of: int | None = None
    completeness_score: float = 1.0
    missing_sections: list[str] = field(default_factory=list)
