import datetime
from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, Field

from backend.schemas.deployment import DeploymentWithModels as DeploymentSchema
from backend.schemas.deployment import ModelSimple as ModelSchema


class AgentVisibility(StrEnum):
    PRIVATE = "private"
    PUBLIC = "public"
    ALL = "all"


class AgentBase(BaseModel):
    user_id: str
    organization_id: Optional[str] = None


class AgentToolMetadata(BaseModel):
    id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    user_id: Optional[str]
    agent_id: str
    tool_name: str
    artifacts: list[dict]

    class Config:
        from_attributes = True
        use_enum_values = True


class AgentToolMetadataPublic(AgentToolMetadata):
    user_id: Optional[str] = Field(exclude=True)

    class Config:
        from_attributes = True


class CreateAgentToolMetadataRequest(BaseModel):
    id: Optional[str] = None
    tool_name: str
    artifacts: list[dict]


class UpdateAgentToolMetadataRequest(BaseModel):
    id: Optional[str] = None
    tool_name: Optional[str] = None
    artifacts: Optional[list[dict]] = None


class DeleteAgentToolMetadata(BaseModel):
    pass


# Agent
class Agent(AgentBase):
    id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    version: int
    name: str
    description: Optional[str]
    preamble: Optional[str]
    temperature: float
    tools: Optional[list[str]]
    tools_metadata: list[AgentToolMetadataPublic]
    deployments: list[DeploymentSchema]
    deployment: Optional[str]
    model: Optional[str]
    is_private: Optional[bool]

    class Config:
        from_attributes = True
        use_enum_values = True


class AgentPublic(Agent):
    organization_id: Optional[str] = Field(exclude=True)
    tools_metadata: Optional[list[AgentToolMetadataPublic]] = None


class CreateAgentRequest(BaseModel):
    name: str
    version: Optional[int] = None
    description: Optional[str] = None
    preamble: Optional[str] = None
    temperature: Optional[float] = None
    tools: Optional[list[str]] = None
    tools_metadata: Optional[list[CreateAgentToolMetadataRequest]] = None
    deployment_config: Optional[dict[str, str]] = None
    is_default_deployment: Optional[bool] = False
    # model_id or model_name
    model: str
    # deployment_id or deployment_name
    deployment: str
    organization_id: Optional[str] = None
    is_private: Optional[bool] = False

    class Config:
        from_attributes = True
        use_enum_values = True


class ListAgentsResponse(BaseModel):
    agents: list[Agent]


class UpdateAgentRequest(BaseModel):
    name: Optional[str] = None
    version: Optional[int] = None
    description: Optional[str] = None
    preamble: Optional[str] = None
    temperature: Optional[float] = None
    model: Optional[str] = None
    deployment: Optional[str] = None
    deployment_config: Optional[dict[str, str]] = None
    is_default_deployment: Optional[bool] = False
    is_default_model: Optional[bool] = False
    organization_id: Optional[str] = None
    tools: Optional[list[str]] = None
    tools_metadata: Optional[list[CreateAgentToolMetadataRequest]] = None

    class Config:
        from_attributes = True
        use_enum_values = True


class DeleteAgent(BaseModel):
    pass
