# Third party
from sqlalchemy.orm import Session

# First party
from app.core.security import hash_password
from app.models.user import User
from app.schemas import UserCreate


class UserService:
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
