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
class FakeUserQuery:
    users: list[User]
    limit_value: int | None = None
    offset_value: int = 0

    def limit(self, value: int) -> FakeUserQuery:
        return FakeUserQuery(
            self.users,
            limit_value=value,
            offset_value=self.offset_value,
        )

    def offset(self, value: int) -> FakeUserQuery:
        return FakeUserQuery(
            self.users,
            limit_value=self.limit_value,
            offset_value=value,
        )

    def all(self) -> list[User]:
        end = (
            None
            if self.limit_value is None
            else self.offset_value + self.limit_value
        )
        return self.users[self.offset_value : end]

    def count(self) -> int:
        return len(self.users)


@dataclass
class RecordUserSession:
    """In-memory session that records user persistence for assertions."""

    added: list[User] = field(default_factory=list)
    committed: bool = False

    def add(self, user: User) -> None:
        self.added.append(user)

    def get(self, model: type[User], ident: object) -> User | None:
        if model is not User:
            return None
        for user in self.added:
            if user.id == ident:
                return user
        return None

    def query(self, model: type[User]) -> FakeUserQuery:
        if model is not User:
            return FakeUserQuery([])
        return FakeUserQuery(list(self.added))

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
