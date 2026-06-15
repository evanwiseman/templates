# Standard library
from uuid import UUID

# Third party
from argon2.exceptions import HashingError
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.sql.selectable import Select

# First party
from project_name.app.core.errors import (
    InternalError,
)
from project_name.app.core.schemas import ListResult
from project_name.app.core.security import hash_password, verify_password

# Local
from .errors import (
    InvalidCredentialsError,
    UserConflictError,
    UserNotFoundError,
)
from .models import User
from .schemas import UserCreate, UserDestroy, UserUpdate


def _require_user(session: Session, user_id: UUID) -> User:
    db_user = session.get(User, user_id)
    if db_user is None:
        raise UserNotFoundError()
    return db_user


def _apply_update(user: User, params: UserUpdate) -> User:
    try:
        user.password_hash = hash_password(
            params.new_password.get_secret_value(),
        )
    except HashingError as exc:
        raise InternalError() from exc
    return user

def _list_query() -> Select[tuple[User]]:
    return select(User).order_by(User.created_at)

class UserService:
    @staticmethod
    def get(session: Session, user_id: UUID) -> User:
        return _require_user(session, user_id)

    @staticmethod
    def list(
        session: Session,
        *,
        limit: int,
        offset: int,
    ) -> ListResult[User]:
        stmt = _list_query()
        total = (
            session.scalar(
                select(func.count()).select_from(stmt.subquery()),
            )
            or 0
        )
        items = list(
            session.scalars(stmt.limit(limit).offset(offset)).all(),
        )
        return ListResult(items=items, total=total)

    @staticmethod
    def create(session: Session, user: UserCreate) -> User:
        db_user = User(
            username=user.username,
            password_hash=hash_password(user.password.get_secret_value()),
        )

        try:
            session.add(db_user)
            session.commit()
        except IntegrityError as exc:
            session.rollback()
            raise UserConflictError() from exc

        session.refresh(db_user)
        return db_user

    @staticmethod
    def update(session: Session, user_id: UUID, user: UserUpdate) -> User:
        db_user = _require_user(session, user_id)
        if not verify_password(db_user.password_hash, user.old_password):
            raise InvalidCredentialsError()

        db_user = _apply_update(db_user, user)
        session.commit()
        session.refresh(db_user)
        return db_user

    @staticmethod
    def destroy(session: Session, user_id: UUID, user: UserDestroy) -> None:
        db_user = _require_user(session, user_id)
        if not verify_password(db_user.password_hash, user.password):
            raise InvalidCredentialsError()

        session.delete(db_user)
        session.commit()
