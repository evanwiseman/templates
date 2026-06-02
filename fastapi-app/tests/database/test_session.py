"""Tests for app.database.session."""

# Standard library
from unittest.mock import patch

# First party
from app.database.session import get_session
from tests.fakes import ClosingSession


def test_get_session_yields_session_and_closes() -> None:
    """get_session yields a DB session and closes it when the generator ends."""
    fake_db = ClosingSession()
    with patch("app.database.session.SessionLocal", return_value=fake_db):
        gen = get_session()
        assert next(gen) is fake_db
        gen.close()
    assert fake_db.closed
