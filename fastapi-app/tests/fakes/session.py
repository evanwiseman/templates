"""Fake SQLAlchemy sessions for unit and API tests."""

# Standard library
from collections.abc import Callable, Generator
from dataclasses import dataclass, field
from typing import cast

# Third party
from sqlalchemy.orm import Session

# First party
from app.models.user import User


@dataclass
class RecordingSession:
    """In-memory session that records add/commit/refresh for assertions."""

    added: list[User] = field(default_factory=list)
    committed: bool = False
    _next_id: int = field(default=1, init=False)

    def add(self, obj: User) -> None:
        self.added.append(obj)

    def commit(self) -> None:
        self.committed = True

    def refresh(self, obj: User) -> None:
        obj.id = self._next_id
        self._next_id += 1


@dataclass
class ClosingSession:
    """Minimal session fake for testing generator cleanup."""

    closed: bool = False

    def close(self) -> None:
        self.closed = True


def as_session(fake: RecordingSession | ClosingSession) -> Session:
    """Cast a fake session to ``Session`` for type-checked call sites."""
    return cast(Session, fake)


def make_get_session_override(
    fake: RecordingSession,
) -> Callable[[], Generator[Session]]:
    """Build override for ``app.dependency_overrides[get_session]``."""

    def _override() -> Generator[Session]:
        yield as_session(fake)

    return _override
