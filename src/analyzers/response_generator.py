"""Priority-aware, category-specific response generator for triaged issues.

Every response is tailored to the *combination* of:
  1. Issue category (bug, feature, question, docs, ...)
  2. Priority level (P0 critical → P4 minor)
  3. What's actually missing or notable

The result reads like a senior maintainer wrote it, not a form letter.
"""

from __future__ import annotations

from src.domain.entities import IssueContext, TriageResult
from src.domain.enums import IssueCategory, Priority

__all__ = ["ResponseGenerator"]


# Concrete examples showing what each missing section *should* look like.
# These are the difference between "please add reproduction steps" and
# "here's the format we expect, with a real example".
_MISSING_SECTION_GUIDANCE: dict[str, tuple[str, str]] = {
    "reproduction steps": (
        "Numbered steps a maintainer can follow on a fresh checkout",
        "1. Run `npm install`\n2. Run `npm start`\n3. Navigate to `/login`\n4. Submit with empty email",
    ),
    "expected behavior": (
        "What you thought would happen if everything worked",
        "**Expected:** Form shows 'Email is required' validation error.",
    ),
    "actual behavior": (
        "What actually happens — paste the exact error if there is one",
        "**Actual:** Page crashes with `TypeError: Cannot read properties of null` (full trace in console).",
    ),
    "environment": (
        "OS, runtime, and library versions — bugs often only reproduce on specific combinations",
        "- OS: macOS 14.2\n- Browser: Chrome 120.0.6099\n- Node: 20.11.0\n- Package version: 2.4.1",
    ),
    "error message": (
        "The exact error text or stack trace — paste it as a fenced code block",
        "```\nTypeError: Cannot read properties of null (reading 'trim')\n  at validateEmail (auth.js:42)\n```",
    ),
    "screenshots": (
        "Screenshot, screen recording, or paste of the rendered output",
        "(drag image here)",
    ),
    "browser version": (
        "Exact browser and version — quirks often differ between Chrome 119 and 120",
        "Chrome 120.0.6099 on macOS 14.2",
    ),
    "node version": (
        "Output of `node --version` — many bugs are version-specific",
        "v20.11.0",
    ),
}


