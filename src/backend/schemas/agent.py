import datetime
from abc import ABC
from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, Field


class AgentVisibility(StrEnum):
    """
    Supported values for Agent Visibility
    """
    PRIVATE = "private"
    PUBLIC = "public"
    ALL = "all"


class AgentBase(ABC, BaseModel):
    """
    Abstract base class for Agent Schemas
    """
    user_id: str = Field(
        ...,
        title="User ID",
        description="User ID for the Agent",
    )
    organization_id: Optional[str] = Field(
        None,
        title="Organization ID",
        description="Organization ID for the Agent",
    )


class AgentToolMetadata(BaseModel):
    """
    Agent tool metadata schema
    """
    id: str = Field(
        ...,
        title="ID",
        description="Agent tool metadata ID",
    )
    created_at: datetime.datetime = Field(
        ...,
        title="Created At Timestamp",
        description="When the agent tool metadata was created",
    )
    updated_at: datetime.datetime = Field(
        ...,
        title="Updated At Timestamp",
        description="When the agent tool metadata was updated",
    )

    user_id: Optional[str] = Field(
        None,
        title="User ID",
        description="User ID for the agent tool metadata",
    )
    agent_id: str = Field(
        ...,
        title="Agent ID",
        description="Agent ID for the agent tool metadata",
    )
    tool_name: str = Field(
        ...,
        title="Tool Name",
        description="Tool Name for the agent tool metadata",
    )
    artifacts: list[dict] = Field(
        ...,
        title="Artifacts",
        description="Artifacts for the agent tool metadata",
    )

    class Config:
        from_attributes = True
        use_enum_values = True


class AgentToolMetadataPublic(AgentToolMetadata):
    """
    Public agent tool metadata schema
    """
    user_id: Optional[str] = Field(
        None,
        title="User ID",
        description="User ID for the agent tool metadata",
        exclude=True,
    )

    class Config:
        from_attributes = True


class AgentToolMedatadataBaseRequest(ABC, BaseModel):
    """
    Abstract class for creating/updating Agent Tool Metadata
    """
    id: Optional[str] = Field(
        None,
        title="ID",
        description="Agent Tool Metadata ID",
    )


class CreateAgentToolMetadataRequest(AgentToolMedatadataBaseRequest):
    """
    Request to create Agent Tool Metadata
    """
    tool_name: str = Field(
        ...,
        title="Tool Name",
        description="Tool Name for the agent tool metadata",
    )
    artifacts: list[dict] = Field(
        ...,
        title="Artifacts",
        description="Artifacts for the agent tool metadata",
    )


class UpdateAgentToolMetadataRequest(AgentToolMedatadataBaseRequest):
    """
    Request to update Agent Tool Metadata
    """
    tool_name: Optional[str] = Field(
        None,
        title="Tool Name",
        description="Tool Name for the agent tool metadata",
    )
    artifacts: Optional[list[dict]] = Field(
        None,
        title="Artifacts",
        description="Artifacts for the agent tool metadata",
    )


class DeleteAgentToolMetadata(BaseModel):
    """
    Delete agent tool metadata response
    """
    pass


# Agent
class Agent(AgentBase):
    """
    Agent schema
    """
    id: str = Field(
        ...,
        title="ID",
        description="Agent ID",
    )
    created_at: datetime.datetime = Field(
        ...,
        title="Created At Timestamp",
        description="When the agent was created",
    )
    updated_at: datetime.datetime = Field(
        ...,
        title="Updated At Timestamp",
        description="When the agent was updated",
    )

    name: str = Field(
        ...,
        title="Name",
        description="Name of the Agent",
    )
    version: int = Field(
        ...,
        title="Version",
        description="Version of the Agent",
    )
    description: Optional[str] = Field(
        None,
        title="Description",
        description="Agent Description",
    )
    preamble: Optional[str] = Field(
        None,
        title="Preamble",
        description="The preamble for the Agent",
    )
    temperature: float = Field(
        ...,
        title="Temperature",
        description="The temperature for the Agent",
    )
    tools: Optional[list[str]] = Field(
        None,
        title="Tools",
        description="List of tools for the Agent",
    )
    tools_metadata: list[AgentToolMetadataPublic] = Field(
        ...,
        title="Tools Metadata",
        description="List of tool metadata for the Agent",
    )
    deployment: Optional[str] = Field(
        None,
        title="Deployment",
        description="Deployment for the Agent",
    )
    model: Optional[str] = Field(
        None,
        title="Model",
        description="Model for the Agent",
    )
    is_private: Optional[bool] = Field(
        None,
        title="Is Private",
        description="If the Agent is private",
    )

    class Config:
        from_attributes = True
        use_enum_values = True


