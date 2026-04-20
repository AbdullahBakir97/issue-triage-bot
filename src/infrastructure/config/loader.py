"""Configuration loader from repository files."""

from __future__ import annotations

import logging
from typing import Any

import yaml

from src.domain.interfaces import IConfigLoader, IGitHubClient
from src.infrastructure.config.schema import TriageBotConfig

__all__ = ["ConfigLoader"]

logger = logging.getLogger(__name__)

CONFIG_PATH = ".github/triage-bot.yml"


class ConfigLoader(IConfigLoader):
    """Loads bot configuration from the repository's .github directory."""

    def __init__(self, github_client: IGitHubClient) -> None:
        """Initialize with a GitHub client for file access."""
        self._github_client = github_client

    async def load_config(self, repo: str) -> dict[str, Any]:
        """Load and validate triage bot configuration.

        Attempts to load .github/triage-bot.yml from the repository.
        Returns default configuration if the file is not found.
        """
        content = await self._github_client.get_file_content(repo, CONFIG_PATH)

        if content is None:
            logger.info("No config file found in %s, using defaults", repo)
            return TriageBotConfig().model_dump()

        try:
            raw_config = yaml.safe_load(content) or {}
            config = TriageBotConfig(**raw_config)
            logger.info("Loaded configuration from %s/%s", repo, CONFIG_PATH)
            return config.model_dump()
        except Exception as exc:
            logger.warning(
                "Failed to parse config from %s: %s. Using defaults.",
                repo,
                exc,
            )
            return TriageBotConfig().model_dump()
