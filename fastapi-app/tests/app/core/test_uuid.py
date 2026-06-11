"""Tests for core UUID helpers."""

# Standard library
from uuid import UUID

# First party
from project_name.app.core.uuid import uuid7


class TestUuid7:
    def test_returns_uuid_instance(self) -> None:
        """uuid7 returns a standard UUID object."""
        assert isinstance(uuid7(), UUID)

    def test_generates_unique_values(self) -> None:
        """Each call produces a distinct UUID."""
        assert uuid7() != uuid7()
