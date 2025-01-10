"""
Shared Query and Path Parameters for Routers
"""
from typing import Annotated, Optional

from fastapi import Depends, Query


class _PaginationParams:
    """
    Common pagination query parameters
    """
    def __init__(
        self,
        offset: Annotated[int, Query(
            title="Pagination Offset",
            description="Offset for where request should start returning records from",
        )] = 0,
        limit: Annotated[int, Query(
            title="Pagination Limit",
            description="Maximum number of records to return per request",
        )] = 100,
    ) -> None:
        self.offset = offset
        self.limit = limit

PaginationQueryParams = Annotated[_PaginationParams, Depends()]


OrderByQueryParam = Annotated[Optional[str], Query(
    title="Orber By",
    description="Field to sorts results by",
)]
