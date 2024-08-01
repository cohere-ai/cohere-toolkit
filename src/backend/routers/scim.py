from typing import Optional

from fastapi import APIRouter

import backend.crud.user as user_repo
import backend.crud.group as group_repo
from backend.config.routers import RouterName
from backend.database_models import DBSessionDep, User as DBUser, Group as DBGroup
from backend.schemas.scim import (
    ListUserResponse,
    User,
    Group,
    CreateUser,
    UpdateUser,
    PatchUser,
    PatchGroup,
    CreateGroup,
)

router = APIRouter(prefix="/scim/v2")
router.name = RouterName.SCIM


class SCIMException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail


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
        db_user = user_repo.get_user_by_user_name(session, filter_value)
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

    db_users = user_repo.get_external_users(
        session, offset=start_index - 1, limit=count
    )
    users = [User.from_db_user(db_user) for db_user in db_users]
    return ListUserResponse(
        totalResults=len(users),
        startIndex=start_index,
        itemsPerPage=count,
        Resources=users,
    )


@router.get("/Groups")
async def get_groups(
    session: DBSessionDep,
    count: int = 100,
    start_index: int = 1,
    filter: Optional[str] = None,
) -> ListUserResponse:
    if filter:
        single_filter = filter.split(" ")
        filter_value = single_filter[2].strip('"')
        db_group = group_repo.get_group_by_name(session, filter_value)
        if not db_group:
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
            Resources=[Group.from_db_group(db_group)],
        )

    db_users = user_repo.get_external_users(
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
async def get_user(user_id: str, session: DBSessionDep):
    db_user = user_repo.get_user(session, user_id)
    if not db_user:
        raise SCIMException(status_code=404, detail="User not found")

    return User.from_db_user(db_user)


@router.get("/Groups/{group_id}")
async def get_group(group_id: str, session: DBSessionDep):
    db_group = group_repo.get_group(session, group_id)
    if not db_group:
        raise SCIMException(status_code=404, detail="User not found")

    return Group.from_db_group(db_group)

@router.post("/Users", status_code=201)
async def create_user(user: CreateUser, session: DBSessionDep):
    db_user = user_repo.get_user_by_external_id(session, user.externalId)
    if db_user:
        raise SCIMException(
            status_code=409, detail="User already exists in the database."
        )

    db_user = DBUser(
        user_name=user.userName,
        fullname=f"{user.name.givenName} {user.name.familyName}",
        active=user.active,
        external_id=user.externalId,
    )

    db_user = user_repo.create_user(session, db_user)
    return User.from_db_user(db_user)


@router.post("/Groups", status_code=201)
async def create_group(group: CreateGroup, session: DBSessionDep):
    print(group)
    # db_group = group_repo.get_group_by_name(session, group.displayName)
    # # TODO: do we need this check?
    # if db_group:
    #     raise SCIMException(
    #         status_code=409, detail="Group already exists in the database."
    #     )

    db_group = DBGroup(
        display_name=group.displayName,
        members=[],
    )

    g = group_repo.create_group(session, db_group)
    return Group.from_db_group(g)


@router.put("/Users/{user_id}")
async def update_user(user_id: str, user: UpdateUser, session: DBSessionDep):
    db_user = user_repo.get_user(session, user_id)
    if not db_user:
        raise SCIMException(status_code=404, detail="User not found")

    db_user.user_name = user.userName
    db_user.fullname = f"{user.name.givenName} {user.name.familyName}"
    db_user.active = user.active

    session.commit()

    return User.from_db_user(db_user)


@router.patch("/Groups/{group_id}")
async def update_grup(group_id: str, patch: PatchGroup, session: DBSessionDep):
    db_user = user_repo.get_user(session, user_id)
    if not db_user:
        raise SCIMException(status_code=404, detail="User not found")

    db_user.user_name = user.userName
    db_user.fullname = f"{user.name.givenName} {user.name.familyName}"
    db_user.active = user.active

    session.commit()

    return User.from_db_user(db_user)


@router.patch("/Users/{user_id}")
async def patch_user(user_id: str, patch: PatchUser, session: DBSessionDep):
    db_user = user_repo.get_user(session, user_id)
    if not db_user:
        raise SCIMException(status_code=404, detail="User not found")

    for operation in patch.Operations:
        k, v = list(operation.value.items())[0]
        setattr(db_user, k, v)

    session.commit()

    return User.from_db_user(db_user)
