"""Tests for app.database.engine."""

# First party
from app.core.config import settings
from app.database.engine import SessionLocal, engine


def test_engine_uses_settings_url() -> None:
    """Engine is created from the configured database URL."""
    assert str(engine.url) == str(settings.db.url)


def test_session_local_bound_to_engine() -> None:
    """Session factory is bound to the shared engine."""
    assert SessionLocal.kw["bind"] is engine
