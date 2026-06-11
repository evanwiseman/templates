"""Tests for user password validation."""

# Third party
import pytest
from pydantic import SecretStr, ValidationError

# First party
from project_name.app.features.users import UserCreate, UserUpdate
from project_name.app.features.users.validators import (
    validate_password_complexity,
)

# Local
from .constants import (
    COMPLEXITY_INVALID_CASES,
    SCHEMA_INVALID_CASES,
    VALID_PASSWORD_CASE,
    PasswordCase,
)


def _case_id(case: PasswordCase) -> str:
    return case.reason


class TestValidatePasswordComplexity:
    @pytest.mark.parametrize(
        "case",
        [VALID_PASSWORD_CASE, *COMPLEXITY_INVALID_CASES],
        ids=_case_id,
    )
    def test_valid_password(self, case: PasswordCase) -> None:
        if case.should_pass:
            assert validate_password_complexity(case.password) == case.password
            return
        assert case.complexity_error is not None
        with pytest.raises(ValueError, match=case.complexity_error):
            validate_password_complexity(case.password)


class TestValidatedPasswordSchema:
    @pytest.mark.parametrize(
        "model",
        [UserCreate, UserUpdate],
        ids=["create", "update"],
    )
    @pytest.mark.parametrize(
        "use_secret_str",
        [False, True],
        ids=["str", "secret-str"],
    )
    @pytest.mark.parametrize(
        "case",
        [VALID_PASSWORD_CASE, *SCHEMA_INVALID_CASES],
        ids=_case_id,
    )
    def test_password_validation(
        self,
        model: type[UserCreate] | type[UserUpdate],
        use_secret_str: bool,
        case: PasswordCase,
    ) -> None:
        password_input: str | SecretStr = (
            SecretStr(case.password) if use_secret_str else case.password
        )
        payload = _password_payload(model, password_input)

        if case.should_pass:
            result = model.model_validate(payload)
            assert _password_value(result) == case.password
            return

        with pytest.raises(ValidationError):
            model.model_validate(payload)


def _password_payload(
    model: type[UserCreate] | type[UserUpdate],
    password: str | SecretStr,
) -> dict[str, object]:
    if model is UserCreate:
        return {"username": "alice", "password": password}
    return {
        "old_password": "any-old-value",
        "new_password": password,
    }


def _password_value(result: UserCreate | UserUpdate) -> str:
    if isinstance(result, UserCreate):
        return result.password.get_secret_value()
    return result.new_password.get_secret_value()
