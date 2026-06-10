# Third party
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# First party
from app.core.config import settings

engine = create_engine(url=str(settings.db.url))
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
