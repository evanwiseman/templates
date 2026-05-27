# Future imports
from __future__ import annotations

# Standard library
import logging

# Third party
from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="_",
        extra="ignore",
    )


class AppSettings(EnvSettings):
    env: str = Field(default="dev")
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8000, ge=1, le=65535)

    model_config = SettingsConfigDict(
        env_prefix="APP_",
    )


class DatabaseSettings(EnvSettings):
    url: PostgresDsn = Field(
        default=PostgresDsn(
            "postgresql+psycopg://user:pass@localhost:5432/fastapi_app"
        )
    )

    model_config = SettingsConfigDict(
        env_prefix="DB_",
    )

    @field_validator("url", mode="before")
    @classmethod
    def check_db_name(cls, v: object) -> PostgresDsn:
        if isinstance(v, str):
            v = PostgresDsn(v)
        if not isinstance(v, PostgresDsn):
            raise TypeError(
                f"url must be str or {PostgresDsn.__name__}, got {type(v)!r}"
            )
        if not v.path or len(v.path) <= 1:
            raise ValueError("database must be provided")
        return v


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
