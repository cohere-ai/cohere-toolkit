from typing import Type

from pydantic import BaseModel, Field

from backend.chat.custom.model_deployments.base import BaseDeployment


class Deployment(BaseModel):
    name: str
    models: list[str]
    is_available: bool = Field(exclude=True)
    deployment_class: Type[BaseDeployment] = Field(exclude=True)
    env_vars: list[str]

    class Config:
        from_attributes = True


class UpdateDeploymentEnv(BaseModel):
    env_vars: dict[str, str]
