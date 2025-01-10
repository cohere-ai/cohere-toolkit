"""
Query and Path Parameters for Messages
"""
from typing import Annotated

from fastapi import Path

MessageIdPathParam = Annotated[str, Path(
    title="Message ID",
    description="Message ID for message in question",
)]
