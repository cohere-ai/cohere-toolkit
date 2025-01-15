"""
Query and Path Parameters for SCIM
"""
from typing import Annotated, Optional

from fastapi import Depends, Path, Query


class _ScimPaginationParams:
    """
    Common pagination query parameters
    """
    def __init__(
        self,
        start_index: Annotated[int, Query(
            title="Start Index",
            description="Start Index for request",
        )] = 1,
        count: Annotated[int, Query(
            title="Count",
            description="Maximum number of records to return per request",
        )] = 100,
        filter: Annotated[Optional[str], Query(
            title="Filter",
            description="Filter to use when filtering response",
        )] = None
    ) -> None:
        self.start_index = start_index
        self.count = count
        self.filter = filter

ScimPaginationQueryParams = Annotated[_ScimPaginationParams, Depends()]


UserIdPathParam = Annotated[str, Path(
    title="User ID",
    description="User ID for the user in question",
)]


GroupIdPathParam = Annotated[str, Path(
    title="Group ID",
    description="Group ID for the group in question",
)]
