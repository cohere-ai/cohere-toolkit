from fastapi import HTTPException

from backend.crud import user as user_crud
from backend.database_models.database import DBSessionDep
from backend.database_models.user import User


def validate_user_exists(session: DBSessionDep, user_id: str) -> User:
    """
    Validate if a user exists.

    Args:
        session (DBSessionDep): Database session.
        user_id (str): User ID.

    Returns:
        User: User with the given ID.

    Raises:
        HTTPException: If the user with the given ID is not found.
    """
    user = user_crud.get_user(session, user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User with ID {user_id} not found.",
        )

    return user
