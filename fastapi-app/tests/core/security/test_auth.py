"""Tests for auth."""

# First party
from app.core.security import hash_password, verify_password


def test_verify_password_accepts_correct_password() -> None:
    """verify_password returns True when the password matches the hash."""
    plain = "secret-password"
    hashed = hash_password(plain)
    result = verify_password(
        hashed,
        plain,
    )

    assert isinstance(result, bool) and result


def test_verify_password_rejects_wrong_password() -> None:
    """verify_password returns False when the password does not match."""
    hashed = hash_password("secret-password")
    result = verify_password(
        hashed,
        "wrong-password",
    )

    assert isinstance(result, bool) and not result


def test_verify_password_rejects_invalid_hash() -> None:
    """verify_password returns False for malformed hash strings."""
    result = verify_password(
        "not-a-valid-hash",
        "secret-password",
    )
    assert isinstance(result, bool) and not result
