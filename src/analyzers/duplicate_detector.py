"""Keyword overlap-based duplicate detection."""

from __future__ import annotations

import re
from typing import Any

from src.domain.entities import IssueContext
from src.domain.interfaces import IDuplicateDetector

__all__ = ["KeywordOverlapDuplicateDetector"]

STOP_WORDS: set[str] = {
    "a",
    "an",
    "the",
    "is",
    "it",
    "to",
    "in",
    "for",
    "on",
    "with",
    "at",
    "by",
    "from",
    "as",
    "of",
    "and",
    "or",
    "but",
    "not",
    "be",
    "are",
    "was",
    "were",
    "been",
    "being",
    "have",
    "has",
    "had",
    "do",
    "does",
    "did",
    "will",
    "would",
    "could",
    "should",
    "may",
    "might",
    "can",
    "this",
    "that",
    "these",
    "those",
    "i",
    "we",
    "you",
    "he",
    "she",
    "they",
    "me",
    "us",
    "him",
    "her",
    "them",
    "my",
    "our",
    "your",
    "his",
    "its",
    "their",
    "what",
    "which",
    "who",
    "whom",
    "when",
    "where",
    "how",
    "all",
    "each",
    "every",
    "both",
    "few",
    "more",
    "most",
    "other",
    "some",
    "such",
    "no",
    "nor",
    "only",
    "same",
    "so",
    "than",
    "too",
    "very",
    "just",
    "if",
    "then",
}


class KeywordOverlapDuplicateDetector(IDuplicateDetector):
    """Detects duplicate issues using keyword overlap analysis."""

    def __init__(self, threshold: float = 0.6) -> None:
        """Initialize with overlap threshold (default 60%)."""
        self._threshold = threshold

    async def find_duplicates(
        self, context: IssueContext, recent_issues: list[dict[str, Any]]
    ) -> int | None:
        """Find potential duplicate by comparing keyword overlap.

        Returns the issue number of the best match if overlap exceeds
        the threshold, otherwise None.
        """
        source_keywords = self._extract_keywords(context.full_text)
        if not source_keywords:
            return None

        best_match: int | None = None
        best_score: float = 0.0

        for issue in recent_issues:
            issue_number = issue.get("number", 0)
            if issue_number == context.issue_number:
                continue

            issue_text = f"{issue.get('title', '')} {issue.get('body', '')}"
            candidate_keywords = self._extract_keywords(issue_text)

            if not candidate_keywords:
                continue

            overlap = source_keywords & candidate_keywords
            union = source_keywords | candidate_keywords
            score = len(overlap) / len(union) if union else 0.0

            if score > best_score:
                best_score = score
                best_match = issue_number

        if best_score >= self._threshold:
            return best_match

        return None

    @staticmethod
    def _extract_keywords(text: str) -> set[str]:
        """Extract meaningful keywords from text, filtering stop words."""
        words = re.findall(r"[a-z]+", text.lower())
        return {w for w in words if len(w) > 2 and w not in STOP_WORDS}
