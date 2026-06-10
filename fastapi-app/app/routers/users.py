"""User routes."""

# Standard library
from uuid import UUID

# Third party
from fastapi import APIRouter, HTTPException, status
from fastapi_pagination import LimitOffsetPage

# First party
from app.dependencies import PaginationParamsDep, SessionDep
from app.errors.user import (
    UserNotFoundError,
    UserUnauthorizedError,
    UserUpdateError,
)
from app.schemas import UserUpdate
from app.schemas.user import UserCreate, UserDestroy, UserShow
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserShow,
)
def get_user(user_id: UUID, session: SessionDep) -> UserShow:
    """Get a user with ``user_id``.

    Args:
        user_id (UUID): The user_id to fetch.
        session (SessionDep): The session dependency.

    Returns:
        UserShow: User model to show.
    """
    try:
        user = UserService.get(session, user_id)
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    return UserShow.model_validate(user)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=LimitOffsetPage[UserShow],
)
def get_users(
    session: SessionDep,
    params: PaginationParamsDep,
) -> LimitOffsetPage[UserShow]:
    """Get a list of users paginated.

    Args:
        session (SessionDep): The session dependency.
        params (PaginationParamsDep): The pagination params dependency.

    Returns:
        LimitOffsetPage[UserShow]: Paginated list of users with show.
    """
    result = UserService.list(
        session,
        limit=params.limit,
        offset=params.offset,
    )
    return LimitOffsetPage[UserShow].create(
        items=[UserShow.model_validate(user) for user in result.items],
        params=params,
        total=result.total,
    )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=UserShow,
)
def post_user(user: UserCreate, session: SessionDep) -> UserShow:
    """Create a user.

    Args:
        user (UserCreate): The parameters to create user.
        session (SessionDep): The session dependency.

    Returns:
        UserShow: User model to show.
    """
    created = UserService.create(session, user)
    return UserShow.model_validate(created)


@router.put(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserShow,
)
def put_user(
    user_id: UUID,
    user: UserUpdate,
    session: SessionDep,
) -> UserShow:
    """Update a user.

    Args:
        user_id (UUID): The user id to update.
        user (UserUpdate): The parameters to update user.
        session (SessionDep): The session dependency.

    Returns:
        UserShow: The user model to show.
    """
    try:
        updated = UserService.update(session, user_id, user)
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except UserUnauthorizedError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
    except UserUpdateError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
    return UserShow.model_validate(updated)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user(user_id: UUID, user: UserDestroy, session: SessionDep) -> None:
    """Delete a user.

    Args:
        user_id (UUID): The user_id to delete.
        user (UserDestroy): The parameters to destroy a user.
        session (SessionDep): The session dependency.
    """
    try:
        UserService.destroy(session, user_id, user)
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except UserUnauthorizedError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
