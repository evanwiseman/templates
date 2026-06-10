"""Tests for app settings."""

# Third party
import pytest
from pydantic import ValidationError

# First party
from app.core.config import AppSettings, Settings


class TestAppSettings:
    def test_defaults(self, app_settings: AppSettings) -> None:
        """Default app settings match local dev values."""
        assert app_settings.env == "dev"
        assert app_settings.host == "127.0.0.1"
        assert app_settings.port == 8000

    def test_model_validate(self) -> None:
        """App settings accept explicit values."""
        app = AppSettings.model_validate(
            {"env": "prod", "host": "10.0.0.1", "port": 3000}
        )
        assert app.env == "prod"
        assert app.host == "10.0.0.1"
        assert app.port == 3000

    @pytest.mark.parametrize("port", [0, 65536])
    def test_rejects_port_out_of_range(self, port: int) -> None:
        """Port must be between 1 and 65535."""
        with pytest.raises(ValidationError):
            AppSettings.model_validate({"port": port})

    def test_reads_from_env(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """APP_ENV, APP_HOST, and APP_PORT are loaded from the environment."""
        monkeypatch.setenv("APP_ENV", "staging")
        monkeypatch.setenv("APP_HOST", "10.0.0.2")
        monkeypatch.setenv("APP_PORT", "9000")
        app = AppSettings()
        assert app.env == "staging"
        assert app.host == "10.0.0.2"
        assert app.port == 9000

    def test_nested_on_settings_defaults(
        self,
        settings: Settings,
        app_settings: AppSettings,
    ) -> None:
        """Settings embeds AppSettings with the same defaults."""
        assert settings.app == app_settings

    def test_nested_on_settings_override(self) -> None:
        """Settings accepts nested app overrides."""
        settings = Settings.model_validate(
            {"app": {"env": "prod", "host": "10.0.0.1", "port": 8080}}
        )
        assert settings.app.env == "prod"
        assert settings.app.host == "10.0.0.1"
        assert settings.app.port == 8080
