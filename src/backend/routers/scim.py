import secrets
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette import status
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


def _check_basic_auth(
    credentials: Annotated[HTTPBasicCredentials, Depends(HTTPBasic())],
) -> bool:
    if not scim_auth or not scim_auth.username or not scim_auth.password:
        raise HTTPException(
            status_code=500,
            detail="SCIM token not set in the environment",
            headers={"WWW-Authenticate": "Basic"},
        )

    is_correct_username = _compare_secret(credentials.username, scim_auth.username)
    is_correct_password = _compare_secret(credentials.password, scim_auth.password)

    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    return True


def _compare_secret(actual: str, expected: str) -> bool:
    return secrets.compare_digest(actual.encode("utf8"), expected.encode("utf8"))


SCIM_PREFIX = "/scim/v2"
scim_auth = Settings().auth.scim
router = APIRouter(prefix=SCIM_PREFIX, dependencies=[Depends(_check_basic_auth)])
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
        single_filter = filter.split(" ")
        filter_value = single_filter[2].strip('"')
        db_user = user_crud.get_user_by_user_name(session, filter_value)
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
    user_id: str,
    session: DBSessionDep,
):
    db_user = user_crud.get_user(session, user_id)
    if not db_user:
        raise SCIMException(status_code=404, detail="User not found")

    return User.from_db_user(db_user)


@router.post("/Users", status_code=201)
async def create_user(
    user: CreateUser,
    session: DBSessionDep,
):
    db_user = user_crud.get_user_by_external_id(session, user.externalId)
    if db_user:
        raise SCIMException(
            status_code=409, detail="User already exists in the database."
        )

    db_user = DBUser(
        user_name=user.userName,
        fullname=f"{user.name.givenName} {user.name.familyName}",
        email=user.email,
        active=user.active,
        external_id=user.externalId,
    )

    db_user = user_crud.create_user(session, db_user)
    return User.from_db_user(db_user)


@router.put("/Users/{user_id}")
async def update_user(user_id: str, user: UpdateUser, session: DBSessionDep):
    db_user = user_crud.get_user(session, user_id)
    if not db_user:
        raise SCIMException(status_code=404, detail="User not found")

    db_user.user_name = user.userName
    db_user.fullname = f"{user.name.givenName} {user.name.familyName}"
    db_user.active = user.active
    if user.email:
        db_user.email = user.email
        

    db_user = user_crud.create_user(session, db_user)

    return User.from_db_user(db_user)


@router.patch("/Users/{user_id}")
async def patch_user(user_id: str, patch: PatchUser, session: DBSessionDep):
    db_user = user_crud.get_user(session, user_id)
    if not db_user:
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
        single_filter = filter.split(" ", maxsplit=2)
        filter_value = single_filter[2].strip('"')
        db_group = group_crud.get_group_by_name(session, filter_value)
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
async def get_group(group_id: str, session: DBSessionDep):
    db_group = group_crud.get_group(session, group_id)
    if not db_group:
        raise SCIMException(status_code=404, detail="Group not found")

    return Group.from_db_group(db_group)


@router.post("/Groups", status_code=201)
async def create_group(group: CreateGroup, session: DBSessionDep):
    db_group = group_crud.get_group_by_name(session, group.displayName)
    if db_group:
        raise SCIMException(
            status_code=409, detail="Group already exists in the database."
        )

    db_group = DBGroup(
        display_name=group.displayName,
    )

    db_group = group_crud.create_group(session, db_group)
    return Group.from_db_group(db_group)


@router.patch("/Groups/{group_id}")
async def patch_group(group_id: str, patch: PatchGroup, session: DBSessionDep):
    db_group = group_crud.get_group(session, group_id)
    if not db_group:
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
async def delete_group(group_id: str, session: DBSessionDep):
    db_group = group_crud.get_group(session, group_id)
    if not db_group:
        raise SCIMException(status_code=404, detail="Group not found")
    group_crud.delete_group(session, group_id)
