# Standard library
from typing import TypeVar

# Third party
from pydantic import BaseModel

T = TypeVar("T")


class ListResult[T](BaseModel):
    items: list[T]
    total: int
