"""Tests for settings."""

# Standard library
import logging

# Third party
import pytest
from pydantic import ValidationError

# First party
from app.core.config import Settings


class TestSettings:
    def test_default_log_level(self, settings: Settings) -> None:
        """Default log level is INFO."""
        assert settings.log_level == logging.INFO

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
