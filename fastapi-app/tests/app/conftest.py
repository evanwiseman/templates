"""Shared pytest fixtures."""

# Standard library
import os

# Third party
import pytest

# Set before importing settings.
os.environ["APP_ENV"] = "dev"
os.environ["APP_HOST"] = "127.0.0.1"
os.environ["APP_PORT"] = "8000"
os.environ["LOG_LEVEL"] = "INFO"
os.environ["DB_URL"] = (
    "postgresql+psycopg://user:pass@localhost:5432/fastapi_app"
)

# First party
from app.core.config import AppSettings, DatabaseSettings, Settings
from app.core.config.settings import settings as config


@pytest.fixture
def app_settings() -> AppSettings:
    """App settings loaded for tests (via env, not ``.env``)."""
    return config.app


@pytest.fixture
def database_settings() -> DatabaseSettings:
    """Database settings loaded for tests (via env, not ``.env``)."""
    return config.db


@pytest.fixture
def settings() -> Settings:
    """Root settings loaded for tests (via env, not ``.env``)."""
    return config
