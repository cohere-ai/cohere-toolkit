"""
Query and Path Parameters for Agents
"""
from typing import Annotated, Optional

from fastapi import Path, Query

from backend.schemas.agent import AgentVisibility

VisibilityQueryParam = Annotated[AgentVisibility, Query(
    title="Visibility",
    description="Agent visibility",
)]

AgentIdQueryParam = Annotated[Optional[str], Query(
    title="Agent ID",
    description="Agent ID to filter results by",
)]

AgentIdPathParam = Annotated[str, Path(
    title="Agent ID",
    description="Agent ID for agent in question",
)]

AgentToolMetadataIdPathParam = Annotated[str, Path(
    title="Agent Tool Metadata ID",
    description="Agent Tool Metadata ID for tool metadata in question",
)]
