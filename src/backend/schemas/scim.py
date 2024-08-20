from typing import ClassVar, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from backend.database_models import Group as DBGroup
from backend.database_models import User as DBUser


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class Meta(BaseSchema):
    resource_type: str
    created: str
    last_modified: str


class Name(BaseSchema):
    given_name: str
    family_name: str


class BaseUser(BaseSchema):
    user_name: Optional[str]
    active: Optional[bool]

    schemas: list[str]


class GroupMember(BaseSchema):
    value: str
    display: str


class BaseGroup(BaseSchema):
    schemas: list[str]
    members: list[GroupMember]
    display_name: str


class CreateGroup(BaseGroup):
    pass


class Email(BaseSchema):
    primary: bool
    value: Optional[str] = None
    type: str


class CreateUser(BaseUser):
    name: Name
    emails: List[Email]
    externalId: str


class UpdateUser(BaseUser):
    emails: List[Email]
    name: Name


class Operation(BaseSchema):
    op: str
    value: dict[str, bool]


class GroupOperation(BaseSchema):
    op: str
    path: Optional[str] = None
    value: Union[Dict[str, str], list[Dict[str, str]]]


class PatchUser(BaseSchema):
    schemas: list[str]
    Operations: list[Operation]


class PatchGroup(BaseSchema):
    schemas: list[str]
    Operations: list[GroupOperation]


class Group(BaseGroup):
    id: str
    display_name: str
    meta: Meta

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
    id: str
    external_id: str
    meta: Meta

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
    total_results: int
    start_index: int
    items_per_page: int


class ListUserResponse(BaseListResponse):
    resources: list[User] = Field(alias='Resources')


class ListGroupResponse(BaseListResponse):
    resources: list[Group] = Field(alias='Resources')
