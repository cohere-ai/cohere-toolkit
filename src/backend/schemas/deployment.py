from typing import Optional, Type

from pydantic import BaseModel, Field

from backend.model_deployments import BaseDeployment


class Deployment(BaseModel):
    name: str
    models: list[str]
    is_available: bool = Field(exclude=True)
    deployment_class: Type[BaseDeployment] = Field(exclude=True)
    env_vars: list[str]
    kwargs: Optional[dict] = Field(exclude=True, default={})

    class Config:
        from_attributes = True


class UpdateDeploymentEnv(BaseModel):
    env_vars: dict[str, str]
