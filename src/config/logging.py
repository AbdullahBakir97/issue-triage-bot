"""Logging configuration."""

from __future__ import annotations

import logging
import sys

__all__ = ["setup_logging"]


def setup_logging(level: str = "INFO") -> None:
    """Configure application logging.

    Sets up structured logging with consistent formatting
    across all application modules.

    Args:
        level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    """
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format=log_format,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )

    # Quiet noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
