"""Keyword-based priority detection."""

from __future__ import annotations

import re

from src.domain.entities import IssueContext
from src.domain.enums import IssueCategory, Priority
from src.domain.interfaces import IPriorityDetector

__all__ = ["KeywordPriorityDetector"]

PRIORITY_KEYWORDS: dict[Priority, list[str]] = {
    Priority.P0: [
        "security",
        "vulnerability",
        "data loss",
        "data leak",
        "exploit",
        "cve",
        "critical",
        "urgent",
        "emergency",
        "production down",
        "outage",
    ],
    Priority.P1: [
        "crash",
        "blocking",
        "regression",
        "blocker",
        "cannot use",
        "unusable",
        "severe",
        "major",
        "deadlock",
        "memory leak",
        "data corruption",
    ],
    Priority.P2: [
        "bug",
        "error",
        "broken",
        "incorrect",
        "wrong",
        "unexpected behavior",
        "inconsistent",
        "fails",
        "not working",
    ],
    Priority.P3: [
        "minor",
        "cosmetic",
        "low priority",
        "nice to have",
        "visual",
        "alignment",
        "formatting",
        "style",
        "polish",
    ],
    Priority.P4: [
        "question",
        "docs",
        "documentation",
        "typo",
        "suggestion",
        "idea",
        "discussion",
        "opinion",
        "feedback",
    ],
}

CATEGORY_BASE_PRIORITY: dict[IssueCategory, Priority] = {
    IssueCategory.BUG: Priority.P2,
    IssueCategory.FEATURE: Priority.P3,
    IssueCategory.QUESTION: Priority.P4,
    IssueCategory.DOCS: Priority.P4,
    IssueCategory.ENHANCEMENT: Priority.P3,
    IssueCategory.SUPPORT: Priority.P3,
    IssueCategory.UNKNOWN: Priority.P3,
}


class KeywordPriorityDetector(IPriorityDetector):
    """Detects issue priority based on keyword analysis."""

    def __init__(
        self,
        keywords: dict[Priority, list[str]] | None = None,
        category_defaults: dict[IssueCategory, Priority] | None = None,
    ) -> None:
        """Initialize with optional custom keyword and category mappings."""
        self._keywords = keywords or PRIORITY_KEYWORDS
        self._category_defaults = category_defaults or CATEGORY_BASE_PRIORITY

    async def detect_priority(self, context: IssueContext, category: IssueCategory) -> Priority:
        """Detect priority using keyword matching with category as baseline.

        Keywords can override the category-based default priority.
        Higher-severity keywords always take precedence.
        """
        text = context.full_text.lower()
        detected_priority: Priority | None = None

        for priority in [Priority.P0, Priority.P1, Priority.P2, Priority.P3, Priority.P4]:
            keywords = self._keywords.get(priority, [])
            for keyword in keywords:
                pattern = re.escape(keyword)
                if re.search(pattern, text):
                    detected_priority = priority
                    break
            if detected_priority is not None:
                break

        base_priority = self._category_defaults.get(category, Priority.P3)

        if detected_priority is None:
            return base_priority

        # Return the higher severity (lower number) priority
        return min(detected_priority, base_priority, key=lambda p: int(p.value[1]))
