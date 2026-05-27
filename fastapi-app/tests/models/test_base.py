"""Tests for app.models."""

# Third party
from sqlalchemy.orm import DeclarativeBase

# First party
from app.models import Base


class TestBase:
    def test_exported_from_package(self) -> None:
        """Base is the declarative registry for ORM models."""
        assert Base is not None
        assert issubclass(Base, DeclarativeBase)
        assert Base.metadata is not None