# Category-specific opening lines — different categories need different tone.
# We keep the language professional and concrete.
_CATEGORY_OPENERS: dict[tuple[IssueCategory, Priority], str] = {
    # Bugs — language scales with priority
    (IssueCategory.BUG, Priority.P0): (
        "This has been triaged as **critical (P0)** based on the keywords used "
        "(security, data loss, or broad outage). A maintainer will look at it as soon as possible — "
        "in the meantime, the details below will speed up investigation."
    ),
    (IssueCategory.BUG, Priority.P1): (
        "This has been triaged as **high-priority (P1)** — likely a crash, regression, or "
        "blocker for a common workflow. To diagnose quickly, please confirm the items below."
    ),
    (IssueCategory.BUG, Priority.P2): (
        "Triaged as a **standard bug (P2)**. Please make sure the report has the items "
        "below so a maintainer can reproduce it."
    ),
    (IssueCategory.BUG, Priority.P3): (
        "Triaged as a **minor bug (P3)**. The items below help us reproduce; "
        "even partial info is useful."
    ),
    (IssueCategory.BUG, Priority.P4): (
        "Triaged as a **low-priority bug (P4)** — likely cosmetic or rare-edge-case. "
        "If you have time to add the details below, that helps a future maintainer pick it up."
    ),
    # Feature requests
    (IssueCategory.FEATURE, Priority.P0): (
        "Triaged as a **critical feature request**. This is large enough to need a design discussion — "
        "please describe the use case in detail before any implementation begins."
    ),
    (IssueCategory.FEATURE, Priority.P1): (
        "Triaged as a **high-impact feature request**. Maintainers will review this against "
        "the roadmap. Concrete use cases help us evaluate priority."
    ),
    (IssueCategory.FEATURE, Priority.P2): (
        "Triaged as a **feature request**. Adding a use case ('I want to do X because Y') "
        "is the single most useful thing you can do to move this forward."
    ),
    (IssueCategory.FEATURE, Priority.P3): (
        "Triaged as a **minor feature request**. We track these but small features are usually "
        "implemented as part of larger work — pull requests are welcome."
    ),
    (IssueCategory.FEATURE, Priority.P4): (
        "Triaged as a **nice-to-have**. PRs are welcome — these are unlikely to be picked up "
        "by maintainers without external contribution."
    ),
    # Questions
    (IssueCategory.QUESTION, Priority.P0): (
        "Triaged as a **critical question** — likely affecting your production setup. "
        "Please paste the exact configuration and error you're seeing for the fastest answer."
    ),
    (IssueCategory.QUESTION, Priority.P1): (
        "Triaged as a **support question**. The issue tracker is for bugs and features — "
        "questions are best asked in [Discussions](../../discussions) where they reach more people. "
        "We'll move this if there's a discussions tab."
    ),
    (IssueCategory.QUESTION, Priority.P2): (
        "Triaged as a **question**. For faster answers, [Discussions](../../discussions) is usually "
        "more appropriate — issues are reserved for actionable bugs and feature requests."
    ),
    (IssueCategory.QUESTION, Priority.P3): (
        "Triaged as a **question**. The README, docs, and existing issues often have the answer — "
        "if not, [Discussions](../../discussions) is the right channel."
    ),
    (IssueCategory.QUESTION, Priority.P4): (
        "Triaged as a **question**. Please check the README and existing issues first; "
        "[Discussions](../../discussions) is the right place if not answered."
    ),
    # Docs
    (IssueCategory.DOCS, Priority.P0): (
        "Triaged as a **critical docs issue** — likely something incorrect in published examples. "
        "A PR fixing this would land quickly."
    ),
    (IssueCategory.DOCS, Priority.P1): (
        "Triaged as an **important docs issue**. Pull requests with the fix are very welcome — "
        "docs PRs are usually merged within a day."
    ),
    (IssueCategory.DOCS, Priority.P2): (
        "Triaged as a **docs issue**. If you have time to send a PR, that's the fastest path; "
        "we accept docs-only PRs without much process."
    ),
    (IssueCategory.DOCS, Priority.P3): (
        "Triaged as a **minor docs issue**. PRs are welcome — even a single-line clarification helps."
    ),
    (IssueCategory.DOCS, Priority.P4): (
        "Triaged as a **typo or minor docs improvement**. Feel free to send a PR directly — "
        "we don't require an issue first for small doc edits."
    ),
}


# Generic fallback openers when a specific category+priority combo isn't mapped.
_CATEGORY_FALLBACK: dict[IssueCategory, str] = {
    IssueCategory.BUG: (
        "Triaged as a bug. The details below will help maintainers reproduce and verify a fix."
    ),
    IssueCategory.FEATURE: (
        "Triaged as a feature request. A clear use case is the single most useful thing to add."
    ),
    IssueCategory.QUESTION: (
        "Triaged as a question. [Discussions](../../discussions) is usually a faster channel."
    ),
    IssueCategory.DOCS: "Triaged as a docs issue. PRs are welcome.",
    IssueCategory.ENHANCEMENT: "Triaged as an enhancement to existing functionality.",
    IssueCategory.SUPPORT: "Triaged as a support request.",
    IssueCategory.UNKNOWN: "Triaged — a maintainer will follow up shortly.",
}


