"""
Query and Path Parameters for Organizations
"""
from typing import Annotated, Optional

from fastapi import Path, Query

OrganizationIdPathParam =  Annotated[str, Path(
    title="Organization ID",
    description="Organization ID for the organization in question",
)]

OrganizationIdQueryParam =  Annotated[Optional[str], Query(
    title="Organization ID",
    description="Organization ID to filter results by",
)]
