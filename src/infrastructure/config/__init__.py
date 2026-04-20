"""Configuration infrastructure components."""

from src.infrastructure.config.loader import ConfigLoader
from src.infrastructure.config.schema import TriageBotConfig

__all__ = ["TriageBotConfig", "ConfigLoader"]
