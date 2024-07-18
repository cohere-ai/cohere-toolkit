from sqlalchemy.orm import Session

from backend.database_models.tool_auth import ToolAuth
from backend.schemas.tool_auth import UpdateToolAuth


def create_tool_auth(db: Session, tool_auth: ToolAuth) -> ToolAuth:
    """
    Create a new tool auth.

    Tool Auth stores the access tokens for tool's that need auth

    Args:
      db (Session): Database session.
      tool_auth (ToolAuth): ToolAuth to be created.

    Returns:
      ToolAuth: Created tool auth.
    """
    db.add(tool_auth)
    db.commit()
    db.refresh(tool_auth)
    return tool_auth


def get_tool_auth(db: Session, tool_id: str, user_id: str) -> ToolAuth:
    """
    Get an tool auth by user ID and tool ID.

    Args:
      db (Session): Database session.
      user_id (str): User ID.
      tool_id (str): Tool ID.

    Returns:
      ToolAuth: ToolAuth with the given ID.
    """
    return (
        db.query(ToolAuth)
        .filter(ToolAuth.tool_id == tool_id, ToolAuth.user_id == user_id)
        .first()
    )


def update_tool_auth(
    db: Session, tool_auth: ToolAuth, new_tool_auth: UpdateToolAuth
) -> ToolAuth:
    """
    Update a tool auth by user ID and tool ID.

    Args:
        db (Session): Database session.
        tool_auth (ToolAuth): Tool auth to be updated.
        new_tool_auth (ToolAuth): New tool auth data.

    Returns:
        ToolAuth: Updated tool auth.
    """
    for attr, value in new_tool_auth.model_dump().items():
        setattr(tool_auth, attr, value)
    db.commit()
    db.refresh(tool_auth)
    return tool_auth


def delete_tool_auth(db: Session, user_id: str, tool_id: str) -> None:
    """
    Delete a tool auth by user ID and tool ID.

    Args:
        db (Session): Database session.
        user_id (str): User ID.
        tool_id (str): Tool ID.
    """
    tool_auth = db.query(ToolAuth).filter(
        ToolAuth.tool_id == tool_id, ToolAuth.user_id == user_id
    )
    tool_auth.delete()
    db.commit()
