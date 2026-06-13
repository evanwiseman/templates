"""Tests for auth."""

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
)
from project_name.app.core.uuid import uuid7

SECRET_KEY = "249d175f203846fa83b53beb95162356900cde5058793bdd2c4fc6d96609ee88"
WRONG_KEY = "7e51dcc6235d686bbbe071ca62abac6a28eb34f3a0aab30b8df051d675afd884"


class TestAccessTokens:
    def test_correct_token(self) -> None:
        issuer = "test"
        user_id = uuid7()
        access_token = create_access_token(
            user_id,
            secret=SECRET_KEY,
            issuer=issuer,
        )
        data = decode_access_token(access_token, secret=SECRET_KEY)

        assert data["sub"] == str(user_id)
        assert data["iss"] == issuer
        assert data["type"] == "access"

    def test_expired_token(self) -> None:
        access_token = create_access_token(
            uuid7(),
            secret=SECRET_KEY,
            expires_minutes=-1,
        )

        with pytest.raises(ExpiredSignatureError):
            decode_access_token(access_token, secret=SECRET_KEY)

    def test_wrong_secret(self) -> None:
        access_token = create_access_token(uuid7(), secret=SECRET_KEY)
        with pytest.raises(InvalidSignatureError):
            decode_access_token(access_token, secret=WRONG_KEY)

    def test_wrong_algorithm(self) -> None:
        access_token = create_access_token(uuid7(), secret=SECRET_KEY)
        with pytest.raises(InvalidAlgorithmError):
            decode_access_token(
                access_token,
                secret=SECRET_KEY,
                algorithm="ES256",
            )

    def test_wrong_issuer(self):
        issuer = "test"
        wrong_issuer = "wrong"

        access_token = create_access_token(
            uuid7(),
            secret=SECRET_KEY,
            issuer=issuer,
        )

        with pytest.raises(InvalidIssuerError):
            decode_access_token(
                access_token,
                secret=SECRET_KEY,
                issuer=wrong_issuer,
            )
