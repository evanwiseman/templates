"""ORM models.

Import model modules here so Alembic autogenerate discovers them, e.g.:

    from app.models.user import User  # noqa: F401
"""

# First party
from app.models.base import Base

__all__ = ["Base"]
