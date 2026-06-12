# Standard library
import logging

# Third party
from pydantic import Field, field_validator
from pydantic_settings import SettingsConfigDict

# First party
from project_name.app.core.config.jwt import JwtSettings

# Local
from .app import AppSettings
from .database import DatabaseSettings
from .env import EnvSettings


def jwt_settings_factory() -> JwtSettings:
    return JwtSettings.model_validate({})


class Settings(EnvSettings):
    log_level: int = Field(default=logging.INFO)

    app: AppSettings = Field(default_factory=AppSettings)
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    jwt: JwtSettings = Field(default_factory=jwt_settings_factory)

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
