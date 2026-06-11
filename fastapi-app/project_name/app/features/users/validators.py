"""Shared user password validation."""

# Standard library
import re
from typing import Annotated

# Third party
from pydantic import BeforeValidator, Field, SecretStr

PASSWORD_MIN_LENGTH = 8
_SPECIAL_CHAR_PATTERN = re.compile(r"[!@#$%^&*(),.?\":{}|<>_+-]")


def validate_password_complexity(password: str) -> str:
    """Require character-class complexity. Length is enforced by Field."""
    if not re.search(r"[A-Z]", password):
        raise ValueError(
            "Password must contain at least one uppercase letter.",
        )
    if not re.search(r"[a-z]", password):
        raise ValueError(
            "Password must contain at least one lowercase letter.",
        )
    if not re.search(r"[0-9]", password):
        raise ValueError("Password must contain at least one digit.")
    if not _SPECIAL_CHAR_PATTERN.search(password):
        raise ValueError(
            "Password must contain at least one special character.",
        )
    return password


def parse_validated_password(value: str | SecretStr) -> SecretStr:
    secret = value if isinstance(value, SecretStr) else SecretStr(value)
    validate_password_complexity(secret.get_secret_value())
    return secret


ValidatedPassword = Annotated[
    SecretStr,
    BeforeValidator(parse_validated_password),
    Field(
        min_length=PASSWORD_MIN_LENGTH,
        description="Must be at least 8 characters long.",
    ),
]
