# Third party
from pydantic import Field
from pydantic_settings import SettingsConfigDict

# Local
from .env import EnvSettings


class AppSettings(EnvSettings):
    env: str = Field(default="dev")
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8000, ge=1, le=65535)

    model_config = SettingsConfigDict(
        env_prefix="APP_",
    )
