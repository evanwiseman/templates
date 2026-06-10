"""Shared pytest fixtures."""

# Standard library
import os
from collections.abc import Generator

# Third party
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

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
from app.database.session import get_session
from app.main import app
from app.models import Base

_TEST_DATABASE_URL = "sqlite:///:memory:"


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


@pytest.fixture
def db_engine() -> Generator[Engine]:
    """In-memory SQLite engine with schema created per test."""
    engine = create_engine(
        _TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def db_session(db_engine: Engine) -> Generator[Session]:
    """Database session bound to the in-memory test engine."""
    session = Session(db_engine)
    yield session
    session.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient]:
    """HTTP client with ``get_session`` overridden to the test database."""

    def override_get_session() -> Generator[Session]:
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
