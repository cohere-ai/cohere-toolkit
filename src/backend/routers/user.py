from fastapi import APIRouter, HTTPException, Request

from backend.config.routers import RouterName
from backend.crud import user as user_crud
from backend.database_models import User as UserModel
from backend.database_models.database import DBSessionDep
from backend.routers.utils import (
    add_agent_to_request_state,
    add_event_type_to_request_state,
    add_session_user_to_request_state,
    add_user_to_request_state,
)
from backend.schemas.metrics import MetricsMessageType
from backend.schemas.user import CreateUser, DeleteUser, UpdateUser
from backend.schemas.user import User
from backend.schemas.user import User as UserSchema

router = APIRouter(prefix="/v1/users")
router.name = RouterName.USER


@router.post("", response_model=User)
async def create_user(
    user: CreateUser, session: DBSessionDep, request: Request
) -> User:
    """
    Create a new user.

    Args:
        user (CreateUser): User data to be created.
        session (DBSessionDep): Database session.

    Returns:
        User: Created user.
    """
    db_user = UserModel(**user.model_dump(exclude_none=True))
    db_user = user_crud.create_user(session, db_user)
    add_user_to_request_state(request, db_user)
    add_event_type_to_request_state(request, MetricsMessageType.USER_CREATED)
    return db_user


@router.get("", response_model=list[User])
async def list_users(
    *, offset: int = 0, limit: int = 100, session: DBSessionDep
) -> list[User]:
    """
    List all users.

    Args:
        offset (int): Offset to start the list.
        limit (int): Limit of users to be listed.
        session (DBSessionDep): Database session.

    Returns:
        list[User]: List of users.
    """
    return user_crud.get_users(session, offset=offset, limit=limit)


@router.get("/{user_id}", response_model=User)
async def get_user(user_id: str, session: DBSessionDep, request: Request) -> User:
    """
    Get a user by ID.

    Args:
        user_id (str): User ID.
        session (DBSessionDep): Database session.

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

    add_session_user_to_request_state(request, session)
    return user


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: str, new_user: UpdateUser, session: DBSessionDep, request: Request
) -> User:
    """
    Update a user by ID.

    Args:
        user_id (str): User ID.
        new_user (UpdateUser): New user data.
        session (DBSessionDep): Database session.

    Returns:
        User: Updated user.

    Raises:
        HTTPException: If the user with the given ID is not found.
    """
    user = user_crud.get_user(session, user_id)
    add_event_type_to_request_state(request, MetricsMessageType.USER_UPDATED)

    if not user:
        raise HTTPException(
            status_code=404, detail=f"User with ID: {user_id} not found."
        )

    user = user_crud.update_user(session, user, new_user)
    add_session_user_to_request_state(request, session)
    return user


@router.delete("/{user_id}")
async def delete_user(
    user_id: str, session: DBSessionDep, request: Request
) -> DeleteUser:
    """ "
    Delete a user by ID.

    Args:
        user_id (str): User ID.
        session (DBSessionDep): Database session.

    Returns:
        DeleteUser: Empty response.

    Raises:
        HTTPException: If the user with the given ID is not found.
    """
    user = user_crud.get_user(session, user_id)

    if not user:
        raise HTTPException(
            status_code=404, detail=f"User with ID: {user_id} not found."
        )

    add_event_type_to_request_state(request, MetricsMessageType.USER_DELETED)
    add_session_user_to_request_state(request, session)
    user_crud.delete_user(session, user_id)

    return DeleteUser()
