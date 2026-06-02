"""Test doubles for app dependencies."""

# Local
from .session import (
    ClosingSession,
    RecordingSession,
    as_session,
    make_get_session_override,
)

__all__ = [
    "ClosingSession",
    "RecordingSession",
    "as_session",
    "make_get_session_override",
]
