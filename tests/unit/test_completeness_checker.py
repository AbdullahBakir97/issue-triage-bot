"""Unit tests for the completeness checker."""

from __future__ import annotations

import pytest

from src.analyzers.completeness_checker import CompletenessChecker
from src.domain.entities import IssueContext
from src.domain.enums import IssueCategory


@pytest.fixture
def checker() -> CompletenessChecker:
    """Create a completeness checker instance."""
    return CompletenessChecker()


class TestCompletenessChecker:
    """Tests for CompletenessChecker."""

    async def test_complete_bug_report(
        self, checker: CompletenessChecker, bug_issue: IssueContext
    ) -> None:
        """A complete bug report should score high."""
        score, missing = await checker.check_completeness(bug_issue, IssueCategory.BUG)
        assert score >= 0.8
        assert len(missing) <= 1

    async def test_incomplete_bug_report(
        self, checker: CompletenessChecker, incomplete_bug_issue: IssueContext
    ) -> None:
        """An incomplete bug report should have low score and list missing sections."""
        score, missing = await checker.check_completeness(incomplete_bug_issue, IssueCategory.BUG)
        assert score < 0.6
        assert len(missing) > 0

    async def test_missing_sections_identified(
        self, checker: CompletenessChecker, incomplete_bug_issue: IssueContext
    ) -> None:
        """Missing sections should be correctly identified."""
        _, missing = await checker.check_completeness(incomplete_bug_issue, IssueCategory.BUG)
        assert "reproduction steps" in missing
        assert "environment info" in missing

    async def test_feature_request_completeness(
        self, checker: CompletenessChecker, feature_issue: IssueContext
    ) -> None:
        """Feature requests with use case and solution should be complete."""
        score, missing = await checker.check_completeness(feature_issue, IssueCategory.FEATURE)
        assert score >= 0.5

    async def test_question_always_complete(
        self, checker: CompletenessChecker, question_issue: IssueContext
    ) -> None:
        """Questions don't have completeness requirements."""
        score, missing = await checker.check_completeness(question_issue, IssueCategory.QUESTION)
        assert score == 1.0
        assert missing == []

    async def test_score_between_zero_and_one(
        self, checker: CompletenessChecker, bug_issue: IssueContext
    ) -> None:
        """Completeness score should always be between 0 and 1."""
        score, _ = await checker.check_completeness(bug_issue, IssueCategory.BUG)
        assert 0.0 <= score <= 1.0
