from fastapi import APIRouter, Depends
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

import backend.crud.group as group_crud
import backend.crud.user as user_crud
from backend.config import Settings
from backend.config.routers import RouterName
from backend.database_models import DBSessionDep, UserGroupAssociation
from backend.database_models import Group as DBGroup
from backend.database_models import User as DBUser
from backend.schemas.context import Context
from backend.schemas.params.scim import (
    GroupIdPathParam,
    ScimPaginationQueryParams,
    UserIdPathParam,
)
from backend.schemas.scim import (
    CreateGroup,
    CreateUser,
    Group,
    ListGroupResponse,
    ListUserResponse,
    PatchGroup,
    PatchUser,
    UpdateUser,
    User,
)
from backend.services.context import get_context

scim_auth = Settings().get('auth.scim')
router = APIRouter(
    prefix="/scim/v2",
    tags=[RouterName.SCIM]
)
router.name = RouterName.SCIM


class SCIMException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail


async def scim_exception_handler(request: Request, exc: SCIMException) -> Response:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
        },
    )


@router.get("/Users")
async def get_users(
    page_params: ScimPaginationQueryParams,
    session: DBSessionDep,
) -> ListUserResponse:
    """
    Return users
    """
    if page_params.filter:
        try:
            display_name = _parse_filter(page_params.filter)
        except ValueError:
            raise SCIMException(status_code=400, detail="filter not supported")
        db_user = user_crud.get_user_by_user_name(session, display_name)
        if not db_user:
            return ListUserResponse(
                total_results=0,
                start_index=page_params.start_index,
                items_per_page=page_params.count,
                resources=[],
            )
        return ListUserResponse(
            total_results=1,
            start_index=page_params.start_index,
            items_per_page=page_params.count,
            resources=[User.from_db_user(db_user)],
        )

    db_users = user_crud.get_external_users(
        session, offset=page_params.start_index - 1, limit=page_params.count
    )
    users = [User.from_db_user(db_user) for db_user in db_users]
    return ListUserResponse(
        total_results=len(users),
        start_index=page_params.start_index,
        items_per_page=page_params.count,
        resources=users,
    )


@router.get("/Users/{user_id}")
async def get_user(
    user_id: UserIdPathParam,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
):
    """
    Get user by User ID
    """
    logger = ctx.get_logger()
    db_user = user_crud.get_user(session, user_id)
    if not db_user:
        logger.error(event="[SCIM] user not found", user_id=user_id)
        raise SCIMException(status_code=404, detail="User not found")

    return User.from_db_user(db_user)


@router.post("/Users", status_code=201)
async def create_user(
    user: CreateUser,
    session: DBSessionDep,
):
    """
    Create a new user
    """
    db_user = user_crud.get_user_by_external_id(session, user.externalId)
    if not db_user:
        db_user = DBUser()

    db_user.user_name = user.user_name
    db_user.fullname = f"{user.name.given_name} {user.name.family_name}"
    db_user.email = _get_email_from_scim_user(user)
    db_user.active = user.active
    db_user.external_id = user.externalId

    db_user = user_crud.create_user(session, db_user)
    return User.from_db_user(db_user)


@router.put("/Users/{user_id}")
async def update_user(
    user_id: UserIdPathParam,
    user: UpdateUser,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
):
    """
    Update a user
    """
    logger = ctx.get_logger()
    db_user = user_crud.get_user(session, user_id)
    if not db_user:
        logger.error(event="[SCIM] user not found", user_id=user_id)
        raise SCIMException(status_code=404, detail="User not found")

    db_user.user_name = user.user_name
    db_user.fullname = f"{user.name.given_name} {user.name.family_name}"
    db_user.active = user.active
    email_update = _get_email_from_scim_user(user)
    db_user.email = email_update

    db_user = user_crud.create_user(session, db_user)

    return User.from_db_user(db_user)


@router.patch("/Users/{user_id}")
async def patch_user(
    user_id: UserIdPathParam,
    patch: PatchUser,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
):
    """
    Patch a user
    """
    logger = ctx.get_logger()
    db_user = user_crud.get_user(session, user_id)
    if not db_user:
        logger.error(event="[SCIM] user not found", user_id=user_id)
        raise SCIMException(status_code=404, detail="User not found")

    for operation in patch.Operations:
        k, v = list(operation.value.items())[0]
        setattr(db_user, k, v)

    db_user = user_crud.create_user(session, db_user)

    return User.from_db_user(db_user)


