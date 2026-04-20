"""Application entrypoint."""

from __future__ import annotations

import uvicorn

from src.api.app import create_app
from src.config.logging import setup_logging
from src.config.settings import Settings


def main() -> None:
    """Start the Issue Triage Bot application."""
    settings = Settings()
    setup_logging(settings.log_level)

    app = create_app()

    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
