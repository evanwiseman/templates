"""Main package."""

# Standard library
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

# Third party
import uvicorn
from fastapi import FastAPI
from fastapi_pagination import add_pagination

# First party
from app.core.config import settings
from app.features.users import users_router

logger = logging.getLogger(__name__)
logger.setLevel(settings.log_level)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(users_router)
add_pagination(app)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello from fast-api"}


def main() -> None:
    uvicorn.run(
        app,
        host=settings.app.host,
        port=settings.app.port,
        log_level=settings.log_level,
    )


if __name__ == "__main__":
    main()
