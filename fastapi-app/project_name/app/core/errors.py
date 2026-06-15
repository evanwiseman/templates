# Third party
from fastapi import status


class AppError(Exception):
    status_code: int
    detail: str

    def __init__(self, detail: str | None = None) -> None:
        self.detail = detail or self.__class__.detail
        super().__init__(self.detail)


class NotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Not found"


class ConflictError(AppError):
    status_code = status.HTTP_409_CONFLICT
    detail = "Conflict error"


class UnauthorizedError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Authentication failed"


class InternalError(AppError):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Server error"
