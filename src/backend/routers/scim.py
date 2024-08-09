from typing import Optional

from fastapi import APIRouter, Depends
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

import backend.crud.group as group_crud
import backend.crud.user as user_crud
from backend.config import Settings
from backend.config.routers import RouterName
from backend.database_models import DBSessionDep
from backend.database_models import Group as DBGroup
from backend.database_models import User as DBUser
from backend.database_models import UserGroupAssociation
from backend.schemas.context import Context
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

SCIM_PREFIX = "/scim/v2"
scim_auth = Settings().auth.scim
router = APIRouter(prefix=SCIM_PREFIX)
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
    session: DBSessionDep,
    count: int = 100,
    start_index: int = 1,
    filter: Optional[str] = None,
) -> ListUserResponse:
    if filter:
        try:
            display_name = _parse_filter(filter)
        except ValueError:
            raise SCIMException(status_code=400, detail="filter not supported")
        db_user = user_crud.get_user_by_user_name(session, display_name)
        if not db_user:
            return ListUserResponse(
                totalResults=0,
                startIndex=start_index,
                itemsPerPage=count,
                Resources=[],
            )
        return ListUserResponse(
            totalResults=1,
            startIndex=start_index,
            itemsPerPage=count,
            Resources=[User.from_db_user(db_user)],
        )

    db_users = user_crud.get_external_users(
        session, offset=start_index - 1, limit=count
    )
    users = [User.from_db_user(db_user) for db_user in db_users]
    return ListUserResponse(
        totalResults=len(users),
        startIndex=start_index,
        itemsPerPage=count,
        Resources=users,
    )


@router.get("/Users/{user_id}")
async def get_user(
    user_id: str, session: DBSessionDep, ctx: Context = Depends(get_context)
):
    logger = ctx.get_logger()
    db_user = user_crud.get_user(session, user_id)
    if not db_user:
        logger.error(event="[SCIM] user not found", user_id=user_id)
        raise SCIMException(status_code=404, detail="User not found")

    return User.from_db_user(db_user)


@router.post("/Users", status_code=201)
async def create_user(
    user: CreateUser, session: DBSessionDep, ctx: Context = Depends(get_context)
):
    logger = ctx.get_logger()
    db_user = user_crud.get_user_by_external_id(session, user.externalId)
    if db_user:
        logger.error(event="[SCIM] user already exists", external_id=user.externalId)
        raise SCIMException(
            status_code=409, detail="User already exists in the database."
        )

    db_user = DBUser(
        user_name=user.userName,
        fullname=f"{user.name.givenName} {user.name.familyName}",
        email=_get_email_from_scim_user(user),
        active=user.active,
        external_id=user.externalId,
    )

    db_user = user_crud.create_user(session, db_user)
    return User.from_db_user(db_user)


@router.put("/Users/{user_id}")
async def update_user(
    user_id: str,
    user: UpdateUser,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
):
    logger = ctx.get_logger()
    db_user = user_crud.get_user(session, user_id)
    if not db_user:
        logger.error(event="[SCIM] user not found", user_id=user_id)
        raise SCIMException(status_code=404, detail="User not found")

    db_user.user_name = user.userName
    db_user.fullname = f"{user.name.givenName} {user.name.familyName}"
    db_user.active = user.active
    email_update = _get_email_from_scim_user(user)
    db_user.email = email_update

    db_user = user_crud.create_user(session, db_user)

    return User.from_db_user(db_user)


@router.patch("/Users/{user_id}")
async def patch_user(
    user_id: str,
    patch: PatchUser,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
):
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
    session: DBSessionDep,
    count: int = 100,
    start_index: int = 1,
    filter: Optional[str] = None,
) -> ListGroupResponse:
    if filter:
        try:
            display_name = _parse_filter(filter)
        except ValueError:
            raise SCIMException(status_code=400, detail="filter not supported")
        db_group = group_crud.get_group_by_name(session, display_name)
        if not db_group:
            return ListGroupResponse(
                totalResults=0,
                startIndex=start_index,
                itemsPerPage=count,
                Resources=[],
            )
        return ListGroupResponse(
            totalResults=1,
            startIndex=start_index,
            itemsPerPage=count,
            Resources=[Group.from_db_group(db_group)],
        )

    db_groups = group_crud.get_groups(session, offset=start_index - 1, limit=count)
    groups = [Group.from_db_group(db_group) for db_group in db_groups]
    return ListGroupResponse(
        totalResults=len(groups),
        startIndex=start_index,
        itemsPerPage=count,
        Resources=groups,
    )


@router.get("/Groups/{group_id}")
async def get_group(
    group_id: str, session: DBSessionDep, ctx: Context = Depends(get_context)
):
    logger = ctx.get_logger()
    db_group = group_crud.get_group(session, group_id)
    if not db_group:
        logger.error(event="[SCIM] group not found", group_id=group_id)
        raise SCIMException(status_code=404, detail="Group not found")

    return Group.from_db_group(db_group)


@router.post("/Groups", status_code=201)
async def create_group(
    group: CreateGroup, session: DBSessionDep, ctx: Context = Depends(get_context)
):
    logger = ctx.get_logger()
    db_group = group_crud.get_group_by_name(session, group.displayName)
    if db_group:
        logger.error(event="[SCIM] group already exists", group_name=group.displayName)
        raise SCIMException(
            status_code=409, detail="Group already exists in the database."
        )

    db_group = DBGroup(
        display_name=group.displayName,
    )

    db_group = group_crud.create_group(session, db_group)
    return Group.from_db_group(db_group)


@router.patch("/Groups/{group_id}")
async def patch_group(
    group_id: str,
    patch: PatchGroup,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
):
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
    group_id: str, session: DBSessionDep, ctx: Context = Depends(get_context)
):
    logger = ctx.get_logger()
    db_group = group_crud.get_group(session, group_id)
    if not db_group:
        logger.error(event="[SCIM] group not found", group_id=group_id)
        raise SCIMException(status_code=404, detail="Group not found")
    group_crud.delete_group(session, group_id)


def _get_email_from_scim_user(user: CreateUser | UpdateUser) -> str | None:
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
