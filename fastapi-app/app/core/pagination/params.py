"""Pagination query parameters."""

# Standard library
from dataclasses import dataclass
from typing import Annotated

# Third party
from fastapi import Depends, Query


@dataclass(frozen=True)
class PaginationParams:
    limit: int
    offset: int


def get_pagination_params(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> PaginationParams:
    return PaginationParams(limit=limit, offset=offset)


PaginationDep = Annotated[PaginationParams, Depends(get_pagination_params)]
