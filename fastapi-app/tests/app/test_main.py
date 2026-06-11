"""Tests for main."""

# Standard library
from unittest.mock import patch

# Third party
from fastapi.testclient import TestClient

# First party
import project_name.app.main as main_module
from project_name.app.core.config import Settings
from project_name.app.main import app, main


def test_root() -> None:
    """GET / returns the hello payload and runs the app lifespan."""
    with TestClient(app) as client:
        response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from fast-api"}


def test_main(settings: Settings) -> None:
    """``main()`` starts uvicorn with the app and settings."""
    with patch.object(main_module.uvicorn, "run") as mock_run:
        main()
    mock_run.assert_called_once_with(
        app,
        host=settings.app.host,
        port=settings.app.port,
        log_level=settings.log_level,
    )
