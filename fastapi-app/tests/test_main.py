"""Tests for app.main."""

# Standard library
import logging

# Third party
import pytest

# First party
from app.main import main


def test_main(caplog: pytest.LogCaptureFixture) -> None:
    """``main()`` logs the hello message at INFO."""
    caplog.set_level(logging.INFO)
    main()
    assert "Hello from fastapi-app!" in caplog.text