class ResponseGenerator:
    """Generates priority-aware, category-specific triage responses."""

    async def generate_response(
        self,
        context: IssueContext,
        result: TriageResult,
    ) -> str:
        """Generate the full triage comment.

        Args:
            context: The issue we're responding to.
            result: The triage result (category, priority, missing sections, ...).

        Returns:
            A Markdown comment string.
        """
        sections: list[str] = []

        # 1. Duplicate notice always comes first when present — no point asking
        #    for repro steps on something that's already a known issue.
        if result.duplicate_of is not None:
            sections.append(self._duplicate_section(result.duplicate_of, context))
            sections.append(self._footer())
            return "\n\n".join(sections)

        # 2. Category + priority opener — sets the tone.
        sections.append(self._opener(result))

        # 3. For bugs with missing sections, surface each one with format guidance.
        if result.category == IssueCategory.BUG and result.missing_sections:
            sections.append(self._missing_sections_block(result.missing_sections))

        # 4. For feature requests, prompt for the use case if the body is thin.
        if result.category == IssueCategory.FEATURE and self._body_is_thin(context.body):
            sections.append(self._feature_use_case_prompt())

        # 5. For complete bug reports, acknowledge specifically what's good.
        if result.category == IssueCategory.BUG and not result.missing_sections:
            sections.append(self._complete_bug_acknowledgement(result.priority))

        sections.append(self._footer())
        return "\n\n".join(sections)

    # ------------------------------------------------------------------ #
    # Sections
    # ------------------------------------------------------------------ #

    @staticmethod
    def _duplicate_section(duplicate_number: int, context: IssueContext) -> str:
        """Specific duplicate notice citing the linked issue and asking for clarification."""
        return (
            f"### Possible duplicate of #{duplicate_number}\n\n"
            f"This issue looks similar to [#{duplicate_number}]"
            f"(../../issues/{duplicate_number}) based on shared keywords. "
            "If they describe the same problem, we'll close this in favour of the existing thread "
            "(your details will be moved over). If they're different, please add a sentence "
            "explaining the difference so we can keep them separate."
        )

    @staticmethod
    def _opener(result: TriageResult) -> str:
        """Category + priority specific opener."""
        key = (result.category, result.priority)
        if key in _CATEGORY_OPENERS:
            return _CATEGORY_OPENERS[key]
        return _CATEGORY_FALLBACK.get(result.category, _CATEGORY_FALLBACK[IssueCategory.UNKNOWN])

    @staticmethod
    def _missing_sections_block(missing: list[str]) -> str:
        """List each missing section with what it should contain and an example."""
        lines: list[str] = ["### Information still needed"]
        for section in missing:
            key = section.lower()
            if key in _MISSING_SECTION_GUIDANCE:
                what, example = _MISSING_SECTION_GUIDANCE[key]
                lines.append(f"\n**{section.title()}**")
                lines.append(f"_{what}._")
                lines.append("")
                lines.append("Example:")
                lines.append(f"```\n{example}\n```")
            else:
                lines.append(f"- **{section.title()}** — please add this section")
        return "\n".join(lines)

    @staticmethod
    def _feature_use_case_prompt() -> str:
        """Ask for a concrete use case when a feature request is thin."""
        return (
            "### Use case needed\n\n"
            "To evaluate this feature, we need a concrete use case. The most useful framing is:\n\n"
            "- **Who** wants this? (your role / project context)\n"
            "- **What** are you trying to do that's currently hard or impossible?\n"
            "- **Why** can't existing features be combined to achieve it?\n\n"
            "A real example beats a hypothetical one — if you've worked around this in some other way, "
            "describe that workaround."
        )

    @staticmethod
    def _complete_bug_acknowledgement(priority: Priority) -> str:
        """Acknowledge a well-formed bug report with priority-specific framing."""
        if priority == Priority.P0:
            return (
                "### Critical bug — escalating\n\n"
                "Report has all the information needed to investigate. Escalating to maintainers; "
                "you should expect a response within hours, not days."
            )
        if priority == Priority.P1:
            return (
                "### Well-formed report — queued for investigation\n\n"
                "Thanks — this report has everything we need. It's been queued and a maintainer "
                "will pick it up in the next triage cycle."
            )
        return (
            "### Report looks complete\n\n"
            "Thanks for the thorough report. A maintainer will pick this up; "
            "no further action needed from you for now."
        )

    @staticmethod
    def _body_is_thin(body: str) -> bool:
        """Heuristic: feature requests under ~100 chars are usually missing context."""
        return len(body.strip()) < 100

    @staticmethod
    def _footer() -> str:
        return (
            "---\n"
            "_[Issue Triage Bot](https://github.com/AbdullahBakir97/issue-triage-bot) "
            "— automated issue triage and routing_"
        )
