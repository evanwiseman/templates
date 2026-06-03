"""Tests for user_service."""

# First party
from app.schemas import UserCreate
from app.services.user_service import UserService
from tests.fakes import RecordUserSession, as_session


class TestUserService:
    def test_create_persists(self) -> None:
        """Create stores the user data."""
        recording = RecordUserSession()
        user_data = {
            "username": "alice",
            "password": "secret-password",
        }
        user_in = UserCreate(**user_data)
        _ = UserService.create(
            as_session(recording),
            user_in,
        )

        is_commited = recording.committed
        assert is_commited
        assert recording.added[0].username == user_data["username"]
        assert recording.added[0].password_hash != user_data["password"]
