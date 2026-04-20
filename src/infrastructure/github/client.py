"""GitHub API client implementation."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from src.domain.exceptions import GitHubClientError
from src.domain.interfaces import IGitHubClient
from src.infrastructure.github.auth import GitHubAppAuth

__all__ = ["GitHubClient"]

logger = logging.getLogger(__name__)

GITHUB_API_BASE = "https://api.github.com"


class GitHubClient(IGitHubClient):
    """GitHub API client using httpx for async operations."""

    def __init__(
        self,
        auth: GitHubAppAuth,
        installation_id: int,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        """Initialize the GitHub client.

        Args:
            auth: GitHub App authentication handler.
            installation_id: The installation ID for token exchange.
            http_client: Optional pre-configured httpx client.
        """
        self._auth = auth
        self._installation_id = installation_id
        self._http_client = http_client or httpx.AsyncClient(timeout=30.0)

    async def _get_headers(self) -> dict[str, str]:
        """Get authenticated request headers."""
        token = await self._auth.get_installation_token(self._installation_id, self._http_client)
        return {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    async def post_comment(self, repo: str, issue_number: int, body: str) -> None:
        """Post a comment on an issue."""
        url = f"{GITHUB_API_BASE}/repos/{repo}/issues/{issue_number}/comments"
        headers = await self._get_headers()

        try:
            response = await self._http_client.post(url, headers=headers, json={"body": body})
            response.raise_for_status()
            logger.info("Posted comment on %s#%d", repo, issue_number)
        except httpx.HTTPStatusError as exc:
            raise GitHubClientError(f"Failed to post comment: {exc.response.status_code}") from exc

    async def add_labels(self, repo: str, issue_number: int, labels: list[str]) -> None:
        """Add labels to an issue."""
        url = f"{GITHUB_API_BASE}/repos/{repo}/issues/{issue_number}/labels"
        headers = await self._get_headers()

        try:
            response = await self._http_client.post(url, headers=headers, json={"labels": labels})
            response.raise_for_status()
            logger.info("Added labels %s to %s#%d", labels, repo, issue_number)
        except httpx.HTTPStatusError as exc:
            raise GitHubClientError(f"Failed to add labels: {exc.response.status_code}") from exc

    async def assign_issue(self, repo: str, issue_number: int, assignees: list[str]) -> None:
        """Assign users to an issue."""
        url = f"{GITHUB_API_BASE}/repos/{repo}/issues/{issue_number}/assignees"
        headers = await self._get_headers()

        try:
            response = await self._http_client.post(
                url, headers=headers, json={"assignees": assignees}
            )
            response.raise_for_status()
            logger.info("Assigned %s to %s#%d", assignees, repo, issue_number)
        except httpx.HTTPStatusError as exc:
            raise GitHubClientError(f"Failed to assign issue: {exc.response.status_code}") from exc

    async def get_recent_issues(self, repo: str, limit: int = 50) -> list[dict[str, Any]]:
        """Get recent issues from the repository."""
        url = f"{GITHUB_API_BASE}/repos/{repo}/issues"
        headers = await self._get_headers()
        params = {
            "state": "all",
            "per_page": str(limit),
            "sort": "created",
            "direction": "desc",
        }

        try:
            response = await self._http_client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            raise GitHubClientError(
                f"Failed to get recent issues: {exc.response.status_code}"
            ) from exc

    async def close_issue(self, repo: str, issue_number: int) -> None:
        """Close an issue."""
        url = f"{GITHUB_API_BASE}/repos/{repo}/issues/{issue_number}"
        headers = await self._get_headers()

        try:
            response = await self._http_client.patch(url, headers=headers, json={"state": "closed"})
            response.raise_for_status()
            logger.info("Closed issue %s#%d", repo, issue_number)
        except httpx.HTTPStatusError as exc:
            raise GitHubClientError(f"Failed to close issue: {exc.response.status_code}") from exc

    async def get_file_content(self, repo: str, path: str) -> str | None:
        """Get file content from the repository."""
        url = f"{GITHUB_API_BASE}/repos/{repo}/contents/{path}"
        headers = await self._get_headers()

        try:
            response = await self._http_client.get(url, headers=headers)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            import base64

            data = response.json()
            content = data.get("content", "")
            return base64.b64decode(content).decode("utf-8")
        except httpx.HTTPStatusError as exc:
            raise GitHubClientError(
                f"Failed to get file content: {exc.response.status_code}"
            ) from exc
