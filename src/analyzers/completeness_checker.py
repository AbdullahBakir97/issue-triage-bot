"""Issue completeness checking."""

from __future__ import annotations

import re

from src.domain.entities import IssueContext
from src.domain.enums import IssueCategory
from src.domain.interfaces import ICompletenessChecker

__all__ = ["CompletenessChecker"]

BUG_REPORT_SECTIONS: dict[str, list[str]] = {
    "reproduction steps": [
        "steps to reproduce",
        "to reproduce",
        "reproduction",
        "repro steps",
        "how to reproduce",
        "reproduce",
        "step 1",
        "1.",
    ],
    "expected behavior": [
        "expected",
        "expected behavior",
        "expected result",
        "should",
        "supposed to",
    ],
    "actual behavior": [
        "actual",
        "actual behavior",
        "actual result",
        "instead",
        "but",
        "however",
        "currently",
    ],
    "environment info": [
        "environment",
        "os",
        "version",
        "platform",
        "browser",
        "node",
        "python",
        "java",
        "runtime",
    ],
    "error messages": [
        "error",
        "exception",
        "traceback",
        "stack trace",
        "log",
        "output",
        "stderr",
        "message",
    ],
}

FEATURE_SECTIONS: dict[str, list[str]] = {
    "use case": [
        "use case",
        "scenario",
        "context",
        "motivation",
        "reason",
        "why",
        "problem",
    ],
    "proposed solution": [
        "proposal",
        "solution",
        "approach",
        "implementation",
        "design",
        "would like",
        "suggest",
    ],
}


class CompletenessChecker(ICompletenessChecker):
    """Checks whether issues contain required information sections."""

    def __init__(
        self,
        bug_sections: dict[str, list[str]] | None = None,
        feature_sections: dict[str, list[str]] | None = None,
    ) -> None:
        """Initialize with optional custom section definitions."""
        self._bug_sections = bug_sections or BUG_REPORT_SECTIONS
        self._feature_sections = feature_sections or FEATURE_SECTIONS

    async def check_completeness(
        self, context: IssueContext, category: IssueCategory
    ) -> tuple[float, list[str]]:
        """Check issue completeness based on category-specific requirements.

        Returns a tuple of (completeness_score, missing_sections).
        Score is 0.0-1.0 representing percentage of sections found.
        """
        if category == IssueCategory.BUG:
            return self._check_sections(context.full_text, self._bug_sections)
        if category == IssueCategory.FEATURE:
            return self._check_sections(context.full_text, self._feature_sections)
        # Other categories don't have strict completeness requirements
        return 1.0, []

    @staticmethod
    def _check_sections(text: str, sections: dict[str, list[str]]) -> tuple[float, list[str]]:
        """Check for the presence of required sections in text."""
        text_lower = text.lower()
        found = 0
        missing: list[str] = []

        for section_name, keywords in sections.items():
            section_found = False
            for keyword in keywords:
                pattern = re.escape(keyword)
                if re.search(pattern, text_lower):
                    section_found = True
                    break
            if section_found:
                found += 1
            else:
                missing.append(section_name)

        total = len(sections)
        score = round(found / total, 2) if total > 0 else 1.0
        return score, missing
