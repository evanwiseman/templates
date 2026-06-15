"""User domain errors."""

# Standard library


# First party
from project_name.app.core.errors import (
    ConflictError,
    NotFoundError,
    UnauthorizedError,
)


class UserConflictError(ConflictError):
    detail = "User already exists"


class UserNotFoundError(NotFoundError):
    detail = "User not found"


class InvalidCredentialsError(UnauthorizedError):
    detail = "Invalid credentials"
