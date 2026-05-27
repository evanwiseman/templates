"""Tests for app.core.config."""

# Standard library
import logging

# Third party
import pytest
from pydantic import ValidationError

# First party
from app.core.config import AppSettings, DatabaseSettings, Settings


class TestAppSettings:
    def test_defaults(self) -> None:
        """Default app settings match local dev values."""
        app = AppSettings()
        assert app.env == "dev"
        assert app.host == "127.0.0.1"
        assert app.port == 8000

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
        """ENV, HOST, and PORT are loaded from the environment."""
        monkeypatch.setenv("ENV", "staging")
        monkeypatch.setenv("HOST", "10.0.0.2")
        monkeypatch.setenv("PORT", "9000")
        app = AppSettings()
        assert app.env == "staging"
        assert app.host == "10.0.0.2"
        assert app.port == 9000

    def test_nested_on_settings_defaults(self) -> None:
        """Settings embeds AppSettings with the same defaults."""
        assert Settings().app == AppSettings()

    def test_nested_on_settings_override(self) -> None:
        """Settings accepts nested app overrides."""
        settings = Settings.model_validate(
            {"app": {"env": "prod", "host": "10.0.0.1", "port": 8080}}
        )
        assert settings.app.env == "prod"
        assert settings.app.host == "10.0.0.1"
        assert settings.app.port == 8080


class TestDatabaseSettings:
    def test_default_url(self) -> None:
        """Default database URL includes a database name."""
        db = DatabaseSettings()
        assert str(db.url).endswith("/fastapi_app")

    @pytest.mark.parametrize(
        "url",
        [
            "postgresql+psycopg://user:pass@localhost:5432/",
            "postgresql+psycopg://user:pass@localhost:5432",
        ],
    )
    def test_requires_database_name(self, url: str) -> None:
        """URLs without a database name are rejected."""
        with pytest.raises(ValidationError, match="database must be provided"):
            DatabaseSettings.model_validate({"url": url})

    def test_coerces_str_to_postgres_dsn(self) -> None:
        """URL validator coerces string values to PostgresDsn."""
        url = DatabaseSettings.check_db_name(
            "postgresql+psycopg://user:pass@localhost:5432/mydb"
        )
        assert str(url).endswith("/mydb")

    def test_rejects_non_str_url(self) -> None:
        """URL validator rejects values that are not str or PostgresDsn."""
        with pytest.raises(TypeError, match="url must be str or"):
            DatabaseSettings.check_db_name(123)

    def test_reads_url_from_env(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """URL is loaded from the environment."""
        monkeypatch.setenv(
            "URL",
            "postgresql+psycopg://user:pass@localhost:5432/custom_db",
        )
        assert str(DatabaseSettings().url).endswith("/custom_db")


class TestSettings:
    def test_default_log_level(self) -> None:
        """Default log level is INFO."""
        assert Settings().log_level == logging.INFO

    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("DEBUG", logging.DEBUG),
            ("info", logging.INFO),
            ("WARNING", logging.WARNING),
            (logging.ERROR, logging.ERROR),
        ],
    )
    def test_parses_log_level(self, raw: str | int, expected: int) -> None:
        """Log level accepts logging names (case-insensitive) and ints."""
        assert (
            Settings.model_validate({"log_level": raw}).log_level == expected
        )

    def test_rejects_invalid_log_level(self) -> None:
        """Unknown log level names raise validation errors."""
        with pytest.raises(ValidationError, match="invalid log level"):
            Settings.model_validate({"log_level": "NOT_A_LEVEL"})

    def test_rejects_non_str_int_log_level(self) -> None:
        """Log level must be a string or int."""
        with pytest.raises(TypeError, match="log_level must be str or int"):
            Settings.model_validate({"log_level": 3.14})

    def test_reads_log_level_from_env(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """LOG_LEVEL is loaded from the environment."""
        monkeypatch.setenv("LOG_LEVEL", "ERROR")
        assert Settings().log_level == logging.ERROR
