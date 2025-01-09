"""
Query and Path Parameters for Files
"""
from typing import Annotated

from fastapi import Path

FileIdPathParam = Annotated[str, Path(
    title="File ID",
    description="File ID for file in question",
)]
