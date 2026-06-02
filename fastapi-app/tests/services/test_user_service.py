"""Tests for app.services.user_service."""

# First party
from app.schemas import UserCreate
from app.services.user_service import UserService
from tests.fakes import RecordingSession, as_session


def test_create_hashes_password_and_persists() -> None:
    """create stores a hashed password and commits the row."""
    recording = RecordingSession()
    user_in = UserCreate(
        username="alice",
        password="secret-password",
    )

    created = UserService.create(
        as_session(recording),
        user_in,
    )

    assert created.username == "alice"
    assert recording.added[0].password_hash != user_in.password
    assert recording.committed is True
