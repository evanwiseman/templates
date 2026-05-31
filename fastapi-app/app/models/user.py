# Standard library
from datetime import date

# Third party
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

# Local
from .base import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    password_hash: Mapped[str] = mapped_column()
    created_at: Mapped[date] = mapped_column(server_default=func.now())
    updated_at: Mapped[date] = mapped_column(server_default=func.now())
