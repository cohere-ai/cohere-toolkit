"""
Query and Path Parameters for Organizations
"""
from typing import Annotated, Optional

from fastapi import Query

OrganizationIdQueryParam =  Annotated[Optional[str], Query(
    title="Organization ID",
    description="Organization ID of the agent",
)]