@router.get("/Groups")
async def get_groups(
    *,
    page_params: ScimPaginationQueryParams,
    session: DBSessionDep,
) -> ListGroupResponse:
    """
    Return Groups
    """
    if page_params.filter:
        try:
            display_name = _parse_filter(page_params.filter)
        except ValueError:
            raise SCIMException(status_code=400, detail="filter not supported")
        db_group = group_crud.get_group_by_name(session, display_name)
        if not db_group:
            return ListGroupResponse(
                total_results=0,
                start_index=page_params.start_index,
                items_per_page=page_params.count,
                resources=[],
            )
        return ListGroupResponse(
            total_results=1,
            start_index=page_params.start_index,
            items_per_page=page_params.count,
            resources=[Group.from_db_group(db_group)],
        )

    db_groups = group_crud.get_groups(session, offset=page_params.start_index - 1, limit=page_params.count)
    groups = [Group.from_db_group(db_group) for db_group in db_groups]
    return ListGroupResponse(
        total_results=len(groups),
        start_index=page_params.start_index,
        items_per_page=page_params.count,
        resources=groups,
    )


@router.get("/Groups/{group_id}")
async def get_group(
    group_id: GroupIdPathParam,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
):
    """
    Get group by group ID
    """
    logger = ctx.get_logger()
    db_group = group_crud.get_group(session, group_id)
    if not db_group:
        logger.error(event="[SCIM] group not found", group_id=group_id)
        raise SCIMException(status_code=404, detail="Group not found")

    return Group.from_db_group(db_group)


@router.post("/Groups", status_code=201)
async def create_group(
    group: CreateGroup,
    session: DBSessionDep,
):
    """
    Create a group
    """
    db_group = group_crud.get_group_by_name(session, group.display_name)
    if not db_group:
        db_group = DBGroup()

    db_group.display_name = group.display_name

    db_group = group_crud.create_group(session, db_group)
    return Group.from_db_group(db_group)


@router.patch("/Groups/{group_id}")
async def patch_group(
    group_id: GroupIdPathParam,
    patch: PatchGroup,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
):
    """
    Patch a group
    """
    logger = ctx.get_logger()
    db_group = group_crud.get_group(session, group_id)
    if not db_group:
        logger.error(event="[SCIM] group not found", group_id=group_id)
        raise SCIMException(status_code=404, detail="Group not found")

    for operation in patch.Operations:
        if operation.op == "replace" and "displayName" in operation.value:
            db_group.display_name = operation.value["displayName"]
            db_group = group_crud.update_group(session, db_group)
        if operation.op == "add" and operation.path == "members":
            associations = []
            for value in operation.value:
                association = UserGroupAssociation(
                    user_id=value["value"],
                    group_id=db_group.id,
                    display=value["display"],
                )
                associations.append(association)
            db_group = group_crud.add_users(session, db_group, associations)
        if operation.op == "replace" and operation.path == "members":
            associations = []
            for value in operation.value:
                association = UserGroupAssociation(
                    user_id=value["value"],
                    group_id=db_group.id,
                    display=value["display"],
                )
                associations.append(association)
            db_group = group_crud.set_users(session, db_group, associations)

    return Group.from_db_group(db_group)


@router.delete("/Groups/{group_id}", status_code=204)
async def delete_group(
    group_id: GroupIdPathParam,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
):
    """
    Delete a group
    """
    logger = ctx.get_logger()
    db_group = group_crud.get_group(session, group_id)
    if not db_group:
        logger.error(event="[SCIM] group not found", group_id=group_id)
        raise SCIMException(status_code=404, detail="Group not found")
    group_crud.delete_group(session, group_id)


def _get_email_from_scim_user(user: CreateUser | UpdateUser) -> str | None:
    """
    Return the primary email or a SCIM user
    """
    for email_obj in user.emails:
        if email_obj.primary:
            return email_obj.value
    return None


def _parse_filter(filter: str) -> str:
    """
    Parse a filter like `displayName eq "test"` into a value. Raises a ValueError if the filter is not valid.
    """
    try:
        filter_column, operator, value = filter.split(" ", maxsplit=2)
        if filter_column not in ["displayName", "userName"]:
            raise ValueError(f"filter not supported: {filter}")
        if operator != "eq":
            raise ValueError(f"filter not supported: {filter}")
        filter_value = value.strip('"')
        return filter_value
    except Exception as e:
        raise ValueError(f"Invalid filter: {filter}") from e
