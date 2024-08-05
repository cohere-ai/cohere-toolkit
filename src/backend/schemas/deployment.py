from typing import Any, Dict, List, Optional, Type

from pydantic import BaseModel, Field, field_validator

# from backend.model_deployments.base import BaseDeployment
from backend.schemas.model import ModelSimple


class DeploymentSimple(BaseModel):
    id: str
    name: str
    deployment_class_name: Optional[str] = Field(exclude=True, default="")
    env_vars: Optional[List[str]]
    is_available: bool
    is_community: bool

    class Config:
        from_attributes = True


class DeploymentWithModels(BaseModel):
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    is_available: bool = False
    is_community: Optional[bool] = False
    env_vars: Optional[List[str]]
    deployment_class_name: Optional[str] = Field(exclude=True, default="")
    models: list[ModelSimple]

    class Config:
        from_attributes = True


class Deployment(BaseModel):
    id: Optional[str] = None
    name: str
    models: list[str]
    is_available: bool = False
    deployment_class: Optional[Type[Any]] = Field(exclude=True, default=None)
    env_vars: Optional[List[str]]
    description: Optional[str] = None
    deployment_class_name: Optional[str] = Field(exclude=True, default="")
    is_community: Optional[bool] = False
    default_deployment_config: Optional[Dict[str, str]] = Field(
        default_factory=dict, exclude=True
    )
    kwargs: Optional[dict] = Field(exclude=True, default={})

    class Config:
        from_attributes = True

    @classmethod
    def custom_transform(cls, obj):
        data = {
            "id": obj.id,
            "name": obj.name,
            "description": obj.description,
            "deployment_class": obj.deployment_class if obj.deployment_class else None,
            "deployment_class_name": (
                obj.deployment_class_name if obj.deployment_class_name else None
            ),
            "models": [model.name for model in obj.models],
            "is_community": obj.is_community,
            "is_available": obj.is_available,
            "env_vars": obj.env_vars,
            "default_deployment_config": obj.default_deployment_config,
        }
        return cls(**data)


class DeploymentCreate(BaseModel):
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    deployment_class_name: str
    is_community: bool = False
    default_deployment_config: Dict[str, str]


class DeploymentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    deployment_class_name: Optional[str] = None
    is_community: Optional[bool] = None
    default_deployment_config: Optional[Dict[str, str]] = None


class DeleteDeployment(BaseModel):
    pass


class UpdateDeploymentEnv(BaseModel):
    env_vars: dict[str, str]
