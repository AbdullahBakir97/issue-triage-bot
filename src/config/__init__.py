"""Application configuration."""

from src.config.logging import setup_logging
from src.config.settings import Settings

__all__ = ["Settings", "setup_logging"]
