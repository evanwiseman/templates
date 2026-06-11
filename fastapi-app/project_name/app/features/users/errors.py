"""User domain errors."""

# Standard library


class UserAlreadyExistsError(Exception):
    def __init__(self) -> None:
        super().__init__("User already exists")


class UserNotFoundError(Exception):
    def __init__(self) -> None:
        super().__init__("User not found")


class UserUnauthorizedError(Exception):
    def __init__(self) -> None:
        super().__init__("Authentication failed")


class UserUpdateError(Exception):
    def __init__(self) -> None:
        super().__init__("An unexpected error occured while updating the user")
