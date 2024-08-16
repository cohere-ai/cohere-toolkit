from sqlalchemy.orm import Session

from backend.database_models.tool_call import ToolCall


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
