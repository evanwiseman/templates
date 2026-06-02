"""Tests for app.services.user_service."""

# Standard library
from dataclasses import dataclass, field
from typing import cast

# Third party
from sqlalchemy.orm import Session

# First party
from app.models.user import User
from app.schemas import UserCreate
from app.services.user_service import UserService


@dataclass
class _RecordingSession:
    added: list[User] = field(default_factory=list)
    committed: bool = False

    def add(self, obj: User) -> None:
        self.added.append(obj)

    def commit(self) -> None:
        self.committed = True

    def refresh(self, obj: User) -> None:
        obj.id = len(self.added)


def test_create_hashes_password_and_persists() -> None:
    """create stores a hashed password and commits the row."""
    recording = _RecordingSession()
    user_in = UserCreate(
        username="alice",
        password="secret-password",
    )

    created = UserService.create(
        cast(Session, recording),
        user_in,
    )

    assert created.username == "alice"
    assert recording.added[0].password_hash != user_in.password
    assert recording.committed is True
