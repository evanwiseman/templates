"""Test doubles for app dependencies."""

# Local
from .session import ClosingSession
from .user import RecordUserSession, as_session, make_get_session_override

__all__ = [
    "ClosingSession",
    "RecordUserSession",
    "as_session",
    "make_get_session_override",
]
