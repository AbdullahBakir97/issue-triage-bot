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

    # GitHub App
    github_app_id: str = ""
    github_private_key: str = ""
    github_webhook_secret: str = ""
    github_installation_id: int = 0

    # Features
    auto_label: bool = True
    auto_comment: bool = True
    auto_assign: bool = False
    duplicate_threshold: float = 0.6

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }
