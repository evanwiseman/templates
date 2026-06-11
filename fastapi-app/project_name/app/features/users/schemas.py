# Standard library
from uuid import UUID

# Third party
from pydantic import BaseModel, ConfigDict


class UserShow(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str


class UserCreate(BaseModel):
    username: str
    password: str


class UserUpdate(BaseModel):
    old_password: str
    new_password: str


class UserDestroy(BaseModel):
    password: str
