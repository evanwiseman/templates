"""Shared test data for user feature tests."""

# Standard library
from dataclasses import dataclass

VALID_PASSWORD = "Secret1!"
VALID_NEW_PASSWORD = "Newpass1!"


@dataclass(frozen=True, slots=True)
class PasswordCase:
    reason: str
    password: str
    should_pass: bool
    complexity_error: str | None = None


VALID_PASSWORD_CASE = PasswordCase("valid", VALID_PASSWORD, True)

SCHEMA_INVALID_CASES = [
    PasswordCase("too-short", "Ab1!xyz", False),
    PasswordCase("weak", "weak", False),
]

COMPLEXITY_INVALID_CASES = [
    PasswordCase("no-upper", "noupper1!", False, "uppercase"),
    PasswordCase("no-lower", "NOLOWER1!", False, "lowercase"),
    PasswordCase("no-digit", "NoDigits!", False, "digit"),
    PasswordCase("no-special", "NoSpecial1", False, "special character"),
]
