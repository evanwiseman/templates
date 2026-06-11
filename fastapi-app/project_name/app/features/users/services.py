# Standard library
from typing import NamedTuple
from uuid import UUID

# Third party
from argon2.exceptions import (
    InvalidHashError,
    VerificationError,
    VerifyMismatchError,
)
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from sqlalchemy.sql.selectable import Select

# First party
from project_name.app.core.security import hash_password, verify_password

# Local
from .errors import (
    UserAlreadyExistsError,
    UserNotFoundError,
    UserUnauthorizedError,
    UserUpdateError,
)
from .models import User
from .schemas import UserCreate, UserDestroy, UserUpdate


class UserListResult(NamedTuple):
    items: list[User]
    total: int


def _require_user(session: Session, user_id: UUID) -> User:
    db_user = session.get(User, user_id)
    if db_user is None:
        raise UserNotFoundError(user_id)
    return db_user


def _validate_password(
    user_id: UUID,
    password_hash: str,
    password: str,
) -> None:
    if not verify_password(
        password_hash,
        password,
    ):
        raise UserUnauthorizedError(user_id)


def _apply_update(user: User, params: UserUpdate) -> User:
    try:
        user.password_hash = hash_password(params.new_password)
    except (
        VerifyMismatchError,
        VerificationError,
        InvalidHashError,
    ) as exc:
        raise UserUpdateError(user.id) from exc
    return user


class UserService:
    @staticmethod
    def get(session: Session, user_id: UUID) -> User:
        return _require_user(session, user_id)

    @staticmethod
    def list_query() -> Select[tuple[User]]:
        return select(User).order_by(User.created_at)

    @staticmethod
    def list(
        session: Session,
        *,
        limit: int,
        offset: int,
    ) -> UserListResult:
        query = UserService.list_query()
        total = (
            session.scalar(
                select(func.count()).select_from(query.subquery()),
            )
            or 0
        )
        items = list(
            session.scalars(query.limit(limit).offset(offset)).all(),
        )
        return UserListResult(items=items, total=total)

    @staticmethod
    def create(session: Session, user: UserCreate) -> User:
        maybe_db_user = session.scalar(
            select(User).where(User.username == user.username)
        )
        if maybe_db_user is not None:
            raise UserAlreadyExistsError()

        db_user = User(
            username=user.username,
            password_hash=hash_password(user.password),
        )

        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user

    @staticmethod
    def update(session: Session, user_id: UUID, user: UserUpdate) -> User:
        db_user = _require_user(session, user_id)
        _validate_password(user_id, db_user.password_hash, user.old_password)
        db_user = _apply_update(db_user, user)

        session.commit()
        session.refresh(db_user)
        return db_user

    @staticmethod
    def destroy(session: Session, user_id: UUID, user: UserDestroy) -> None:
        db_user = _require_user(session, user_id)
        _validate_password(user_id, db_user.password_hash, user.password)

        session.delete(db_user)
        session.commit()
