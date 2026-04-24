"""Application settings using Pydantic BaseSettings."""

from __future__ import annotations

from pydantic_settings import BaseSettings

__all__ = ["Settings"]


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "issue-triage-bot"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"
    env: str = "development"

    # GitHub App (canonical names)
    github_app_id: str = ""
    github_private_key: str = ""
    github_webhook_secret: str = ""
    github_installation_id: int = 0

    # Aliases (matches the env vars used on Render)
    app_id: str = ""
    private_key: str = ""
    webhook_secret: str = ""

    # Features
    auto_label: bool = True
    auto_comment: bool = True
    auto_assign: bool = False
    duplicate_threshold: float = 0.6

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }

    def model_post_init(self, __context) -> None:
        """Sync alias fields to canonical names so either env var works."""
        if self.app_id and not self.github_app_id:
            self.github_app_id = self.app_id
        if self.private_key and not self.github_private_key:
            self.github_private_key = self.private_key.replace("\\n", "\n")
        if self.webhook_secret and not self.github_webhook_secret:
            self.github_webhook_secret = self.webhook_secret
