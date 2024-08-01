from fastapi import APIRouter, Depends, HTTPException, Request

from backend.config.routers import RouterName
from backend.crud import user as user_crud
from backend.database_models import User as UserModel
from backend.database_models.database import DBSessionDep
from backend.schemas.context import Context
from backend.schemas.metrics import MetricsMessageType
from backend.schemas.user import CreateUser, DeleteUser, UpdateUser
from backend.schemas.user import User
from backend.schemas.user import User as UserSchema
from backend.services.context import get_context

router = APIRouter(prefix="/v1/users")
router.name = RouterName.USER


@router.post("", response_model=User)
async def create_user(
    user: CreateUser,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
) -> User:
    """
    Create a new user.

    Args:
        user (CreateUser): User data to be created.
        session (DBSessionDep): Database session.
        ctx (Context): Context object.

    Returns:
        User: Created user.
    """
    ctx.with_event_type(MetricsMessageType.USER_CREATED)

    db_user = UserModel(**user.model_dump(exclude_none=True))
    db_user = user_crud.create_user(session, db_user)

    user_schema = UserSchema.model_validate(db_user)
    ctx.with_user(user=user_schema)

    return db_user


@router.get("", response_model=list[User])
async def list_users(
    *,
    offset: int = 0,
    limit: int = 100,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
) -> list[User]:
    """
    List all users.

    Args:
        offset (int): Offset to start the list.
        limit (int): Limit of users to be listed.
        session (DBSessionDep): Database session.
        ctx (Context): Context object.

    Returns:
        list[User]: List of users.
    """
    return user_crud.get_users(session, offset=offset, limit=limit)


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: str,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
) -> User:
    """
    Get a user by ID.

    Args:
        user_id (str): User ID.
        session (DBSessionDep): Database session.
        ctx (Context): Context object.

    Returns:
        User: User with the given ID.

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


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: str,
    new_user: UpdateUser,
    session: DBSessionDep,
    request: Request,
    ctx: Context = Depends(get_context),
) -> User:
    """
    Update a user by ID.

    Args:
        user_id (str): User ID.
        new_user (UpdateUser): New user data.
        session (DBSessionDep): Database session.
        request (Request): Request object.
        ctx (Context): Context object

    Returns:
        User: Updated user.

    Raises:
        HTTPException: If the user with the given ID is not found.
    """
    user = user_crud.get_user(session, user_id)
    ctx.with_event_type(MetricsMessageType.USER_UPDATED)

    if not user:
        raise HTTPException(
            status_code=404, detail=f"User with ID: {user_id} not found."
        )

    user = user_crud.update_user(session, user, new_user)
    user_schema = UserSchema.model_validate(user)
    ctx.with_user(user=user_schema)

    return user


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
) -> DeleteUser:
    """ "
    Delete a user by ID.

    Args:
        user_id (str): User ID.
        session (DBSessionDep): Database session.
        ctx (Context): Context object.

    Returns:
        DeleteUser: Empty response.

    Raises:
        HTTPException: If the user with the given ID is not found.
    """
    ctx.with_event_type(MetricsMessageType.USER_DELETED)
    user = user_crud.get_user(session, user_id)

    if not user:
        raise HTTPException(
            status_code=404, detail=f"User with ID: {user_id} not found."
        )

    user_schema = UserSchema.model_validate(user)
    ctx.with_user(user=user_schema)
    user_crud.delete_user(session, user_id)

    return DeleteUser()
