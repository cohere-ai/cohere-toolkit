"""
Query and Path Parameters for Snapshots
"""
from typing import Annotated

from fastapi import Path

LinkIdPathParam =  Annotated[str, Path(
    title="Link ID",
    description="Link ID for the snapshot link in question",
)]

SnapshotIdPathParam =  Annotated[str, Path(
    title="Snapshot ID",
    description="Snapshot ID for the snapshot in question",
)]
