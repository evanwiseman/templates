"""Tests for access and refresh tokens."""

# Standard library
import hashlib

# Third party
import pytest
from jwt.exceptions import (
    ExpiredSignatureError,
    InvalidAlgorithmError,
    InvalidIssuerError,
    InvalidSignatureError,
)

# First party
from project_name.app.core.security.tokens import (
    create_access_token,
    decode_access_token,
    hash_refresh_token,
    make_refresh_token,
)
from project_name.app.core.uuid import uuid7

_SECRET_KEY = (
    "249d175f203846fa83b53beb95162356900cde5058793bdd2c4fc6d96609ee88"
)
_WRONG_KEY = "7e51dcc6235d686bbbe071ca62abac6a28eb34f3a0aab30b8df051d675afd884"
_KNOWN_RAW = "refresh-token-value"
_KNOWN_HASH = hashlib.sha256(_KNOWN_RAW.encode()).hexdigest()


class TestAccessTokens:
    def test_correct_token(self) -> None:
        issuer = "test"
        user_id = uuid7()
        access_token = create_access_token(
            user_id,
            secret=_SECRET_KEY,
            issuer=issuer,
        )
        data = decode_access_token(access_token, secret=_SECRET_KEY)

        assert data["sub"] == str(user_id)
        assert data["iss"] == issuer
        assert data["type"] == "access"

    def test_expired_token(self) -> None:
        access_token = create_access_token(
            uuid7(),
            secret=_SECRET_KEY,
            expires_minutes=-1,
        )

        with pytest.raises(ExpiredSignatureError):
            decode_access_token(access_token, secret=_SECRET_KEY)

    def test_wrong_secret(self) -> None:
        access_token = create_access_token(uuid7(), secret=_SECRET_KEY)
        with pytest.raises(InvalidSignatureError):
            decode_access_token(access_token, secret=_WRONG_KEY)

    def test_wrong_algorithm(self) -> None:
        access_token = create_access_token(uuid7(), secret=_SECRET_KEY)
        with pytest.raises(InvalidAlgorithmError):
            decode_access_token(
                access_token,
                secret=_SECRET_KEY,
                algorithm="ES256",
            )

    def test_wrong_issuer(self):
        issuer = "test"
        wrong_issuer = "wrong"

        access_token = create_access_token(
            uuid7(),
            secret=_SECRET_KEY,
            issuer=issuer,
        )

        with pytest.raises(InvalidIssuerError):
            decode_access_token(
                access_token,
                secret=_SECRET_KEY,
                issuer=wrong_issuer,
            )


class TestMakeRefreshToken:
    def test_returns_url_safe_string(self) -> None:
        """Generated refresh tokens are non-empty url-safe strings."""
        refresh_token = make_refresh_token()

        assert refresh_token
        assert refresh_token.isascii()
        assert " " not in refresh_token
        assert len(refresh_token) >= 32

    def test_generates_unique_values(self) -> None:
        """Produces different token every call."""
        first = make_refresh_token()
        second = make_refresh_token()

        assert first != second


class TestHashRefreshToken:
    def test_is_deterministic(self) -> None:
        """Hashing same raw token always yields same digest."""
        raw = make_refresh_token()

        assert hash_refresh_token(raw) == hash_refresh_token(raw)

    def test_matches_sha256_hex(self) -> None:
        """Hash output matches stdlib SHA-256 hex digest."""
        assert hash_refresh_token(_KNOWN_RAW) == _KNOWN_HASH

    def test_differs_for_different_inputs(self) -> None:
        """Different raw tokens produce different hashes."""
        first_hash = hash_refresh_token("token-a")
        second_hash = hash_refresh_token("token-b")

        assert first_hash != second_hash


class TestRefreshTokens:
    def test_lookup_flow_hashes_incoming_token(self) -> None:
        """Verify refresh comparing client and stored hash."""
        raw = make_refresh_token()
        stored_hash = hash_refresh_token(raw)

        assert hash_refresh_token(raw) == stored_hash
        assert hash_refresh_token("wrong-token") != stored_hash
