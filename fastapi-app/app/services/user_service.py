# Standard library
from uuid import UUID

# Third party
from fastapi import HTTPException, status
from fastapi_pagination import LimitOffsetPage, LimitOffsetParams
from sqlalchemy import func, select
from sqlalchemy.orm import Session

# First party
from app.core.security import hash_password
from app.models.user import User
from app.schemas.users import UserCreate, UserUpdate


class UserService:
    @staticmethod
    def get(session: Session, user_id: UUID) -> User:
        db_user = session.get(User, user_id)
        if db_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User not found: {user_id}",
            )
        return db_user

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
    def update(
        session: Session,
        user_id: UUID,
        user: UserUpdate,
    ) -> User:
        db_user = session.get(User, user_id)
        if db_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User not found: {user_id}",
            )

        db_user.username = user.username
        db_user.password_hash = hash_password(user.password)

        session.commit()
        session.refresh(db_user)
        return db_user

    @staticmethod
    def destroy(session: Session, user_id: UUID) -> None:
        db_user = session.get(User, user_id)
        if db_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User not found: {user_id}",
            )
        session.delete(db_user)
        session.commit()
