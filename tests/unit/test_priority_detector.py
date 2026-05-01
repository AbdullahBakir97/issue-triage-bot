"""Unit tests for the priority detector."""

from __future__ import annotations

import pytest

from src.analyzers.priority_detector import KeywordPriorityDetector
from src.domain.entities import IssueContext
from src.domain.enums import IssueCategory, Priority


@pytest.fixture
def detector() -> KeywordPriorityDetector:
    """Create a priority detector instance."""
    return KeywordPriorityDetector()


class TestKeywordPriorityDetector:
    """Tests for KeywordPriorityDetector."""

    async def test_security_issue_gets_p0(
        self, detector: KeywordPriorityDetector, security_issue: IssueContext
    ) -> None:
        """Security vulnerabilities should get P0 priority."""
        priority = await detector.detect_priority(security_issue, IssueCategory.BUG)
        assert priority == Priority.P0

    async def test_crash_issue_gets_p1(self, detector: KeywordPriorityDetector) -> None:
        """Crashes and blocking issues should get P1 priority."""
        context = IssueContext(
            issue_number=10,
            title="Application crash on startup",
            body="The app crashes immediately after launch. Blocking all work.",
            author="user",
            repo_owner="org",
            repo_name="repo",
        )
        priority = await detector.detect_priority(context, IssueCategory.BUG)
        assert priority == Priority.P1

    async def test_crash_bug_gets_p1(
        self, detector: KeywordPriorityDetector, bug_issue: IssueContext
    ) -> None:
        """A bug describing a crash is a P1 — crash keywords escalate severity."""
        priority = await detector.detect_priority(bug_issue, IssueCategory.BUG)
        assert priority == Priority.P1

    async def test_cosmetic_bug_floors_at_p2(self, detector: KeywordPriorityDetector) -> None:
        """Bugs default to P2 even when described with P3 keywords like 'minor'.

        The category baseline is a *floor* — we don't downgrade bugs below P2
        just because the reporter called it minor. (Real-world reasoning:
        users often underestimate the impact of bugs.)
        """
        context = IssueContext(
            issue_number=10,
            title="Minor alignment in footer",
            body="The footer text alignment is slightly off.",
            author="user",
            repo_owner="org",
            repo_name="repo",
        )
        priority = await detector.detect_priority(context, IssueCategory.BUG)
        assert priority == Priority.P2

    async def test_minor_enhancement_downgrades_to_p3(self, detector: KeywordPriorityDetector) -> None:
        """Enhancements (default P3) keep their default when no escalation keyword fires."""
        context = IssueContext(
            issue_number=11,
            title="Polish: tweak button hover color",
            body="Cosmetic polish to the button hover state.",
            author="user",
            repo_owner="org",
            repo_name="repo",
        )
        priority = await detector.detect_priority(context, IssueCategory.ENHANCEMENT)
        assert priority == Priority.P3

    async def test_question_gets_p4(
        self, detector: KeywordPriorityDetector, question_issue: IssueContext
    ) -> None:
        """Questions should get P4 priority."""
        priority = await detector.detect_priority(question_issue, IssueCategory.QUESTION)
        assert priority == Priority.P4

    async def test_feature_defaults_to_p3(
        self, detector: KeywordPriorityDetector, feature_issue: IssueContext
    ) -> None:
        """Feature requests without severity keywords should default to P3."""
        priority = await detector.detect_priority(feature_issue, IssueCategory.FEATURE)
        assert priority == Priority.P3
