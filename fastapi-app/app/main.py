"""Main package."""

# Standard library
import logging

logger = logging.getLogger(__name__)


def main() -> None:
    """Main entry point."""
    logger.info("Hello from fastapi-app!")


if __name__ == "__main__":
    main()
