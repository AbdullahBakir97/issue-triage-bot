"""Label management for GitHub issues."""

from __future__ import annotations

from src.domain.enums import IssueCategory, Priority

__all__ = ["LabelManager"]

CATEGORY_LABELS: dict[IssueCategory, dict[str, str]] = {
    IssueCategory.BUG: {"name": "bug", "color": "d73a4a"},
    IssueCategory.FEATURE: {"name": "feature", "color": "a2eeef"},
    IssueCategory.QUESTION: {"name": "question", "color": "d876e3"},
    IssueCategory.DOCS: {"name": "documentation", "color": "0075ca"},
    IssueCategory.ENHANCEMENT: {"name": "enhancement", "color": "a2eeef"},
    IssueCategory.SUPPORT: {"name": "support", "color": "f9d0c4"},
    IssueCategory.UNKNOWN: {"name": "needs-triage", "color": "ededed"},
}

PRIORITY_LABELS: dict[Priority, dict[str, str]] = {
    Priority.P0: {"name": "priority: critical", "color": "b60205"},
    Priority.P1: {"name": "priority: high", "color": "d93f0b"},
    Priority.P2: {"name": "priority: medium", "color": "fbca04"},
    Priority.P3: {"name": "priority: low", "color": "0e8a16"},
    Priority.P4: {"name": "priority: minimal", "color": "c5def5"},
}


class LabelManager:
    """Manages label generation and color schemes for triaged issues."""

    def __init__(
        self,
        category_labels: dict[IssueCategory, dict[str, str]] | None = None,
        priority_labels: dict[Priority, dict[str, str]] | None = None,
    ) -> None:
        """Initialize with optional custom label configurations."""
        self._category_labels = category_labels or CATEGORY_LABELS
        self._priority_labels = priority_labels or PRIORITY_LABELS

    def get_labels_for_category(self, category: IssueCategory) -> list[str]:
        """Get label names for a given category."""
        label_info = self._category_labels.get(category)
        if label_info:
            return [label_info["name"]]
        return ["needs-triage"]

    def get_labels_for_priority(self, priority: Priority) -> list[str]:
        """Get label names for a given priority."""
        label_info = self._priority_labels.get(priority)
        if label_info:
            return [label_info["name"]]
        return []

    def get_all_labels(self, category: IssueCategory, priority: Priority) -> list[str]:
        """Get all labels for a category and priority combination."""
        labels = self.get_labels_for_category(category)
        labels.extend(self.get_labels_for_priority(priority))
        return labels

    def get_label_color(self, label_name: str) -> str | None:
        """Get the color hex code for a label name."""
        for label_info in self._category_labels.values():
            if label_info["name"] == label_name:
                return label_info["color"]
        for label_info in self._priority_labels.values():
            if label_info["name"] == label_name:
                return label_info["color"]
        return None

    @property
    def all_label_definitions(self) -> list[dict[str, str]]:
        """Get all label definitions for repository setup."""
        labels: list[dict[str, str]] = []
        for label_info in self._category_labels.values():
            labels.append(label_info)
        for label_info in self._priority_labels.values():
            labels.append(label_info)
        return labels
