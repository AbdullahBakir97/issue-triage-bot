"""Tests for the priority-aware, category-specific response generator."""

from __future__ import annotations

import pytest

from src.analyzers.response_generator import ResponseGenerator
from src.domain.entities import IssueContext, TriageResult
from src.domain.enums import IssueCategory, Priority


# ------------------------------------------------------------------ #
# Fixtures
# ------------------------------------------------------------------ #


@pytest.fixture
def generator() -> ResponseGenerator:
    return ResponseGenerator()


def _ctx(*, body: str = "Some description", title: str = "Issue title") -> IssueContext:
    return IssueContext(
        issue_number=1,
        title=title,
        body=body,
        author="user",
        repo_owner="org",
        repo_name="repo",
        labels=[],
        is_pull_request=False,
    )


def _result(
    *,
    category: IssueCategory = IssueCategory.BUG,
    priority: Priority = Priority.P2,
    missing_sections: list[str] | None = None,
    duplicate_of: int | None = None,
    confidence: float = 0.8,
) -> TriageResult:
    return TriageResult(
        category=category,
        priority=priority,
        confidence=confidence,
        missing_sections=missing_sections or [],
        duplicate_of=duplicate_of,
    )


# ------------------------------------------------------------------ #
# Scenario 1: Duplicate detection short-circuits everything
# ------------------------------------------------------------------ #


class TestDuplicate:
    @pytest.mark.asyncio
    async def test_duplicate_response_cites_the_linked_issue(self, generator):
        ctx = _ctx()
        result = _result(duplicate_of=42)

        comment = await generator.generate_response(ctx, result)

        assert "#42" in comment
        assert "Possible duplicate" in comment
        # When it's a duplicate, we don't ask for repro steps
        assert "Information still needed" not in comment

    @pytest.mark.asyncio
    async def test_duplicate_response_invites_clarification(self, generator):
        ctx = _ctx()
        result = _result(duplicate_of=99, missing_sections=["reproduction steps"])

        comment = await generator.generate_response(ctx, result)

        # Even though missing_sections is set, the duplicate path skips it.
        assert "Information still needed" not in comment
        assert "explaining the difference" in comment


# ------------------------------------------------------------------ #
# Scenario 2: Bug priority levels — different tones
# ------------------------------------------------------------------ #


class TestBugByPriority:
    @pytest.mark.asyncio
    async def test_p0_uses_critical_language(self, generator):
        ctx = _ctx()
        result = _result(category=IssueCategory.BUG, priority=Priority.P0)

        comment = await generator.generate_response(ctx, result)

        assert "critical (P0)" in comment.lower() or "critical" in comment.lower()
        assert "as soon as possible" in comment

    @pytest.mark.asyncio
    async def test_p1_uses_high_priority_language(self, generator):
        ctx = _ctx()
        result = _result(category=IssueCategory.BUG, priority=Priority.P1)

        comment = await generator.generate_response(ctx, result)

        assert "high-priority" in comment.lower()
        assert "P1" in comment

    @pytest.mark.asyncio
    async def test_p4_uses_lower_urgency_language(self, generator):
        ctx = _ctx()
        result = _result(category=IssueCategory.BUG, priority=Priority.P4)

        comment = await generator.generate_response(ctx, result)

        assert "low-priority" in comment.lower() or "P4" in comment

    @pytest.mark.asyncio
    async def test_priority_levels_produce_different_comments(self, generator):
        ctx = _ctx()
        comments = []
        for p in [Priority.P0, Priority.P1, Priority.P2, Priority.P3, Priority.P4]:
            comments.append(
                await generator.generate_response(
                    ctx, _result(category=IssueCategory.BUG, priority=p)
                )
            )

        # All five priority levels should produce *different* comments
        assert len(set(comments)) == 5


# ------------------------------------------------------------------ #
# Scenario 3: Missing sections get specific format guidance + examples
# ------------------------------------------------------------------ #


class TestMissingSections:
    @pytest.mark.asyncio
    async def test_each_missing_section_gets_format_example(self, generator):
        ctx = _ctx(body="The app crashes")
        result = _result(
            category=IssueCategory.BUG,
            priority=Priority.P2,
            missing_sections=["reproduction steps", "environment", "error message"],
        )

        comment = await generator.generate_response(ctx, result)

        # Each section appears with its concrete example
        assert "Reproduction Steps" in comment
        assert "Environment" in comment
        assert "Error Message" in comment

        # Format examples are present
        assert "Run `npm install`" in comment  # repro step example
        assert "macOS" in comment  # env example
        assert "TypeError" in comment  # error example

    @pytest.mark.asyncio
    async def test_unknown_missing_section_falls_back_to_generic(self, generator):
        ctx = _ctx(body="The app crashes")
        result = _result(
            category=IssueCategory.BUG,
            priority=Priority.P2,
            missing_sections=["custom_section_we_didnt_anticipate"],
        )

        comment = await generator.generate_response(ctx, result)

        # Falls back to a generic "please add this section" message
        assert "Custom_Section_We_Didnt_Anticipate" in comment
        assert "please add this section" in comment

    @pytest.mark.asyncio
    async def test_complete_bug_report_gets_acknowledgement_not_request(self, generator):
        ctx = _ctx(body="Detailed report")
        result = _result(
            category=IssueCategory.BUG,
            priority=Priority.P1,
            missing_sections=[],
        )

        comment = await generator.generate_response(ctx, result)

        # No "Information still needed" section
        assert "Information still needed" not in comment

        # But there IS an acknowledgement
        assert "Well-formed report" in comment or "Report looks complete" in comment


