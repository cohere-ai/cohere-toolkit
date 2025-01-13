"""
Query and Path Parameters for Auth
"""
from typing import Annotated, Optional

from fastapi import Path, Query

StrategyPathParam = Annotated[str, Path(
    title="Strategy Name",
    description="Name of strategy in question",
)]

CodeQueryParam = Annotated[Optional[str], Query(
    title="Code",
    description="OAuth Code",
)]
