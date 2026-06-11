"""Tests for database settings."""

# Third party
import pytest
from pydantic import ValidationError

# First party
from project_name.app.core.config import DatabaseSettings


class TestDatabaseSettings:
    def test_default_url(self, database_settings: DatabaseSettings) -> None:
        """Default database URL includes a database name."""
        assert str(database_settings.url).endswith("/fastapi_app")

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
            "DB_URL",
            "postgresql+psycopg://user:pass@localhost:5432/custom_db",
        )
        assert str(DatabaseSettings().url).endswith("/custom_db")
