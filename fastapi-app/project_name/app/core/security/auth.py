# Standard library
from datetime import UTC, datetime, timedelta
from uuid import UUID

# Third party
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import (
    InvalidHashError,
    VerificationError,
    VerifyMismatchError,
)

_ph = PasswordHasher()


def hash_password(password: str):
    return _ph.hash(password)


def verify_password(hashed_password: str, password: str) -> bool:
    try:
        _ph.verify(hashed_password, password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False
    return True

def create_access_token(
    user_id: UUID,
    *,
    secret: str,
    algorithm: str = "HS256",
    expires_minutes: int = 15,
    issuer: str | None = None,
) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=expires_minutes),
        "type": "access",
    }
    if issuer:
        payload["iss"] = issuer
    return jwt.encode(payload, secret, algorithm=algorithm)


def decode_access_token(
    token: str,
    *,
    secret: str,
    algorithm: str = "HS256",
    issuer: str | None = None,
) -> dict[str, object]:
    return jwt.decode(
        token,
        secret,
        algorithms=[algorithm],
        issuer=issuer,
        options={"require": ["exp", "sub", "iat"]},
    )