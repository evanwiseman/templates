"""Tests for engine."""

# First party
from project_name.app.core.config import Settings
from project_name.app.database.engine import SessionLocal, engine


class TestEngine:
    def test_uses_settings_url(self, settings: Settings) -> None:
        """Engine is created from the configured database URL."""
        assert engine.url.render_as_string(hide_password=False) == str(
            settings.db.url
        )

    def test_session_local_bound_to_engine(self) -> None:
        """Session factory is bound to the shared engine."""
        assert SessionLocal.kw["bind"] is engine
