"""
Query and Path Parameters for Models
"""
from typing import Annotated, Optional

from fastapi import Query

ModelQueryParam =  Annotated[Optional[str], Query(
    title="Model",
    description="Model to filter results by",
)]
