"""Template-based response generation for triaged issues."""

from __future__ import annotations

from src.domain.entities import IssueContext, TriageResult
from src.domain.enums import IssueCategory

__all__ = ["ResponseGenerator"]


class ResponseGenerator:
    """Generates template responses based on triage results."""

    async def generate_response(self, context: IssueContext, result: TriageResult) -> str:
        """Generate an appropriate response comment based on triage results."""
        parts: list[str] = []

        # Duplicate notice takes top priority
        if result.duplicate_of is not None:
            parts.append(self._duplicate_response(result.duplicate_of))

        # Incomplete bug reports
        if result.category == IssueCategory.BUG and result.missing_sections:
            parts.append(self._incomplete_bug_response(result.missing_sections))

        # Category-specific responses
        if result.category == IssueCategory.QUESTION:
            parts.append(self._question_response())
        elif result.category == IssueCategory.BUG and not result.missing_sections:
            parts.append(self._good_report_response())
        elif result.category == IssueCategory.FEATURE:
            parts.append(self._feature_response())
        elif result.category == IssueCategory.DOCS:
            parts.append(self._docs_response())

        if not parts:
            parts.append(self._default_response())

        return "\n\n".join(parts)

    @staticmethod
    def _duplicate_response(issue_number: int) -> str:
        """Response for potential duplicates."""
        return (
            f"**Potential Duplicate Detected**\n\n"
            f"This issue may be related to #{issue_number}. "
            f"Please check if your issue has already been reported there.\n\n"
            f"If this is indeed a duplicate, we may close this issue in favor "
            f"of the existing one. If you believe this is a separate issue, "
            f"please clarify the differences."
        )

    @staticmethod
    def _incomplete_bug_response(missing: list[str]) -> str:
        """Response for incomplete bug reports."""
        missing_list = "\n".join(f"- {section}" for section in missing)
        return (
            f"**Additional Information Needed**\n\n"
            f"Thank you for reporting this issue! To help us investigate, "
            f"could you please provide the following information:\n\n"
            f"{missing_list}\n\n"
            f"Having these details will help us reproduce and fix the issue faster."
        )

    @staticmethod
    def _question_response() -> str:
        """Response for questions."""
        return (
            "**Question Received**\n\n"
            "Thank you for your question! While we work on answering it, "
            "you might find helpful information in:\n\n"
            "- Our [documentation](./docs)\n"
            "- The [FAQ section](./docs/faq.md)\n"
            "- Previous [discussions](../../discussions)\n\n"
            "A maintainer will respond as soon as possible."
        )

    @staticmethod
    def _good_report_response() -> str:
        """Response for well-written bug reports."""
        return (
            "**Thank You!**\n\n"
            "Thank you for the detailed bug report! "
            "This has been triaged and will be looked into. "
            "A maintainer will follow up with next steps."
        )

    @staticmethod
    def _feature_response() -> str:
        """Response for feature requests."""
        return (
            "**Feature Request Received**\n\n"
            "Thank you for the feature suggestion! "
            "We will review this proposal and discuss it with the team. "
            "Feel free to provide additional context or use cases."
        )

    @staticmethod
    def _docs_response() -> str:
        """Response for documentation issues."""
        return (
            "**Documentation Issue Noted**\n\n"
            "Thank you for helping improve our documentation! "
            "We appreciate contributions to docs. "
            "If you'd like, feel free to submit a PR with the fix."
        )

    @staticmethod
    def _default_response() -> str:
        """Default response for uncategorized issues."""
        return (
            "**Issue Received**\n\n"
            "Thank you for opening this issue! "
            "It has been triaged and a maintainer will review it shortly."
        )
