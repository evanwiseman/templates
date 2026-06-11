"""User domain errors."""

# Standard library
from uuid import UUID


class UserAlreadyExistsError(Exception):
    def __init__(self) -> None:
        super().__init__("User already exists")


class UserNotFoundError(Exception):
    def __init__(self, user_id: UUID) -> None:
        self.user_id = user_id
        super().__init__(f"User not found: {user_id}")


class UserUnauthorizedError(Exception):
    def __init__(self, user_id: UUID) -> None:
        self.user_id = user_id
        super().__init__(f"User unauthorized: {user_id}")


class UserUpdateError(Exception):
    def __init__(self, user_id: UUID) -> None:
        self.user_id = user_id
        super().__init__(f"Unable to update user: {user_id}")
