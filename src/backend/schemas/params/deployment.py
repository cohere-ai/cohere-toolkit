"""
Query and Path Parameters for Deployments
"""
from typing import Annotated, Optional

from fastapi import Path, Query

DeploymentIdPathParam = Annotated[str, Path(
    title="Deployment ID",
    description="Deployment ID for deployment in question",
)]

AllQueryParam = Annotated[Optional[bool], Query(
    title="All",
    description="Include all deployments, regardless of availability.",
)]
