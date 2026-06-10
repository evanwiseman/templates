# Standard library
from typing import Annotated

# Third party
from fastapi import Depends
from fastapi_pagination import LimitOffsetParams
from sqlalchemy.orm import Session

# First party
from app.database.session import get_session

SessionDep = Annotated[Session, Depends(get_session)]
PaginationParamsDep = Annotated[LimitOffsetParams, Depends()]

__all__ = ["PaginationParamsDep", "SessionDep"]
