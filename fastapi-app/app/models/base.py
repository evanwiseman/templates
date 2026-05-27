"""SQLAlchemy declarative base for ORM models."""

# Third party
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared metadata registry for all ORM models."""
