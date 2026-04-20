"""Keyword-based issue categorization."""

from __future__ import annotations

import re

from src.domain.entities import IssueContext
from src.domain.enums import IssueCategory
from src.domain.interfaces import ICategorizer

__all__ = ["KeywordCategorizer"]

CATEGORY_KEYWORDS: dict[IssueCategory, list[str]] = {
    IssueCategory.BUG: [
        "bug",
        "crash",
        "error",
        "broken",
        "fail",
        "failure",
        "not working",
        "doesn't work",
        "does not work",
        "unexpected",
        "regression",
        "issue",
        "problem",
        "defect",
        "fix",
    ],
    IssueCategory.FEATURE: [
        "feature",
        "request",
        "add",
        "implement",
        "new",
        "proposal",
        "suggest",
        "enhancement",
        "would be nice",
        "wish",
        "could we",
        "can we",
    ],
    IssueCategory.QUESTION: [
        "how",
        "help",
        "?",
        "wondering",
        "question",
        "what is",
        "what are",
        "where",
        "when",
        "why",
        "confused",
        "clarification",
        "explain",
        "understand",
    ],
    IssueCategory.DOCS: [
        "docs",
        "documentation",
        "readme",
        "typo",
        "spelling",
        "grammar",
        "wiki",
        "guide",
        "tutorial",
        "example",
        "javadoc",
        "docstring",
    ],
    IssueCategory.ENHANCEMENT: [
        "improve",
        "optimize",
        "refactor",
        "performance",
        "better",
        "upgrade",
        "modernize",
        "clean up",
        "speed up",
    ],
    IssueCategory.SUPPORT: [
        "support",
        "assistance",
        "troubleshoot",
        "debug",
        "diagnose",
        "configuration",
        "setup",
        "install",
        "deploy",
    ],
}


class KeywordCategorizer(ICategorizer):
    """Categorizes issues based on keyword matching."""

    def __init__(self, keywords: dict[IssueCategory, list[str]] | None = None) -> None:
        """Initialize with optional custom keyword mappings."""
        self._keywords = keywords or CATEGORY_KEYWORDS

    async def categorize(self, context: IssueContext) -> tuple[IssueCategory, float]:
        """Categorize an issue using keyword frequency analysis.

        Returns a tuple of (category, confidence) where confidence is 0.0-1.0.
        """
        text = context.full_text.lower()
        scores: dict[IssueCategory, int] = {}

        for category, keywords in self._keywords.items():
            score = 0
            for keyword in keywords:
                pattern = re.escape(keyword)
                matches = re.findall(pattern, text)
                score += len(matches)
            if score > 0:
                scores[category] = score

        if not scores:
            return IssueCategory.UNKNOWN, 0.0

        total = sum(scores.values())
        best_category = max(scores, key=lambda c: scores[c])
        confidence = round(scores[best_category] / total, 2) if total > 0 else 0.0

        return best_category, confidence
