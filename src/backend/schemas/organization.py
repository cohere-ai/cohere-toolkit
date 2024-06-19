import datetime
from typing import Optional

from pydantic import BaseModel

from backend.services.auth import BasicAuthentication


class OrganizationBase(BaseModel):
    name: str


class Organization(OrganizationBase):
    id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True


class CreateOrganization(OrganizationBase):
    pass


class UpdateOrganization(OrganizationBase):
    pass


class DeleteOrganization(BaseModel):
    pass
