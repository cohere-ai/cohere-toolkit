"""
Query and Path Parameters for Auth
"""
from typing import Annotated

from fastapi import Path

StrategyPathParam = Annotated[str, Path(
    title="Strategy Name",
    description="Name of strategy in question",
)]
