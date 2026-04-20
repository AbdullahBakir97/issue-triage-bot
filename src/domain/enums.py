"""Domain enumerations for Issue Triage Bot."""

from enum import StrEnum

__all__ = ["IssueCategory", "Priority", "TriageAction"]


class IssueCategory(StrEnum):
    """Classification categories for GitHub issues."""

    BUG = "bug"
    FEATURE = "feature"
    QUESTION = "question"
    DOCS = "docs"
    ENHANCEMENT = "enhancement"
    SUPPORT = "support"
    UNKNOWN = "unknown"


class Priority(StrEnum):
    """Priority levels for triaged issues."""

    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


class TriageAction(StrEnum):
    """Actions that can be taken during triage."""

    LABEL = "label"
    COMMENT = "comment"
    ASSIGN = "assign"
    CLOSE = "close"
