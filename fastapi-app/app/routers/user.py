"""User routes."""

# Standard library
from uuid import UUID

# Third party
from fastapi import APIRouter, status

# First party
from app.core.pagination import Page, PaginationDep
from app.database import SessionDep
from app.schemas.users import UserCreate, UserShow
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=UserShow,
)
def post_user(user: UserCreate, session: SessionDep) -> UserShow:
    """Create a user."""
    created = UserService.create(session, user)
    return UserShow.model_validate(created)


@router.get(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserShow,
)
def get_user(user_id: UUID, session: SessionDep) -> UserShow:
    """Get a user."""
    user = UserService.get(session, user_id)
    return UserShow.model_validate(user)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=Page[UserShow],
)
def list_users(
    session: SessionDep,
    pagination: PaginationDep,
) -> Page[UserShow]:
    """List users."""
    users, total = UserService.get_all(
        session,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return Page(
        items=[UserShow.model_validate(user) for user in users],
        total=total,
        limit=pagination.limit,
        offset=pagination.offset,
    )
