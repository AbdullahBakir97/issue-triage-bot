"""Configuration schema using Pydantic v2."""

from __future__ import annotations

from pydantic import BaseModel, Field

__all__ = ["TriageBotConfig"]


class TriageBotConfig(BaseModel):
    """Configuration schema for Issue Triage Bot.

    Loaded from .github/triage-bot.yml in the repository.
    """

    enabled: bool = Field(default=True, description="Whether the bot is active")
    auto_label: bool = Field(default=True, description="Automatically add labels")
    auto_comment: bool = Field(default=True, description="Automatically post triage comment")
    auto_assign: bool = Field(default=False, description="Automatically assign issues")
    require_reproduction_steps: bool = Field(
        default=True,
        description="Require reproduction steps for bug reports",
    )
    assignees: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Category to assignees mapping",
    )
    category_labels: dict[str, str] = Field(
        default_factory=dict,
        description="Custom category label names",
    )
    priority_labels: dict[str, str] = Field(
        default_factory=dict,
        description="Custom priority label names",
    )
    ignore_labels: list[str] = Field(
        default_factory=list,
        description="Labels that prevent triage",
    )
    duplicate_threshold: float = Field(
        default=0.6,
        description="Keyword overlap threshold for duplicate detection",
        ge=0.0,
        le=1.0,
    )
