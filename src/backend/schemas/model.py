from abc import ABC
from typing import Optional

from pydantic import BaseModel, Field


class BaseModelSchema(ABC, BaseModel):
    """
    Abstract class for Model Schemas
    """
    name: str = Field(
        ...,
        title="Name",
        description="Model name",
    )
    cohere_name: Optional[str] = Field(
        None,
        title="Cohere Name",
        description="Cohere model name",
    )
    description: Optional[str] = Field(
        None,
        title="Description",
        description="Model description",
    )


class Model(BaseModelSchema):
    id: str = Field(
        ...,
        title="ID",
        description="Unique identifier for the model"
    )
    deployment_id: str = Field(
        ...,
        title="Deployment ID",
        description="Unique identifier for the deployment"
    )

    class Config:
        from_attributes = True


class ModelCreate(BaseModelSchema):
    deployment_id: str = Field(
        ...,
        title="Deployment ID",
        description="Unique identifier for the deployment"
    )


class ModelUpdate(BaseModelSchema):
    name: Optional[str] = Field(
        None,
        title="Name",
        description="Model name",
    )
    deployment_id: Optional[str] = Field(
        None,
        title="Deployment ID",
        description="Unique identifier for the deployment"
    )


class DeleteModel(BaseModel):
    """
    Response for deleting a model
    """
    pass
