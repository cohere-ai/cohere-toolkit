from typing import Optional

from fastapi import APIRouter
from starlette.responses import JSONResponse

import backend.crud.user as user_repo
from backend.config.routers import RouterName
from backend.database_models import DBSessionDep, User as DBUser
from backend.schemas.scim import ListUserResponse, User, CreateUser, UpdateUser, PatchUser

router = APIRouter(prefix="/scim/v2")
router.name = RouterName.SCIM


class SCIMException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail


@router.get("/Users")
async def get_users(session: DBSessionDep, count: int = 100, start_index: int = 1,
                    filter: Optional[str] = None) -> ListUserResponse:
    # TODO implement filter
    db_users = user_repo.get_external_users(session, offset=start_index - 1, limit=count)
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


@router.post("/Users", status_code=201)
async def create_user(user: CreateUser, session: DBSessionDep):
    db_user = user_repo.get_user_by_external_id(session, user.externalId)
    if not db_user:
        raise SCIMException(status_code=404, detail="User not found")

    db_user = DBUser(
        user_name=user.userName,
        fullname=f"{user.name.givenName} {user.name.familyName}",
        active=user.active,
        external_id=user.externalId,
    )

    db_user = user_repo.create_user(session, db_user)
    r = User.from_db_user(db_user)
    return r


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
