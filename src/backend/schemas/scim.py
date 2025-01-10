from abc import ABC
from typing import ClassVar, Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from backend.database_models import Group as DBGroup
from backend.database_models import User as DBUser


class BaseSchema(ABC, BaseModel):
    """
    Abstract class for other schemas
    """
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class Meta(BaseSchema):
    """
    Schema for metadata
    """
    resource_type: str = Field(
        ...,
        title="Resource Type",
        description="Type of resource the metadata is for",
    )
    created: str = Field(
        ...,
        title="Created",
        description="When metadata was created",
    )
    last_modified: str = Field(
        ...,
        title="Last Modified",
        description="When metadata was last modified",
    )


class Name(BaseSchema):
    given_name: str = Field(
        ...,
        title="Given Name",
        description="User's given name",
    )
    family_name: str = Field(
        ...,
        title="Family Name",
        description="User's family name",
    )


class BaseUser(BaseSchema):
    user_name: Optional[str] = Field(
        None,
        title="User Name",
        description="User name",
    )
    active: Optional[bool] = Field(
        None,
        title="Active",
        description="Is user active",
    )

    schemas: list[str] = Field(
        ...,
        title="Schemas",
        description="Schemas for the user",
    )


class GroupMember(BaseSchema):
    value: str = Field(
        ...,
        title="Value",
        description="Value",
    )
    display: str = Field(
        ...,
        title="Display",
        description="Display",
    )


class BaseGroup(BaseSchema):
    schemas: list[str] = Field(
        ...,
        title="Schemas",
        description="Schemas for the group",
    )
    members: list[GroupMember] = Field(
        ...,
        title="Members",
        description="Members of the group",
    )
    display_name: str = Field(
        ...,
        title="Display Name",
        description="Display name for the group",
    )


class CreateGroup(BaseGroup):
    pass


class Email(BaseSchema):
    primary: bool = Field(
        ...,
        title="Primary",
        description="Is email the primary email",
    )
    value: Optional[str] = Field(
        None,
        title="Value",
        description="Email value",
    )
    type: str = Field(
        ...,
        title="Type",
        description="Type of email",
    )


class CreateUser(BaseUser):
    name: Name = Field(
        ...,
        title="Name",
        description="Name of user",
    )
    emails: list[Email] = Field(
        ...,
        title="Emails",
        description="List of emails for user",
    )
    externalId: str = Field(
        ...,
        title="External ID",
        description="External ID for the user",
    )


class UpdateUser(BaseUser):
    name: Name = Field(
        ...,
        title="Name",
        description="Name of user",
    )
    emails: list[Email] = Field(
        ...,
        title="Emails",
        description="List of emails for user",
    )


class Operation(BaseSchema):
    op: str = Field(
        ...,
        title="Op",
        description="Op",
    )
    value: dict[str, bool] = Field(
        ...,
        title="Value",
        description="Value",
    )


class GroupOperation(BaseSchema):
    op: str = Field(
        ...,
        title="Op",
        description="Op",
    )
    path: Optional[str] = Field(
        None,
        title="Path",
        description="Path",
    )
    value: dict[str, str]|list[dict[str, str]] = Field(
        ...,
        title="Value",
        description="Value",
    )


class PatchUser(BaseSchema):
    schemas: list[str] = Field(
        ...,
        title="Schemas",
        description="Schemas for user",
    )
    Operations: list[Operation] = Field(
        ...,
        title="Operations",
        description="Operations for the user",
    )


class PatchGroup(BaseSchema):
    schemas: list[str] = Field(
        ...,
        title="Schemas",
        description="Schemas for group",
    )
    Operations: list[GroupOperation] = Field(
        ...,
        title="Operations",
        description="Operations for the group",
    )


class Group(BaseGroup):
    id: str = Field(
        ...,
        title="ID",
        description="Unique identifier for the group",
    )
    display_name: str = Field(
        ...,
        title="Display Name",
        description="Display name for the group",
    )
    meta: Meta = Field(
        ...,
        title="Meta",
        description="Metadata for the group",
    )

    @staticmethod
    def from_db_group(db_group: DBGroup) -> "Group":
        return Group(
            id=db_group.id,
            display_name=db_group.display_name,
            members=[
                GroupMember(value=ua.user_id, display=ua.display)
                for ua in db_group.user_associations
            ],
            meta=Meta(
                resourceType="Group",
                created=db_group.created_at.isoformat(),
                lastModified=db_group.updated_at.isoformat(),
            ),
            schemas=["urn:ietf:params:scim:schemas:core:2.0:Group"],
        )


class User(BaseUser):
    id: str = Field(
        ...,
        title="ID",
        description="Unique identifier for the user",
    )
    external_id: str = Field(
        ...,
        title="External ID",
        description="External ID for the user",
    )
    meta: Meta = Field(
        ...,
        title="Meta",
        description="Metadata for the user",
    )

    @staticmethod
    def from_db_user(db_user: DBUser) -> "User":
        return User(
            id=db_user.id,
            user_name=db_user.user_name,
            active=db_user.active,
            external_id=db_user.external_id,
            meta=Meta(
                resourceType="User",
                created=db_user.created_at.isoformat(),
                lastModified=db_user.updated_at.isoformat(),
            ),
            schemas=["urn:ietf:params:scim:schemas:core:2.0:User"],
        )


class BaseListResponse(BaseSchema):
    schemas: ClassVar[list[str]] = [
        "urn:ietf:params:scim:api:messages:2.0:ListResponse"
    ]
    total_results: int = Field(
        ...,
        title="Total Results",
        description="Total results available",
    )
    start_index: int = Field(
        ...,
        title="Start Index",
        description="Start index for returned results",
    )
    items_per_page: int = Field(
        ...,
        title="Items Per Page",
        description="Total results returned in the request",
    )


class ListUserResponse(BaseListResponse):
    resources: list[User] = Field(
        ...,
        title="Resources",
        description="List of Users",
        alias="Resources",
    )


class ListGroupResponse(BaseListResponse):
    resources: list[Group] = Field(
        ...,
        title="Resources",
        description="List of Groups",
        alias="Resources",
    )
