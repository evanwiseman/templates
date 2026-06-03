"""Tests for user."""

# Standard library
import http

# Third party
from fastapi.testclient import TestClient

# First party
from app.database.session import get_session
from app.main import app
from app.schemas import UserRead
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
        user = UserRead.model_validate(response.json())
        assert user.username == user_data["username"]
        assert user.id == recording.added[0].id
        assert recording.committed
