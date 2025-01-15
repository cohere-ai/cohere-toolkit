"""
Query and Path Parameters for Models
"""
from typing import Annotated, Optional

from fastapi import Path, Query

ModelIdPathParam =  Annotated[str, Path(
    title="Model ID",
    description="Model ID for the model in question",
)]

ModelQueryParam =  Annotated[Optional[str], Query(
    title="Model",
    description="Model to filter results by",
)]
