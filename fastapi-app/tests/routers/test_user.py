"""Tests for app.routers.user."""

# Third party
from fastapi.testclient import TestClient
from tests.fakes import RecordUserSession, make_get_session_override

# First party
from app.database.session import get_session
from app.main import app
from app.schemas import UserRead


def test_create_new_user_calls_user_service() -> None:
    """POST /users injects session via Depends(get_session)."""
    recording = RecordUserSession()
    app.dependency_overrides[get_session] = make_get_session_override(
        recording,
    )
    try:
        with TestClient(app) as client:
            response = client.post(
                "/users/",
                json={"username": "alice", "password": "secret-password"},
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    user = UserRead.model_validate(response.json())
    assert user.username == "alice"
    assert user.id == recording.added[0].id
    assert recording.committed is True
