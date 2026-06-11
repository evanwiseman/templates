# Standard library
from datetime import datetime
from uuid import UUID, uuid7

# Third party
from sqlalchemy import Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

# First party
from project_name.app.database.base import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid7,
        index=True,
    )
    username: Mapped[str] = mapped_column(unique=True, index=True)
    password_hash: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now())
