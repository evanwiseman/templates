"""Tests for user."""

# Standard library
import http
from unittest.mock import patch
from uuid import uuid7

# Third party
from fastapi.testclient import TestClient
from fastapi_pagination import LimitOffsetPage
from pydantic import TypeAdapter
from sqlalchemy import select
from sqlalchemy.orm import Session

# First party
from app.core.security import hash_password, verify_password
from app.features.users import User, UserShow, UserUpdateError

_USERS_URL = "/users/"
UserPage = TypeAdapter(LimitOffsetPage[UserShow])


class TestGetUser:
    def test_returns_user(
        self,
        client: TestClient,
        db_session: Session,
    ) -> None:
        """GET /users/{user_id} returns requested user.

        Args:
            client (TestClient): Test client.
            db_session (Session): Test session.
        """
        db_user = User(
            id=uuid7(),
            username="alice",
            password_hash="hashed",
        )
        db_session.add(db_user)
        db_session.commit()

        response = client.get(f"{_USERS_URL}{db_user.id}")
        assert response.status_code == http.HTTPStatus.OK

        user = UserShow.model_validate(response.json())
        assert user.id == db_user.id
        assert user.username == db_user.username

    def test_returns_not_found(self, client: TestClient) -> None:
        """GET /users/{user_id} returns 404 when user does not exist.

        Args:
            client (TestClient): Test client.
        """
        missing_id = uuid7()

        response = client.get(f"{_USERS_URL}{missing_id}")

        assert response.status_code == http.HTTPStatus.NOT_FOUND


class TestGetUsers:
    def test_returns_paginated_users(
        self,
        client: TestClient,
        db_session: Session,
    ) -> None:
        """GET /users returns paginated user list.

        Args:
            client (TestClient): Test client.
            db_session (Session): Test session.
        """
        db_user = User(
            id=uuid7(),
            username="alice",
            password_hash="hashed",
        )
        db_session.add(db_user)
        db_session.commit()

        response = client.get(_USERS_URL)
        assert response.status_code == http.HTTPStatus.OK

        page = UserPage.validate_python(response.json())
        assert page.total == 1
        assert page.limit == 50
        assert page.offset == 0
        assert len(page.items) == 1
        assert page.items[0].username == db_user.username


class TestPostUser:
    def test_creates_user(
        self,
        client: TestClient,
        db_session: Session,
    ) -> None:
        """POST /users creates user.

        Args:
            client (TestClient): Test client.
            db_session (Session): Test session.
        """
        user_data = {
            "username": "alice",
            "password": "secret-password",
        }
        response = client.post(url=_USERS_URL, json=user_data)
        assert response.status_code == http.HTTPStatus.CREATED

        user = UserShow.model_validate(response.json())
        assert user.username == user_data["username"]
        stored = db_session.scalars(
            select(User).where(User.username == user_data["username"]),
        ).one()
        assert stored.id == user.id


class TestPutUser:
    def test_updates_user(
        self,
        client: TestClient,
        db_session: Session,
    ) -> None:
        """PUT /users/{user_id} updates user.

        Args:
            client (TestClient): Test client.
            db_session (Session): Test session.
        """
        old_password = "old-password"
        new_password = "new-password"
        db_user = User(
            id=uuid7(),
            username="alice",
            password_hash=hash_password(old_password),
        )
        db_session.add(db_user)
        db_session.commit()

        response = client.put(
            f"{_USERS_URL}{db_user.id}",
            json={
                "old_password": old_password,
                "new_password": new_password,
            },
        )
        assert response.status_code == http.HTTPStatus.OK

        user = UserShow.model_validate(response.json())
        assert user.id == user.id
        assert user.username == db_user.username

        stored = db_session.get(User, user.id)
        assert stored is not None
        assert verify_password(stored.password_hash, new_password)

    def test_returns_not_found(self, client: TestClient) -> None:
        """PUT /users/{user_id} returns 404 when user does not exist.

        Args:
            client (TestClient): Test client.
            db_session (Session): Test session.
        """
        missing_id = uuid7()

        response = client.put(
            f"{_USERS_URL}{missing_id}",
            json={
                "old_password": "old-password",
                "new_password": "new-password",
            },
        )

        assert response.status_code == http.HTTPStatus.NOT_FOUND

    def test_returns_unauthorized(
        self,
        client: TestClient,
        db_session: Session,
    ) -> None:
        """PUT /users/{user_id} returns 401 when password is wrong.

        Args:
            client (TestClient): Test client.
            db_session (Session): Test session.
        """
        db_user = User(
            id=uuid7(),
            username="alice",
            password_hash=hash_password("correct-password"),
        )
        db_session.add(db_user)
        db_session.commit()

        response = client.put(
            f"{_USERS_URL}{db_user.id}",
            json={
                "old_password": "wrong-password",
                "new_password": "new-password",
            },
        )

        assert response.status_code == http.HTTPStatus.UNAUTHORIZED

    def test_returns_update_error(
        self,
        client: TestClient,
        db_session: Session,
    ) -> None:
        """PUT /users/{user_id} returns 500 on update error.

        Args:
            client (TestClient): Test client.
            db_session (Session): Test session.
        """
        db_user = User(
            id=uuid7(),
            username="alice",
            password_hash=hash_password("secret-password"),
        )
        db_session.add(db_user)
        db_session.commit()

        with patch(
            "app.features.users.router.UserService.update",
            side_effect=UserUpdateError(db_user.id),
        ):
            response = client.put(
                f"{_USERS_URL}{db_user.id}",
                json={
                    "old_password": "secret-password",
                    "new_password": "new-password",
                },
            )

        assert response.status_code == http.HTTPStatus.INTERNAL_SERVER_ERROR


class TestDeleteUser:
    def test_deletes_user(
        self,
        client: TestClient,
        db_session: Session,
    ) -> None:
        """DELETE /users/{user_id} removes user.

        Args:
            client (TestClient): Test client.
            db_session (Session): Test session.
        """
        password = "secret-password"
        db_user = User(
            id=uuid7(),
            username="alice",
            password_hash=hash_password(password),
        )
        db_session.add(db_user)
        db_session.commit()
        user_id = db_user.id

        response = client.request(
            "DELETE",
            f"{_USERS_URL}{user_id}",
            json={"password": password},
        )
        assert response.status_code == http.HTTPStatus.NO_CONTENT
        assert db_session.get(User, user_id) is None

    def test_returns_not_found(self, client: TestClient) -> None:
        """DELETE /users/{user_id} returns 404 when user does not exist.

        Args:
            client (TestClient): Test client.
            db_session (Session): Test session.
        """
        missing_id = uuid7()

        response = client.request(
            "DELETE",
            f"{_USERS_URL}{missing_id}",
            json={"password": "secret-password"},
        )

        assert response.status_code == http.HTTPStatus.NOT_FOUND

    def test_returns_unauthorized(
        self,
        client: TestClient,
        db_session: Session,
    ) -> None:
        """DELETE /users/{user_id} returns 401 when password is wrong.

        Args:
            client (TestClient): Test client.
            db_session (Session): Test session.
        """
        user_id = uuid7()
        db_user = User(
            id=user_id,
            username="alice",
            password_hash=hash_password("correct-password"),
        )
        db_session.add(db_user)
        db_session.commit()

        response = client.request(
            "DELETE",
            f"{_USERS_URL}{user_id}",
            json={"password": "wrong-password"},
        )

        assert response.status_code == http.HTTPStatus.UNAUTHORIZED
