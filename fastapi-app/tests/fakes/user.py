"""User-related test doubles."""

# Standard library
from collections.abc import Callable, Generator
from dataclasses import dataclass, field
from typing import cast
from uuid import uuid7

# Third party
from sqlalchemy.orm import Session

# First party
from app.models.user import User


@dataclass
class RecordUserSession:
    """In-memory session that records user persistence for assertions."""

    added: list[User] = field(default_factory=list)
    committed: bool = False

    def add(self, user: User) -> None:
        self.added.append(user)

    def commit(self) -> None:
        self.committed = True

    def refresh(self, user: User) -> None:
        user.id = uuid7()


def as_session(fake: RecordUserSession) -> Session:
    """Cast a fake user session to ``Session`` for type-checked call sites."""
    return cast(Session, fake)


def make_get_session_override(
    fake: RecordUserSession,
) -> Callable[[], Generator[Session]]:
    """Build override for ``app.dependency_overrides[get_session]``."""

    def _override() -> Generator[Session]:
        yield as_session(fake)

    return _override
