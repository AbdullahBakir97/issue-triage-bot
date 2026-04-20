"""Unit tests for the keyword categorizer."""

from __future__ import annotations

import pytest

from src.analyzers.categorizer import KeywordCategorizer
from src.domain.entities import IssueContext
from src.domain.enums import IssueCategory


@pytest.fixture
def categorizer() -> KeywordCategorizer:
    """Create a categorizer instance."""
    return KeywordCategorizer()


class TestKeywordCategorizer:
    """Tests for KeywordCategorizer."""

    async def test_categorizes_bug_report(
        self, categorizer: KeywordCategorizer, bug_issue: IssueContext
    ) -> None:
        """Bug reports should be categorized as BUG."""
        category, confidence = await categorizer.categorize(bug_issue)
        assert category == IssueCategory.BUG
        assert confidence > 0.0

    async def test_categorizes_feature_request(
        self, categorizer: KeywordCategorizer, feature_issue: IssueContext
    ) -> None:
        """Feature requests should be categorized as FEATURE."""
        category, confidence = await categorizer.categorize(feature_issue)
        assert category == IssueCategory.FEATURE
        assert confidence > 0.0

    async def test_categorizes_question(
        self, categorizer: KeywordCategorizer, question_issue: IssueContext
    ) -> None:
        """Questions should be categorized as QUESTION."""
        category, confidence = await categorizer.categorize(question_issue)
        assert category == IssueCategory.QUESTION
        assert confidence > 0.0

    async def test_categorizes_docs_issue(self, categorizer: KeywordCategorizer) -> None:
        """Documentation issues should be categorized as DOCS."""
        context = IssueContext(
            issue_number=10,
            title="Typo in README",
            body="The docs have a spelling error in the installation guide.",
            author="user",
            repo_owner="org",
            repo_name="repo",
        )
        category, confidence = await categorizer.categorize(context)
        assert category == IssueCategory.DOCS
        assert confidence > 0.0

    async def test_unknown_category_for_empty_text(self, categorizer: KeywordCategorizer) -> None:
        """Empty or unrecognizable text should return UNKNOWN."""
        context = IssueContext(
            issue_number=99,
            title="xyz",
            body="abc 123",
            author="user",
            repo_owner="org",
            repo_name="repo",
        )
        category, confidence = await categorizer.categorize(context)
        assert category == IssueCategory.UNKNOWN
        assert confidence == 0.0

    async def test_confidence_between_zero_and_one(
        self, categorizer: KeywordCategorizer, bug_issue: IssueContext
    ) -> None:
        """Confidence score should always be between 0 and 1."""
        _, confidence = await categorizer.categorize(bug_issue)
        assert 0.0 <= confidence <= 1.0
