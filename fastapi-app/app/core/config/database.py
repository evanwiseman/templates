# Standard library

# Third party
from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import SettingsConfigDict

# Local
from .env import EnvSettings


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
