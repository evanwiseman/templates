# Standard library
from collections.abc import Generator
from typing import Annotated

# Third party
from fastapi import Depends
from sqlalchemy.orm.session import Session

# Local
from .engine import SessionLocal


def get_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


SessionDep = Annotated[Session, Depends(get_session)]
