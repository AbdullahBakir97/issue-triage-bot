"""Triage comment builder for GitHub issues."""

from __future__ import annotations

from src.domain.entities import IssueContext, TriageResult
from src.domain.enums import IssueCategory, Priority

__all__ = ["CommentBuilder"]


class CommentBuilder:
    """Builds structured triage comments for GitHub issues."""

    async def build_triage_comment(self, context: IssueContext, result: TriageResult) -> str:
        """Build a comprehensive triage comment summarizing analysis results.

        Includes category, priority, completeness assessment, and
        duplicate detection results.
        """
        sections: list[str] = []

        # Header
        sections.append("## Issue Triage Summary\n")

        # Category and priority
        sections.append(self._build_classification_section(result))

        # Completeness
        if result.category == IssueCategory.BUG:
            sections.append(self._build_completeness_section(result))

        # Duplicates
        if result.duplicate_of is not None:
            sections.append(self._build_duplicate_section(result))

        # Footer
        sections.append(self._build_footer())

        return "\n".join(sections)

    @staticmethod
    def _build_classification_section(result: TriageResult) -> str:
        """Build the classification details section."""
        category_emoji = {
            IssueCategory.BUG: "bug",
            IssueCategory.FEATURE: "sparkles",
            IssueCategory.QUESTION: "question",
            IssueCategory.DOCS: "books",
            IssueCategory.ENHANCEMENT: "rocket",
            IssueCategory.SUPPORT: "raised_hands",
            IssueCategory.UNKNOWN: "grey_question",
        }

        priority_indicator = {
            Priority.P0: "CRITICAL",
            Priority.P1: "HIGH",
            Priority.P2: "MEDIUM",
            Priority.P3: "LOW",
            Priority.P4: "MINIMAL",
        }

        emoji = category_emoji.get(result.category, "grey_question")
        indicator = priority_indicator.get(result.priority, "UNKNOWN")

        return (
            f"| Field | Value |\n"
            f"|-------|-------|\n"
            f"| **Category** | :{emoji}: {result.category.value} |\n"
            f"| **Priority** | {result.priority.value} ({indicator}) |\n"
            f"| **Confidence** | {result.confidence:.0%} |\n"
        )

    @staticmethod
    def _build_completeness_section(result: TriageResult) -> str:
        """Build the completeness assessment section."""
        score_bar = _progress_bar(result.completeness_score)

        section = f"\n### Completeness: {score_bar} {result.completeness_score:.0%}\n"

        if result.missing_sections:
            section += "\n**Missing information:**\n"
            for item in result.missing_sections:
                section += f"- [ ] {item}\n"

        return section

    @staticmethod
    def _build_duplicate_section(result: TriageResult) -> str:
        """Build the duplicate detection section."""
        return (
            f"\n### Potential Duplicate\n\n"
            f"This issue appears similar to #{result.duplicate_of}. "
            f"Please verify if they describe the same problem.\n"
        )

    @staticmethod
    def _build_footer() -> str:
        """Build the comment footer."""
        return (
            "\n---\n"
            "*This triage was performed automatically by Issue Triage Bot. "
            "Maintainers may adjust labels and priority as needed.*"
        )


def _progress_bar(score: float) -> str:
    """Generate a text-based progress bar."""
    filled = int(score * 5)
    empty = 5 - filled
    return "[" + "=" * filled + " " * empty + "]"
