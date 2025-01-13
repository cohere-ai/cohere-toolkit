"""
Query and Path Parameters for Users
"""
from typing import Annotated

from fastapi import Path

UserIdPathParam = Annotated[str, Path(
    title="User ID",
    description="User ID for the user in question",
)]
