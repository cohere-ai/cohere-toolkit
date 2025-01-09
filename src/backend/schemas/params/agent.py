"""
Query and Path Parameters for Agents
"""
from typing import Annotated

from fastapi import Path, Query

from backend.schemas.agent import AgentVisibility

VisibilityQueryParam = Annotated[AgentVisibility, Query(
    title="Visibility",
    description="Agent visibility",
)]

AgentIdPathParam = Annotated[str, Path(
    title="Agent ID",
    description="Agent ID for agent in question",
)]

AgentToolMetadataIdPathParam = Annotated[str, Path(
    title="Agent Tool Metadata ID",
    description="Agent Tool Metadata ID for tool metadata in question",
)]
