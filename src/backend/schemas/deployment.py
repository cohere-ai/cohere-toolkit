from typing import Optional

from pydantic import BaseModel, Field


class DeploymentDefinition(BaseModel):
    """
    Deployment Definition
    """
    id: str = Field(
        ...,
        title="ID",
        description="Unique Identifier for the Deployment",
    )
    name: str = Field(
        ...,
        title="Name",
        description="Name of the Deployment",
    )
    description: Optional[str] = Field(
        None,
        title="Description",
        description="Description of the deployment",
    )
    config: dict[str, str] = Field(
        {},
        title="Config",
        description="Config for the deployment",
    )
    is_available: bool = Field(
        False,
        title="Is Available",
        description="Is deployment is available",
    )
    is_community: Optional[bool] = Field(
        False,
        title="Is Community",
        description="Is the deployment from the commmunity",
    )
    models: list[str] = Field(
        ...,
        title="Models",
        description="List of models for the deployment",
    )
    class_name: str = Field(
        ...,
        title="Class Name",
        description="Deployment class name",
    )

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
    """
    Deployment Create Schema
    """
    id: Optional[str] = Field(
        None,
        title="ID",
        description="Unique Identifier for the Deployment",
    )
    name: str = Field(
        ...,
        title="Name",
        description="Name of the Deployment",
    )
    description: Optional[str] = Field(
        None,
        title="Description",
        description="Description of the deployment",
    )
    deployment_class_name: str = Field(
        ...,
        title="Deployment Class Name",
        description="Deployment Class Name",
    )
    is_community: bool = Field(
        False,
        title="Is Community",
        description="Is the deployment from the commmunity",
    )
    default_deployment_config: dict[str, str] = Field(
        ...,
        title="Default Deployment Config",
        description="The default deployment configuration",
    )


class DeploymentUpdate(BaseModel):
    """
    Deployment Update Schema
    """
    name: Optional[str] = Field(
        None,
        title="Name",
        description="Name of the Deployment",
    )
    description: Optional[str] = Field(
        None,
        title="Description",
        description="Description of the deployment",
    )
    deployment_class_name: Optional[str] = Field(
        None,
        title="Deployment Class Name",
        description="Deployment Class Name",
    )
    is_community: Optional[bool] = Field(
        None,
        title="Is Community",
        description="Is the deployment from the commmunity",
    )
    default_deployment_config: Optional[dict[str, str]] = Field(
        None,
        title="Default Deployment Config",
        description="The default deployment configuration",
    )


class DeleteDeployment(BaseModel):
    """
    Delete Deployment Response
    """
    pass


class UpdateDeploymentEnv(BaseModel):
    """
    Request to update Deployment Environment Variables
    """
    env_vars: dict[str, str] = Field(
        ...,
        title="Env Vars",
        description="Environment Variables for the Deployment",
    )
