import logging

from core.settings import settings


def setup_logging():
    """Configure logging for the application."""
    log_level = logging.DEBUG if settings.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
