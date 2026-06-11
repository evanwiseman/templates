# Standard library
import logging

# Third party
from pydantic import Field, field_validator
from pydantic_settings import SettingsConfigDict

# Local
from .app import AppSettings
from .database import DatabaseSettings
from .env import EnvSettings


class Settings(EnvSettings):
    log_level: int = Field(default=logging.INFO)

    app: AppSettings = Field(default_factory=AppSettings)
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)

    model_config = SettingsConfigDict(
        extra="ignore",
    )

    @field_validator("log_level", mode="before")
    @classmethod
    def parse_log_level(cls, v: object) -> int:
        if isinstance(v, int):
            return v
        if isinstance(v, str):
            name = v.upper()
            level = getattr(logging, name, None)
            if isinstance(level, int):
                return level
            raise ValueError(f"invalid log level: {v!r}")
        raise TypeError(f"log_level must be str or int, got {type(v)!r}")


settings = Settings()
