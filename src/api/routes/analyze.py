"""Demo analysis route for testing triage without GitHub integration."""

from __future__ import annotations

from fastapi import APIRouter

from src.analyzers.categorizer import KeywordCategorizer
from src.analyzers.completeness_checker import CompletenessChecker
from src.analyzers.priority_detector import KeywordPriorityDetector
from src.api.schemas import AnalyzeRequest, AnalyzeResponse
from src.domain.entities import IssueContext

__all__ = ["router"]

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_issue(request: AnalyzeRequest) -> AnalyzeResponse:
    """Analyze issue text without posting to GitHub.

    This endpoint is useful for testing and demo purposes.
    It runs categorization, priority detection, and completeness
    checking on the provided text.
    """
    context = IssueContext(
        issue_number=0,
        title=request.title,
        body=request.body,
        author="demo",
        repo_owner="demo",
        repo_name="demo",
    )

    categorizer = KeywordCategorizer()
    priority_detector = KeywordPriorityDetector()
    completeness_checker = CompletenessChecker()

    category, confidence = await categorizer.categorize(context)
    priority = await priority_detector.detect_priority(context, category)
    completeness_score, missing_sections = await completeness_checker.check_completeness(
        context, category
    )

    return AnalyzeResponse(
        category=category.value,
        priority=priority.value,
        confidence=confidence,
        completeness_score=completeness_score,
        missing_sections=missing_sections,
    )
