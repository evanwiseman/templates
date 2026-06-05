"""Tests for user_service."""

# Standard library
import http
from uuid import uuid7

# Third party
import pytest
from fastapi import HTTPException

# First party
from app.models.user import User
from app.schemas import UserCreate, UserUpdate
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

    def test_get_raises_when_not_found(self) -> None:
        """Get raises when the user id does not exist."""
        recording = RecordUserSession()
        missing_id = uuid7()

        with pytest.raises(HTTPException) as exc_info:
            UserService.get(as_session(recording), missing_id)

        assert exc_info.value.status_code == http.HTTPStatus.NOT_FOUND
        assert str(missing_id) in str(exc_info.value.detail)

    def test_update_raises_when_not_found(self) -> None:
        """Update raises when the user id does not exist."""
        recording = RecordUserSession()
        missing_id = uuid7()
        user_in = UserUpdate(username="alice", password="secret-password")

        with pytest.raises(HTTPException) as exc_info:
            UserService.update(as_session(recording), missing_id, user_in)

        assert exc_info.value.status_code == http.HTTPStatus.NOT_FOUND
        assert str(missing_id) in str(exc_info.value.detail)

    def test_get_all_paginates(self) -> None:
        """Get all returns a page of users and the total count."""
        recording = RecordUserSession()
        for index in range(5):
            recording.added.append(
                User(
                    id=uuid7(),
                    username=f"user-{index}",
                    password_hash="hashed",
                ),
            )

        users, total = UserService.get_all(
            as_session(recording),
            limit=2,
            offset=1,
        )

        assert total == 5
        assert len(users) == 2
        assert users[0].username == "user-1"
        assert users[1].username == "user-2"
