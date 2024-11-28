from typing import Dict, List, Optional

from pydantic import BaseModel, Field

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
    deployment_class_name: Optional[str] = Field(exclude=True, default="")
    env_vars: Optional[List[str]]
    is_available: bool = False
    is_community: Optional[bool] = False
    models: list[ModelSimple]

    class Config:
        from_attributes = True


class DeploymentDefinition(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    config: Dict[str, str] = {}
    is_available: bool = False
    is_community: bool = False
    models: list[str]
    class_name: str

    class Config:
        from_attributes = True

    @classmethod
    def from_db_deployment(cls, obj):
        data = {
            "id": obj.id,
            "name": obj.name,
            "description": obj.description if obj.description else None,
            "models": [model.name for model in obj.models],
            "is_community": obj.is_community,
            "is_available": obj.is_available,
            "config": obj.default_deployment_config,
            "class_name": obj.deployment_class_name,
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