# ------------------------------------------------------------------ #
# Scenario 4: Feature requests prompt for use case when body is thin
# ------------------------------------------------------------------ #


class TestFeatureRequest:
    @pytest.mark.asyncio
    async def test_thin_feature_body_prompts_use_case(self, generator):
        ctx = _ctx(body="Add dark mode")  # very thin
        result = _result(category=IssueCategory.FEATURE, priority=Priority.P2)

        comment = await generator.generate_response(ctx, result)

        assert "Use case needed" in comment
        assert "Who" in comment and "What" in comment and "Why" in comment

    @pytest.mark.asyncio
    async def test_substantial_feature_body_skips_use_case_prompt(self, generator):
        ctx = _ctx(
            body=(
                "I'm building a documentation site for my open-source project. "
                "Users have asked for a dark mode option because they read at night. "
                "I tried using a CSS-only solution but it doesn't sync with system preferences. "
                "Native dark mode support with system detection would solve this completely."
            )
        )
        result = _result(category=IssueCategory.FEATURE, priority=Priority.P2)

        comment = await generator.generate_response(ctx, result)

        # Body is substantial — no need to ask for a use case again
        assert "Use case needed" not in comment

    @pytest.mark.asyncio
    async def test_feature_priority_changes_opener(self, generator):
        ctx = _ctx(body="Substantial use case description here that exceeds the thin threshold easily.")
        comments = []
        for p in [Priority.P0, Priority.P1, Priority.P2, Priority.P3, Priority.P4]:
            comments.append(
                await generator.generate_response(
                    ctx, _result(category=IssueCategory.FEATURE, priority=p)
                )
            )

        # All priorities produce distinct openers
        assert len(set(comments)) == 5


# ------------------------------------------------------------------ #
# Scenario 5: Questions redirect to discussions
# ------------------------------------------------------------------ #


class TestQuestion:
    @pytest.mark.asyncio
    async def test_question_redirects_to_discussions(self, generator):
        ctx = _ctx(body="How do I configure X?")
        result = _result(category=IssueCategory.QUESTION, priority=Priority.P2)

        comment = await generator.generate_response(ctx, result)

        assert "Discussions" in comment

    @pytest.mark.asyncio
    async def test_p0_question_is_more_urgent(self, generator):
        ctx = _ctx(body="Production is broken")
        result = _result(category=IssueCategory.QUESTION, priority=Priority.P0)

        comment = await generator.generate_response(ctx, result)

        assert "production" in comment.lower()
        # P0 question doesn't redirect away — it engages
        assert "fastest answer" in comment or "exact configuration" in comment


# ------------------------------------------------------------------ #
# Scenario 6: Docs invite PRs
# ------------------------------------------------------------------ #


class TestDocs:
    @pytest.mark.asyncio
    async def test_docs_response_invites_pr(self, generator):
        ctx = _ctx(body="The README has a typo")
        result = _result(category=IssueCategory.DOCS, priority=Priority.P3)

        comment = await generator.generate_response(ctx, result)

        assert "PR" in comment

    @pytest.mark.asyncio
    async def test_p4_docs_says_no_issue_required(self, generator):
        ctx = _ctx(body="Typo in README")
        result = _result(category=IssueCategory.DOCS, priority=Priority.P4)

        comment = await generator.generate_response(ctx, result)

        # P4 docs explicitly say "send a PR directly"
        assert "send a PR directly" in comment


# ------------------------------------------------------------------ #
# Scenario 7: Voice quality
# ------------------------------------------------------------------ #


class TestVoiceQuality:
    AI_TRIGGERS = [
        "I'd be happy to",
        "hope this helps",
        "feel free to reach out",
        "delve into",
        "holistic approach",
        "Thank you for reporting",  # the old generic boilerplate
    ]

    @pytest.mark.asyncio
    async def test_no_ai_phrases_in_any_scenario(self, generator):
        scenarios = [
            (IssueCategory.BUG, Priority.P0, []),
            (IssueCategory.BUG, Priority.P2, ["reproduction steps"]),
            (IssueCategory.FEATURE, Priority.P3, []),
            (IssueCategory.QUESTION, Priority.P2, []),
            (IssueCategory.DOCS, Priority.P4, []),
        ]
        for category, priority, missing in scenarios:
            ctx = _ctx(body="Sample body" * 30)
            result = _result(category=category, priority=priority, missing_sections=missing)
            comment = await generator.generate_response(ctx, result)
            lowered = comment.lower()

            for phrase in self.AI_TRIGGERS:
                assert phrase.lower() not in lowered, (
                    f"Scenario {category.value}/{priority.value} contains '{phrase}'"
                )


# ------------------------------------------------------------------ #
# Scenario 8: Footer
# ------------------------------------------------------------------ #


class TestFooter:
    @pytest.mark.asyncio
    async def test_footer_links_to_project(self, generator):
        ctx = _ctx()
        result = _result()

        comment = await generator.generate_response(ctx, result)

        assert "github.com/AbdullahBakir97/issue-triage-bot" in comment
