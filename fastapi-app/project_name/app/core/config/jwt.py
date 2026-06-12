# Third party
from pydantic import Field, SecretStr
from pydantic_settings import SettingsConfigDict

# First party
from project_name.app.core.config.env import EnvSettings


class JwtSettings(EnvSettings):
    model_config = SettingsConfigDict(
        env_prefix="JWT_",
    )

    secret: SecretStr = Field(min_length=32)
    ttl: int = Field(default=15, ge=1)
    issuer: str | None = Field(default=None)
