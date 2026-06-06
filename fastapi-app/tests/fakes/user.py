"""User-related test doubles."""

# Standard library
import re
from collections.abc import Callable, Generator
from dataclasses import dataclass, field
from typing import cast
from uuid import uuid7

# Third party
from sqlalchemy.orm import Session
from sqlalchemy.sql.selectable import Select

# First party
from app.models.user import User

_LIMIT_RE = re.compile(r"LIMIT (\d+)", re.IGNORECASE)
_OFFSET_RE = re.compile(r"OFFSET (\d+)", re.IGNORECASE)


@dataclass
class FakeScalarResult:
    items: list[User]

    def all(self) -> list[User]:
        return self.items


def _select_limit_offset(
    statement: Select[tuple[User]],
) -> tuple[int | None, int]:
    sql = str(statement.compile(compile_kwargs={"literal_binds": True}))
    limit_match = _LIMIT_RE.search(sql)
    offset_match = _OFFSET_RE.search(sql)
    limit = int(limit_match.group(1)) if limit_match else None
    offset = int(offset_match.group(1)) if offset_match else 0
    return limit, offset


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

    def scalar(self, _statement: object) -> int | None:
        return len(self.added)

    def scalars(self, statement: Select[tuple[User]]) -> FakeScalarResult:
        limit, offset = _select_limit_offset(statement)
        end = None if limit is None else offset + limit
        return FakeScalarResult(list(self.added)[offset:end])

    def commit(self) -> None:
        self.committed = True

    def delete(self, user: User) -> None:
        self.added.remove(user)

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
