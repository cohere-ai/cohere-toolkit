from sqlalchemy.orm import Session

from backend.database_models.tool_call import ToolCall, UpdateToolCall


def create_tool_call(db: Session, tool_call: ToolCall) -> ToolCall:
    """
    Create a new tool call.

    Args:
        db (Session): Database session.
        tool_call (ToolCall): Tool call data to be created.

    Returns:
        ToolCall: Created tool call.
    """
    db.add(tool_call)
    db.commit()
    db.refresh(tool_call)
    return tool_call


def get_tool_call_by_id(db: Session, tool_call_id: str) -> ToolCall:
    """
    Get a tool call by its ID.

    Args:
        db (Session): Database session.
        tool_call_id (str): Tool call ID.

    Returns:
        ToolCall: Tool call with the given ID.
    """
    return db.query(ToolCall).filter(ToolCall.id == tool_call_id).first()


def list_tool_calls_by_message_id(db: Session, message_id: str) -> list[ToolCall]:
    """
    List all tool calls by message ID.

    Args:
        db (Session): Database session.
        message_id (str): Message ID.

    Returns:
        list[ToolCall]: List of tool calls.
    """
    return db.query(ToolCall).filter(ToolCall.message_id == message_id).all()


def delete_tool_calls_by_message_id(db: Session, message_id: str):
    """
    Delete all tool calls by message ID.

    Args:
        db (Session): Database session.
        message_id (str): Message ID.
    """
    db.query(ToolCall).filter(ToolCall.message_id == message_id).delete()
    db.commit()


def update_tool_call(
    db: Session, tool_call: ToolCall, new_tool_call: UpdateToolCall
) -> ToolCall:
    """
    Update a tool call.

    Args:
        db (Session): Database session.
        tool_call (ToolCall): Tool call data to be updated.

    Returns:
        ToolCall: Updated tool call.
    """

    for field, value in new_tool_call.dict().items():
        if value is not None:
            setattr(tool_call, field, value)
    db.commit()
    db.refresh(tool_call)
    return tool_call
