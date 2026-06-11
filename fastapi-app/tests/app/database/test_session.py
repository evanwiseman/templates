"""Tests for session."""

# Standard library
from dataclasses import dataclass
from unittest.mock import patch

# First party
import project_name.app.database.session as session_module
from project_name.app.database.session import get_session


@dataclass
class _ClosingSession:
    """Minimal session fake for testing generator cleanup."""

    closed: bool = False

    def close(self) -> None:
        self.closed = True


class TestGetSession:
    def test_yields_session_and_closes(self) -> None:
        """get_session yields a DB session and closes it when the generator ends."""
        fake_db = _ClosingSession()
        with patch.object(
            session_module, "SessionLocal", return_value=fake_db
        ):
            gen = get_session()
            assert next(gen) is fake_db
            gen.close()
        assert fake_db.closed
