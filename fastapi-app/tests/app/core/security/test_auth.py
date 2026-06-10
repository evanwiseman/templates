"""Tests for auth."""

# First party
from app.core.security import hash_password, verify_password


class TestVerifyPassword:
    def test_correct_password(self) -> None:
        """Password matches the hash."""
        plain = "secret-password"
        hashed = hash_password(plain)
        result = verify_password(
            hashed,
            plain,
        )

        assert result

    def test_reject_wrong_password(self) -> None:
        """Password does not match."""
        hashed = hash_password("secret-password")
        result = verify_password(
            hashed,
            "wrong-password",
        )

        assert not result

    def test_rejects_invalid_hash(self) -> None:
        """Password returns False for malformed hash strings."""
        result = verify_password(
            "not-a-valid-hash",
            "secret-password",
        )
        assert not result
