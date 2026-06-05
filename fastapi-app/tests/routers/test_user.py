"""Tests for user."""

# Standard library
import http
from uuid import uuid7

# Third party
from fastapi.testclient import TestClient

# First party
from app.core.pagination import Page
from app.database.session import get_session
from app.main import app
from app.models.user import User
from app.schemas import UserShow
from tests.fakes import RecordUserSession, make_get_session_override

_USERS_URL = "/users/"


class TestCreateNewUser:
    def test_calls_user_service(self) -> None:
        """POST /users injects session via Depends(get_session)."""
        recording = RecordUserSession()
        app.dependency_overrides[get_session] = make_get_session_override(
            recording,
        )
        user_data = {
            "username": "alice",
            "password": "secret-password",
        }
        try:
            with TestClient(app) as client:
                response = client.post(
                    url=_USERS_URL,
                    json=user_data,
                )
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == http.HTTPStatus.CREATED
        user = UserShow.model_validate(response.json())
        assert user.username == user_data["username"]
        assert user.id == recording.added[0].id
        assert recording.committed


class TestListUsers:
    def test_returns_paginated_users(self) -> None:
        """GET /users returns a paginated user list."""
        recording = RecordUserSession()
        recording.added.append(
            User(
                id=uuid7(),
                username="alice",
                password_hash="hashed",
            ),
        )
        app.dependency_overrides[get_session] = make_get_session_override(
            recording,
        )
        try:
            with TestClient(app) as client:
                response = client.get(_USERS_URL)
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == http.HTTPStatus.OK
        page = Page[UserShow].model_validate(response.json())
        assert page.total == 1
        assert page.limit == 20
        assert page.offset == 0
        assert len(page.items) == 1
        assert page.items[0].username == "alice"


class TestGetUser:
    def test_returns_user(self) -> None:
        """GET /users/{user_id} returns the requested user."""
        user_id = uuid7()
        recording = RecordUserSession()
        recording.added.append(
            User(
                id=user_id,
                username="alice",
                password_hash="hashed",
            ),
        )
        app.dependency_overrides[get_session] = make_get_session_override(
            recording,
        )
        try:
            with TestClient(app) as client:
                response = client.get(f"{_USERS_URL}{user_id}")
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == http.HTTPStatus.OK
        user = UserShow.model_validate(response.json())
        assert user.id == user_id
        assert user.username == "alice"
