"""Tests for user_service."""

# Standard library
from datetime import datetime, timedelta
from unittest.mock import patch
from uuid import uuid7

# Third party
import pytest
from argon2.exceptions import InvalidHashError
from sqlalchemy import select
from sqlalchemy.orm import Session

# First party
import project_name.app.features.users.services as services_module
from project_name.app.core.security import hash_password, verify_password
from project_name.app.features.users import (
    User,
    UserCreate,
    UserDestroy,
    UserNotFoundError,
    UserService,
    UserUnauthorizedError,
    UserUpdate,
    UserUpdateError,
)


class TestGet:
    def test_returns_user(self, db_session: Session) -> None:
        """Get returns the user when the id exists.

        Args:
            db_session (Session): Test session.
        """
        user = User(
            id=uuid7(),
            username="alice",
            password_hash="hashed",
        )
        db_session.add(user)
        db_session.flush()

        result = UserService.get(db_session, user.id)

        assert result.id == user.id
        assert result.username == "alice"

    def test_raises_when_not_found(self, db_session: Session) -> None:
        """Get raises when the user id does not exist.

        Args:
            db_session (Session): Test session.
        """
        missing_id = uuid7()

        with pytest.raises(UserNotFoundError) as exc_info:
            UserService.get(db_session, missing_id)

        assert exc_info.value.user_id == missing_id


class TestListQuery:
    def test_orders_users_by_created_at(self) -> None:
        """List query selects users ordered by created_at."""
        query = UserService.list_query()
        compiled = str(query.compile(compile_kwargs={"literal_binds": True}))

        assert "FROM users" in compiled
        assert "ORDER BY users.created_at" in compiled


class TestList:
    def test_list_chunks_users(self, db_session: Session) -> None:
        """List returns one chunk of users and the total count.

        Args:
            db_session (Session): Test session.
        """
        base_time = datetime(2026, 1, 1)
        for index in range(5):
            user = User(
                id=uuid7(),
                username=f"user-{index}",
                password_hash="hashed",
                created_at=base_time + timedelta(days=index),
            )
            db_session.add(user)
        db_session.commit()

        result = UserService.list(db_session, limit=2, offset=1)

        assert result.total == 5
        assert len(result.items) == 2
        assert result.items[0].username == "user-1"
        assert result.items[1].username == "user-2"


class TestCreate:
    def test_persists(self, db_session: Session) -> None:
        """Create stores the user data.

        Args:
            db_session (Session): Test session.
        """
        user_data = {
            "username": "alice",
            "password": "secret-password",
        }
        user_in = UserCreate(**user_data)
        created = UserService.create(db_session, user_in)

        stored = db_session.scalars(
            select(User).where(User.username == user_data["username"]),
        ).one()
        assert stored.id == created.id
        assert stored.password_hash != user_data["password"]


class TestUpdate:
    def test_persists(self, db_session: Session) -> None:
        """Update stores the new password when the old password matches.

        Args:
            db_session (Session): Test session.
        """
        old_password = "old-password"
        new_password = "new-password"
        user = User(
            id=uuid7(),
            username="alice",
            password_hash=hash_password(old_password),
        )

        db_session.add(user)
        db_session.commit()

        user_in = UserUpdate(
            old_password=old_password,
            new_password=new_password,
        )

        result = UserService.update(db_session, user.id, user_in)

        assert result.username == "alice"
        assert result.password_hash != new_password
        assert verify_password(result.password_hash, new_password)

    def test_raises_when_unauthorized(self, db_session: Session) -> None:
        """Update raises when the old password does not match.

        Args:
            db_session (Session): Test session.
        """
        user = User(
            id=uuid7(),
            username="alice",
            password_hash=hash_password("correct-password"),
        )
        db_session.add(user)
        db_session.commit()
        user_in = UserUpdate(
            old_password="wrong-password",
            new_password="new-password",
        )

        with pytest.raises(UserUnauthorizedError) as exc_info:
            UserService.update(db_session, user.id, user_in)

        assert exc_info.value.user_id == user.id

    def test_raises_when_hash_fails(self, db_session: Session) -> None:
        """Update raises when password hashing fails.

        Args:
            db_session (Session): Test session.
        """
        old_password = "old-password"
        user = User(
            id=uuid7(),
            username="alice",
            password_hash=hash_password(old_password),
        )
        db_session.add(user)
        db_session.commit()
        user_in = UserUpdate(
            old_password=old_password,
            new_password="new-password",
        )

        with (
            patch.object(
                services_module,
                "hash_password",
                side_effect=InvalidHashError(),
            ),
            pytest.raises(UserUpdateError) as exc_info,
        ):
            UserService.update(db_session, user.id, user_in)

        assert exc_info.value.user_id == user.id

    def test_raises_when_not_found(self, db_session: Session) -> None:
        """Update raises when the user id does not exist.

        Args:
            db_session (Session): Test session.
        """
        missing_id = uuid7()
        user_in = UserUpdate(
            old_password="old-password",
            new_password="secret-password",
        )

        with pytest.raises(UserNotFoundError) as exc_info:
            UserService.update(db_session, missing_id, user_in)

        assert exc_info.value.user_id == missing_id


class TestDestroy:
    def test_removes_user(self, db_session: Session) -> None:
        """Destroy deletes the user when the password matches.

        Args:
            db_session (Session): Test session.
        """
        password = "secret-password"
        user = User(
            id=uuid7(),
            username="alice",
            password_hash=hash_password(password),
        )
        db_session.add(user)
        db_session.commit()

        UserService.destroy(
            db_session,
            user.id,
            UserDestroy(password=password),
        )

        assert db_session.get(User, user.id) is None

    def test_raises_when_unauthorized(self, db_session: Session) -> None:
        """Destroy raises when the password does not match.

        Args:
            db_session (Session): Test session.
        """
        user = User(
            id=uuid7(),
            username="alice",
            password_hash=hash_password("correct-password"),
        )
        db_session.add(user)
        db_session.commit()

        with pytest.raises(UserUnauthorizedError) as exc_info:
            UserService.destroy(
                db_session,
                user.id,
                UserDestroy(password="wrong-password"),
            )

        assert exc_info.value.user_id == user.id

    def test_raises_when_not_found(self, db_session: Session) -> None:
        """Destroy raises when the user id does not exist.

        Args:
            db_session (Session): Test session.
        """
        missing_id = uuid7()

        with pytest.raises(UserNotFoundError) as exc_info:
            UserService.destroy(
                db_session,
                missing_id,
                UserDestroy(password="secret-password"),
            )

        assert exc_info.value.user_id == missing_id