class AgentPublic(Agent):
    """
    Public agent schema
    """
    organization_id: Optional[str] = Field(
        None,
        title="Organization ID",
        description="Organization ID for the Agent",
        exclude=True,
    )
    tools_metadata: Optional[list[AgentToolMetadataPublic]] = Field(
        None,
        title="Tools Metadata",
        description="List of tool metadata for the Agent",
    )


class CreateAgentRequest(BaseModel):
    """
    Schema to create an agent
    """
    name: str = Field(
        ...,
        title="Name",
        description="Name of the Agent",
    )
    version: Optional[int] = Field(
        None,
        title="Version",
        description="Version of the Agent",
    )
    description: Optional[str] = Field(
        None,
        title="Description",
        description="Agent Description",
    )
    preamble: Optional[str] = Field(
        None,
        title="Preamble",
        description="The preamble for the Agent",
    )
    temperature: Optional[float] = Field(
        None,
        title="Temperature",
        description="The temperature for the Agent",
    )
    tools: Optional[list[str]] = Field(
        None,
        title="Tools",
        description="List of tools for the Agent",
    )
    tools_metadata: Optional[list[CreateAgentToolMetadataRequest]] = Field(
        None,
        title="Tools Metadata",
        description="Tools metadata for the Agent",
    )
    # deployment_id or deployment_name
    deployment: str = Field(
        ...,
        title="Deployment",
        description="Deployment for the Agent",
    )
    deployment_config: Optional[dict[str, str]] = Field(
        None,
        title="Deployment Config",
        description="Deployment config for the Agent",
    )
    # model_id or model_name
    model: str = Field(
        ...,
        title="Model",
        description="Model for the Agent",
    )
    organization_id: Optional[str] = Field(
        None,
        title="Organization ID",
        description="Organization ID for the Agent",
    )
    is_private: Optional[bool] = Field(
        False,
        title="Is Private",
        description="If the Agent is private",
    )

    class Config:
        from_attributes = True
        use_enum_values = True


class ListAgentsResponse(BaseModel):
    """
    Response schema for listing agents
    """
    agents: list[Agent] = Field(
        ...,
        title="Agents",
        description="List of Agents",
    )


class UpdateAgentNoDeploymentModel(ABC, BaseModel):
    """
    Abstract class for updating agents
    """
    name: Optional[str] = Field(
        None,
        title="Name",
        description="Name of the Agent",
    )
    version: Optional[int] = Field(
        None,
        title="Version",
        description="Version of the Agent",
    )
    description: Optional[str] = Field(
        None,
        title="Description",
        description="Agent Description",
    )
    preamble: Optional[str] = Field(
        None,
        title="Preamble",
        description="The preamble for the Agent",
    )
    temperature: Optional[float] = Field(
        None,
        title="Temperature",
        description="The temperature for the Agent",
    )
    tools: Optional[list[str]] = Field(
        None,
        title="Tools",
        description="List of tools for the Agent",
    )
    organization_id: Optional[str] = Field(
        None,
        title="Organization ID",
        description="Organization ID for the Agent",
    )
    is_private: Optional[bool] = Field(
        None,
        title="Is Private",
        description="If the Agent is private",
    )

    class Config:
        from_attributes = True
        use_enum_values = True

class UpdateAgentDB(UpdateAgentNoDeploymentModel):
    """
    Model for updating agents
    """
    model_id: Optional[str] = Field(
        None,
        title="Model ID",
        description="Model ID",
    )
    deployment_id: Optional[str] = Field(
        None,
        title="Deployment ID",
        description="Deployment ID",
    )

    model_config = {
        "from_attributes": True,
        "use_enum_values": True,
        "protected_namespaces": (),
    }


class UpdateAgentRequest(UpdateAgentNoDeploymentModel):
    """
    Schema to update an agent
    """
    deployment: Optional[str] = Field(
        None,
        title="Deployment",
        description="Deployment for the Agent",
    )
    model: Optional[str] = Field(
        None,
        title="Model",
        description="Model for the Agent",
    )
    tools_metadata: Optional[list[CreateAgentToolMetadataRequest]] = Field(
        None,
        title="Tools Metadata",
        description="Tools metadata for the Agent",
    )
    class Config:
        from_attributes = True
        use_enum_values = True


class DeleteAgent(BaseModel):
    """
    Response for deleting an agent
    """
    pass
