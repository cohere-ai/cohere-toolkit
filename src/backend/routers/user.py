from fastapi import APIRouter, Depends, HTTPException

from backend.config.auth import is_authentication_enabled
from backend.config.routers import RouterName
from backend.crud import user as user_crud
from backend.database_models import User as UserModel
from backend.database_models.database import DBSessionDep
from backend.schemas.context import Context
from backend.schemas.params.shared import PaginationQueryParams
from backend.schemas.params.user import UserIdPathParam
from backend.schemas.user import CreateUser, DeleteUser, UpdateUser, User
from backend.schemas.user import User as UserSchema
from backend.services.auth.request_validators import validate_authorization
from backend.services.context import get_context

router = APIRouter(
    prefix="/v1/users",
    tags=[RouterName.USER],
)
router.name = RouterName.USER

auth_dependencies = [Depends(validate_authorization)] if is_authentication_enabled() else []


@router.post("", response_model=User)
async def create_user(
    user: CreateUser,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
) -> User:
    """
    Create a new user.
    """
    db_user = UserModel(**user.model_dump(exclude_none=True))
    db_user = user_crud.create_user(session, db_user)

    user_schema = UserSchema.model_validate(db_user)
    ctx.with_user(user=user_schema)

    return db_user


@router.get(
    "",
    response_model=list[User],
    dependencies=auth_dependencies,
)
async def list_users(
    page_params: PaginationQueryParams,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
) -> list[User]:
    """
    List all users.
    """
    return user_crud.get_users(session, offset=page_params.offset, limit=page_params.limit)


@router.get(
    "/{user_id}",
    response_model=User,
    dependencies=auth_dependencies,
)
async def get_user(
    user_id: UserIdPathParam,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
) -> User:
    """
    Get a user by ID.

    Raises:
        HTTPException: If the user with the given ID is not found.
    """

    user = user_crud.get_user(session, user_id)
    if not user:
        raise HTTPException(
            status_code=404, detail=f"User with ID: {user_id} not found."
        )

    user_schema = UserSchema.model_validate(user)
    ctx.with_user(user=user_schema)
    return user


@router.put(
    "/{user_id}",
    response_model=User,
    dependencies=auth_dependencies,
)
async def update_user(
    user_id: UserIdPathParam,
    new_user: UpdateUser,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
) -> User:
    """
    Update a user by ID.

    Raises:
        HTTPException: If the user with the given ID is not found.
    """
    user = user_crud.get_user(session, user_id)

    if not user:
        raise HTTPException(
            status_code=404, detail=f"User with ID: {user_id} not found."
        )

    user = user_crud.update_user(session, user, new_user)
    user_schema = UserSchema.model_validate(user)
    ctx.with_user(user=user_schema)

    return user


@router.delete(
    "/{user_id}",
    dependencies=auth_dependencies,
)
async def delete_user(
    user_id: UserIdPathParam,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
) -> DeleteUser:
    """
    Delete a user by ID.

    Raises:
        HTTPException: If the user with the given ID is not found.
    """
    user = user_crud.get_user(session, user_id)

    if not user:
        raise HTTPException(
            status_code=404, detail=f"User with ID: {user_id} not found."
        )

    user_schema = UserSchema.model_validate(user)
    ctx.with_user(user=user_schema)
    user_crud.delete_user(session, user_id)

    return DeleteUser()
