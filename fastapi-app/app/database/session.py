# Standard library
from collections.abc import Generator

# Third party
from sqlalchemy.orm.session import Session

# Local
from .engine import SessionLocal


def get_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
