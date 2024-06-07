import datetime
from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, Field, computed_field

from backend.database_models.agent import Deployment, Model


class ModelType(str, Enum):
    COMMAND_R = "command-r"
    COMMAND_R_PLUS = "command-r-plus"
    COMMAND_LIGHT = "command-light"
    COMMAND = "command"


class DeploymentType(str, Enum):
    COHERE_PLATFORM = "Cohere Platform"
    SAGE_MAKER = "SageMaker"
    AZURE = "Azure"
    BEDROCK = "Bedrock"


class AgentBase(BaseModel):
    user_id: str


class Agent(AgentBase):
    id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    version: int
    name: str
    description: Optional[str]
    preamble: Optional[str]
    temperature: float
    # tools: List[Tool]

    model: Model
    deployment: Deployment

    class Config:
        from_attributes = True
        use_enum_values = True


class CreateAgent(BaseModel):
    name: str
    version: Optional[int] = None
    description: Optional[str] = None
    preamble: Optional[str] = None
    temperature: Optional[float] = None
    model: Model
    deployment: Deployment

    class Config:
        from_attributes = True
        use_enum_values = True


class UpdateAgent(BaseModel):
    name: Optional[str] = None
    version: Optional[int] = None
    description: Optional[str] = None
    preamble: Optional[str] = None
    temperature: Optional[float] = None
    model: Optional[Model] = None
    deployment: Optional[Deployment] = None
    # tools: Optional[List[Tool]] = None

    class Config:
        from_attributes = True
        use_enum_values = True


class DeleteAgent(BaseModel):
    pass
