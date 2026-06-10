# Third party
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
    except VerifyMismatchError, VerificationError, InvalidHashError:
        return False
    return True
