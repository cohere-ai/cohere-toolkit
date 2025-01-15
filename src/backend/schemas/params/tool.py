"""
Query and Path Parameters for Auth
"""
from typing import Annotated

from fastapi import Path

ToolIdPathParam = Annotated[str, Path(
    title="Tool ID",
    description="Tool ID for tool in question",
)]
