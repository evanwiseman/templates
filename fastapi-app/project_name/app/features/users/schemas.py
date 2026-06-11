# Standard library
from uuid import UUID

# Third party
from pydantic import BaseModel, ConfigDict

# Local
from .validators import ValidatedPassword


class UserShow(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str


class UserCreate(BaseModel):
    username: str
    password: ValidatedPassword


class UserUpdate(BaseModel):
    old_password: str
    new_password: ValidatedPassword


class UserDestroy(BaseModel):
    password: str
