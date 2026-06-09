"""Generic SQLAlchemy session test doubles."""

# Standard library
from dataclasses import dataclass


@dataclass
class ClosingSession:
    """Minimal session fake for testing generator cleanup."""

    closed: bool = False

    def close(self) -> None:
        self.closed = True
