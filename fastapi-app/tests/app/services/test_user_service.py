"""Tests for user_service."""

# Standard library
import http
from unittest.mock import patch
from uuid import uuid7

# Third party
import pytest
from argon2.exceptions import InvalidHashError
from fastapi import HTTPException
from fastapi_pagination import LimitOffsetParams

# First party
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas import UserCreate, UserUpdate
from app.schemas.users import UserDestroy
from app.services.user_service import UserService
from tests.app.fakes import RecordUserSession, as_session


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

    def test_get_returns_user(self) -> None:
        """Get returns the user when the id exists."""
        user_id = uuid7()
        recording = RecordUserSession()
        db_user = User(
            id=user_id,
            username="alice",
            password_hash="hashed",
        )
        recording.added.append(db_user)

        result = UserService.get(as_session(recording), user_id)

        assert result is db_user

    def test_get_raises_when_not_found(self) -> None:
        """Get raises when the user id does not exist."""
        recording = RecordUserSession()
        missing_id = uuid7()

        with pytest.raises(HTTPException) as exc_info:
            UserService.get(as_session(recording), missing_id)

        assert exc_info.value.status_code == http.HTTPStatus.NOT_FOUND
        assert str(missing_id) in str(exc_info.value.detail)

    def test_update_persists(self) -> None:
        """Update stores the new password when the old password matches."""
        old_password = "old-password"
        new_password = "new-password"
        user_id = uuid7()
        recording = RecordUserSession()
        recording.added.append(
            User(
                id=user_id,
                username="alice",
                password_hash=hash_password(old_password),
            ),
        )
        user_in = UserUpdate(
            old_password=old_password,
            new_password=new_password,
        )

        result = UserService.update(
            as_session(recording),
            user_id,
            user_in,
        )

        assert recording.committed
        assert result.username == "alice"
        assert result.password_hash != new_password
        assert verify_password(result.password_hash, new_password)

    def test_update_raises_when_unauthorized(self) -> None:
        """Update raises when the old password does not match."""
        user_id = uuid7()
        recording = RecordUserSession()
        recording.added.append(
            User(
                id=user_id,
                username="alice",
                password_hash=hash_password("correct-password"),
            ),
        )
        user_in = UserUpdate(
            old_password="wrong-password",
            new_password="new-password",
        )

        with pytest.raises(HTTPException) as exc_info:
            UserService.update(as_session(recording), user_id, user_in)

        assert exc_info.value.status_code == http.HTTPStatus.UNAUTHORIZED
        assert str(user_id) in str(exc_info.value.detail)

    def test_update_raises_when_hash_fails(self) -> None:
        """Update raises when password hashing fails."""
        old_password = "old-password"
        user_id = uuid7()
        recording = RecordUserSession()
        recording.added.append(
            User(
                id=user_id,
                username="alice",
                password_hash=hash_password(old_password),
            ),
        )
        user_in = UserUpdate(
            old_password=old_password,
            new_password="new-password",
        )

        with (
            patch(
                "app.services.user_service.hash_password",
                side_effect=InvalidHashError(),
            ),
            pytest.raises(HTTPException) as exc_info,
        ):
            UserService.update(as_session(recording), user_id, user_in)

        assert (
            exc_info.value.status_code == http.HTTPStatus.INTERNAL_SERVER_ERROR
        )
        assert str(user_id) in str(exc_info.value.detail)

    def test_update_raises_when_not_found(self) -> None:
        """Update raises when the user id does not exist."""
        recording = RecordUserSession()
        missing_id = uuid7()
        user_in = UserUpdate(
            old_password="old-password",
            new_password="secret-password",
        )

        with pytest.raises(HTTPException) as exc_info:
            UserService.update(as_session(recording), missing_id, user_in)

        assert exc_info.value.status_code == http.HTTPStatus.NOT_FOUND
        assert str(missing_id) in str(exc_info.value.detail)

    def test_get_pages_paginates(self) -> None:
        """Get pages returns one page of users and the total count."""
        recording = RecordUserSession()
        users = [
            User(
                id=uuid7(),
                username=f"user-{index}",
                password_hash="hashed",
            )
            for index in range(5)
        ]
        recording.added.extend(users)
        params = LimitOffsetParams(limit=2, offset=1)

        page = UserService.get_pages(
            as_session(recording),
            params=params,
        )

        assert page.total == 5
        assert page.limit == 2
        assert page.offset == 1
        assert len(page.items) == 2
        assert page.items[0].username == "user-1"
        assert page.items[1].username == "user-2"

    def test_destroy_removes_user(self) -> None:
        """Destroy deletes the user when the password matches."""
        password = "secret-password"
        user_id = uuid7()
        recording = RecordUserSession()
        recording.added.append(
            User(
                id=user_id,
                username="alice",
                password_hash=hash_password(password),
            ),
        )

        UserService.destroy(
            as_session(recording),
            user_id,
            UserDestroy(password=password),
        )

        assert recording.committed
        assert recording.added == []

    def test_destroy_raises_when_unauthorized(self) -> None:
        """Destroy raises when the password does not match."""
        user_id = uuid7()
        recording = RecordUserSession()
        recording.added.append(
            User(
                id=user_id,
                username="alice",
                password_hash=hash_password("correct-password"),
            ),
        )

        with pytest.raises(HTTPException) as exc_info:
            UserService.destroy(
                as_session(recording),
                user_id,
                UserDestroy(password="wrong-password"),
            )

        assert exc_info.value.status_code == http.HTTPStatus.UNAUTHORIZED
        assert str(user_id) in str(exc_info.value.detail)

    def test_destroy_raises_when_not_found(self) -> None:
        """Destroy raises when the user id does not exist."""
        recording = RecordUserSession()
        missing_id = uuid7()

        with pytest.raises(HTTPException) as exc_info:
            UserService.destroy(
                as_session(recording),
                missing_id,
                UserDestroy(password="secret-password"),
            )

        assert exc_info.value.status_code == http.HTTPStatus.NOT_FOUND
        assert str(missing_id) in str(exc_info.value.detail)
