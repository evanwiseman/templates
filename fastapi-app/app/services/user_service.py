# Standard library
from uuid import UUID

# Third party
from argon2.exceptions import (
    InvalidHashError,
    VerificationError,
    VerifyMismatchError,
)
from fastapi import HTTPException, status
from fastapi_pagination import LimitOffsetPage, LimitOffsetParams
from sqlalchemy import func, select
from sqlalchemy.orm import Session

# First party
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.users import UserCreate, UserDestroy, UserUpdate


def _require_user(session: Session, user_id: UUID) -> User:
    db_user = session.get(User, user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found: {user_id}",
        )
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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"User unauthorized: {user_id}",
        )


def _apply_update(user: User, params: UserUpdate) -> User:
    try:
        user.password_hash = hash_password(params.new_password)
    except (
        VerifyMismatchError,
        VerificationError,
        InvalidHashError,
    ) as exc:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to update user: {user.id}",
        ) from exc
    return user


class UserService:
    @staticmethod
    def get(session: Session, user_id: UUID) -> User:
        return _require_user(session, user_id)

    @staticmethod
    def get_pages(
        session: Session,
        *,
        params: LimitOffsetParams,
    ) -> LimitOffsetPage[User]:
        query = select(User).order_by(User.created_at)
        total = session.scalar(select(func.count()).select_from(User)) or 0
        users = session.scalars(
            query.limit(params.limit).offset(params.offset),
        ).all()
        return LimitOffsetPage.create(
            items=list(users),
            params=params,
            total=total,
        )

    @staticmethod
    def create(session: Session, user: UserCreate) -> User:
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
