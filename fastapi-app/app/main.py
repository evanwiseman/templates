"""Main package."""

# Standard library
import logging
import sys

# First party
from app.core.config import settings

logger = logging.getLogger(__name__)
logger.setLevel(settings.log_level)


def configure_logging(level: int) -> None:
    logging.basicConfig(
        level=level,
        format="%(levelname)s : %(name)s - %(message)s",
        stream=sys.stdout,
    )


def main() -> None:
    """Main entry point."""
    configure_logging(settings.log_level)
    logger.info("Hello from fastapi-app!")


if __name__ == "__main__":
    main()
