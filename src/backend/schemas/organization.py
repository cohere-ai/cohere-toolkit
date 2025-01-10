import datetime
from abc import ABC
from typing import Optional

from pydantic import BaseModel, Field


class OrganizationBase(ABC, BaseModel):
    """
    Abstract class for organization schemas
    """
    name: str = Field(
        ...,
        title="Name",
        description="Name of the organization",
    )


class Organization(OrganizationBase):
    """
    Schema for an organization
    """
    id: str = Field(
        ...,
        title="ID",
        description="Unique identifier of the organization",
    )
    created_at: datetime.datetime = Field(
        ...,
        title="Created At Timestamp",
        description="When organization was created",
    )
    updated_at: datetime.datetime = Field(
        ...,
        title="Updated At Timestamp",
        description="When organization was updated",
    )

    class Config:
        from_attributes = True


class CreateOrganization(OrganizationBase):
    """
    Request to create an organization
    """
    pass


class UpdateOrganization(OrganizationBase):
    """
    Request to update an organization
    """
    name: Optional[str] = Field(
        None,
        title="Name",
        description="Name of the organization",
    )


class DeleteOrganization(BaseModel):
    """
    Response when deleting organization
    """
    pass
