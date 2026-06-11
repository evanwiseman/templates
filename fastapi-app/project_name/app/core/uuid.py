"""UUID helpers with RFC 9562 v7 support on Python 3.12+."""

# Standard library
import importlib
import sys
from collections.abc import Callable
from typing import cast
from uuid import UUID

_UUID7_ATTR = "uuid7"


def uuid7() -> UUID:
    """Generate a monotonic time-ordered UUID (RFC 9562 version 7)."""
    module_name = "uuid" if sys.version_info >= (3, 14) else "uuid_backport"
    module = importlib.import_module(module_name)
    uuid7_fn = cast(Callable[[], UUID], getattr(module, _UUID7_ATTR))
    return uuid7_fn()


__all__ = ["UUID", "uuid7"]
