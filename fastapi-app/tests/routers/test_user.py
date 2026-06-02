"""Tests for app.routers.user."""

# Third party
from fastapi.testclient import TestClient
from tests.fakes import RecordingSession, make_get_session_override

# First party
from app.database.session import get_session
from app.main import app


def test_create_new_user_calls_user_service() -> None:
    """POST /users injects session via Depends(get_session)."""
    recording = RecordingSession()
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
    assert response.json() == {"id": 1, "username": "alice"}
    assert recording.committed is True
