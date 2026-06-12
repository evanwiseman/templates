"""Tests for JWT settings."""

# Third party
import pytest
from pydantic import ValidationError
from pydantic_settings import SettingsConfigDict

# First party
from project_name.app.core.config import JwtSettings, Settings
from project_name.app.core.config.settings import jwt_settings_factory

_VALID_SECRET = "a" * 32


class TestJwtSettings:
    def test_defaults(self, jwt_settings: JwtSettings) -> None:
        """JWT settings load from test env configured in conftest.

        Args:
            jwt_settings (JwtSettings): Test JwtSettings.
        """
        assert (
            jwt_settings.secret.get_secret_value()
            == "25f5df2fe8a5a66c2fcf6fdf9be43795cc8d2b47f4aa160341a546f0e513c1ef"
        )
        assert jwt_settings.ttl == 15
        assert jwt_settings.issuer == "tests"

    def test_model_validate(self) -> None:
        """JWT settings accept explicit values."""
        jwt = JwtSettings.model_validate(
            {
                "secret": _VALID_SECRET,
                "ttl": 30,
                "issuer": "my-app",
            }
        )
        assert jwt.secret.get_secret_value() == _VALID_SECRET
        assert jwt.ttl == 30
        assert jwt.issuer == "my-app"

    def test_model_validate_without_issuer(self) -> None:
        """Issuer is optional."""
        jwt = JwtSettings.model_validate(
            {
                "secret": _VALID_SECRET,
                "ttl": 15,
                "issuer": None,
            }
        )
        assert jwt.issuer is None

    def test_rejects_missing_secret(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Secret is required.

        Args:
            monkeypatch (pytest.MonkeyPatch): Patcher for ``.env``.
        """
        monkeypatch.delenv("JWT_SECRET", raising=False)
        monkeypatch.setattr(
            JwtSettings,
            "model_config",
            SettingsConfigDict(env_prefix="JWT_", env_file=None),
        )
        with pytest.raises(ValidationError):
            JwtSettings.model_validate({})

    def test_rejects_short_secret(self) -> None:
        """Secret must be at least 32 characters."""
        with pytest.raises(ValidationError):
            JwtSettings.model_validate(
                {
                    "secret": "too-short",
                    "ttl": 15,
                }
            )

    def test_rejects_zero_ttl(self) -> None:
        """TTL must be at least 1."""
        with pytest.raises(ValidationError):
            JwtSettings.model_validate(
                {
                    "secret": _VALID_SECRET,
                    "ttl": 0,
                }
            )

    def test_rejects_negative_ttl(self) -> None:
        """TTL must be at least 1."""
        with pytest.raises(ValidationError):
            JwtSettings.model_validate(
                {
                    "secret": _VALID_SECRET,
                    "ttl": -1,
                }
            )

    def test_reads_from_env(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """JWT_SECRET, JWT_TTL, and JWT_ISSUER loaded from environment.

        Args:
            monkeypatch (pytest.MonkeyPatch): Patcher for ``.env``.
        """
        secret = "b" * 32
        monkeypatch.setenv("JWT_SECRET", secret)
        monkeypatch.setenv("JWT_TTL", "60")
        monkeypatch.setenv("JWT_ISSUER", "from-env")

        jwt = JwtSettings.model_validate({})

        assert jwt.secret.get_secret_value() == secret
        assert jwt.ttl == 60
        assert jwt.issuer == "from-env"

    def test_nested_on_settings_defaults(
        self,
        settings: Settings,
        jwt_settings: JwtSettings,
    ) -> None:
        """Settings embeds JwtSettings with the same values.

        Args:
            settings (Settings): Test Settings.
            jwt_settings (JwtSettings): Test JwtSettings.

        """
        assert settings.jwt == jwt_settings

    def test_nested_on_settings_override(self) -> None:
        """Settings accepts nested JWT overrides."""
        secret = "c" * 32
        settings = Settings.model_validate(
            {
                "jwt": {
                    "secret": secret,
                    "ttl": 45,
                    "issuer": "nested-override",
                }
            }
        )
        assert settings.jwt.secret.get_secret_value() == secret
        assert settings.jwt.ttl == 45
        assert settings.jwt.issuer == "nested-override"

    def test_jwt_settings_factory_loads_from_env(
        self,
        jwt_settings: JwtSettings,
    ) -> None:
        """Settings default_factory builds JWT config from environment.

        Args:
            jwt_settings (JwtSettings): Test JwtSettings.
        """
        assert jwt_settings_factory() == jwt_settings
