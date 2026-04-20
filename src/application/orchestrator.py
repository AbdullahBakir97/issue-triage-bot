"""Triage orchestrator coordinating all analysis steps."""

from __future__ import annotations

import logging

from src.analyzers.response_generator import ResponseGenerator
from src.domain.entities import IssueContext, TriageResult
from src.domain.enums import TriageAction
from src.domain.interfaces import (
    ICategorizer,
    ICompletenessChecker,
    IDuplicateDetector,
    IGitHubClient,
    IPriorityDetector,
)
from src.generators.comment_builder import CommentBuilder
from src.generators.label_manager import LabelManager

__all__ = ["TriageOrchestrator"]

logger = logging.getLogger(__name__)


class TriageOrchestrator:
    """Orchestrates the full issue triage pipeline.

    Coordinates categorization, priority detection, completeness
    checking, duplicate detection, and response generation.
    """

    def __init__(
        self,
        categorizer: ICategorizer,
        priority_detector: IPriorityDetector,
        completeness_checker: ICompletenessChecker,
        duplicate_detector: IDuplicateDetector,
        github_client: IGitHubClient,
        label_manager: LabelManager,
        comment_builder: CommentBuilder,
        response_generator: ResponseGenerator,
        *,
        auto_label: bool = True,
        auto_comment: bool = True,
        auto_assign: bool = False,
        assignees_mapping: dict[str, list[str]] | None = None,
    ) -> None:
        """Initialize the orchestrator with all required components."""
        self._categorizer = categorizer
        self._priority_detector = priority_detector
        self._completeness_checker = completeness_checker
        self._duplicate_detector = duplicate_detector
        self._github_client = github_client
        self._label_manager = label_manager
        self._comment_builder = comment_builder
        self._response_generator = response_generator
        self._auto_label = auto_label
        self._auto_comment = auto_comment
        self._auto_assign = auto_assign
        self._assignees_mapping = assignees_mapping or {}

    async def triage(self, context: IssueContext) -> TriageResult:
        """Run the full triage pipeline for an issue.

        Steps:
        1. Categorize the issue
        2. Detect priority
        3. Check completeness
        4. Detect duplicates
        5. Generate response
        6. Apply actions (labels, comments, assignments)
        """
        logger.info(
            "Starting triage for issue #%d in %s",
            context.issue_number,
            context.repo_full_name,
        )

        # Step 1: Categorize
        category, confidence = await self._categorizer.categorize(context)
        logger.info("Category: %s (confidence: %.2f)", category.value, confidence)

        # Step 2: Detect priority
        priority = await self._priority_detector.detect_priority(context, category)
        logger.info("Priority: %s", priority.value)

        # Step 3: Check completeness
        completeness_score, missing_sections = await self._completeness_checker.check_completeness(
            context, category
        )
        logger.info("Completeness: %.0f%%", completeness_score * 100)

        # Step 4: Detect duplicates
        recent_issues = await self._github_client.get_recent_issues(context.repo_full_name)
        duplicate_of = await self._duplicate_detector.find_duplicates(context, recent_issues)
        if duplicate_of:
            logger.info("Potential duplicate of #%d", duplicate_of)

        # Build result
        labels = self._label_manager.get_all_labels(category, priority)
        assignees = self._get_assignees(category.value)
        actions: list[TriageAction] = []

        if self._auto_label:
            actions.append(TriageAction.LABEL)
        if self._auto_comment:
            actions.append(TriageAction.COMMENT)
        if self._auto_assign and assignees:
            actions.append(TriageAction.ASSIGN)

        result = TriageResult(
            category=category,
            priority=priority,
            confidence=confidence,
            actions=actions,
            labels=labels,
            assignees=assignees,
            duplicate_of=duplicate_of,
            completeness_score=completeness_score,
            missing_sections=missing_sections,
        )

        # Generate comment
        response = await self._response_generator.generate_response(context, result)
        triage_comment = await self._comment_builder.build_triage_comment(context, result)
        result.comment = f"{triage_comment}\n\n{response}"

        # Step 6: Apply actions
        await self._apply_actions(context, result)

        logger.info(
            "Triage complete for issue #%d: %s/%s",
            context.issue_number,
            category.value,
            priority.value,
        )

        return result

    async def _apply_actions(self, context: IssueContext, result: TriageResult) -> None:
        """Apply triage actions to the GitHub issue."""
        repo = context.repo_full_name

        if TriageAction.LABEL in result.actions and result.labels:
            await self._github_client.add_labels(repo, context.issue_number, result.labels)

        if TriageAction.COMMENT in result.actions and result.comment:
            await self._github_client.post_comment(repo, context.issue_number, result.comment)

        if TriageAction.ASSIGN in result.actions and result.assignees:
            await self._github_client.assign_issue(repo, context.issue_number, result.assignees)

    def _get_assignees(self, category: str) -> list[str]:
        """Get assignees for a category based on configuration."""
        return self._assignees_mapping.get(category, [])
