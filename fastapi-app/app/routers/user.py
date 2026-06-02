"""User routes."""

# Third party
from fastapi import APIRouter, status

# First party
from app.database import SessionDep
from app.schemas import UserCreate, UserRead
from app.services import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=UserRead,
)
def create_new_user(user: UserCreate, session: SessionDep) -> UserRead:
    """Create a user."""
    created = UserService.create(session, user)
    return UserRead.model_validate(created)
