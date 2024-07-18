from sqlalchemy.orm import Session

from backend.database_models.message import Message
from backend.schemas.message import UpdateMessage
from backend.services.transaction import validate_transaction


@validate_transaction
def create_message(db: Session, message: Message) -> Message:
    """
    Create a new message.

    Args:
        db (Session): Database session.
        message (Message): Message data to be created.

    Returns:
        Message: Created message.
    """
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


@validate_transaction
def get_message(db: Session, message_id: str, user_id: str) -> Message:
    """
    Get a message by ID.

    Args:
        db (Session): Database session.
        message_id (str): Message ID.
        user_id (str): User ID.

    Returns:
        Message: Message with the given ID.
    """
    return (
        db.query(Message)
        .filter(Message.id == message_id, Message.user_id == user_id)
        .first()
    )


@validate_transaction
def get_messages(
    db: Session, user_id: str, offset: int = 0, limit: int = 100
) -> list[Message]:
    """
    List all messages.

    Args:
        db (Session): Database session.
        offset (int): Offset to start the list.
        limit (int): Limit of messages to be listed.
        user_id (str): User ID.

    Returns:
        list[Message]: List of messages.
    """
    return (
        db.query(Message)
        .filter(Message.user_id == user_id)
        .offset(offset)
        .limit(limit)
        .all()
    )


@validate_transaction
def get_messages_by_conversation_id(
    db: Session, conversation_id: str, user_id: str
) -> list[Message]:
    """
    List all messages from a conversation.

    Args:
        db (Session): Database session.
        conversation_id (str): Conversation ID.
        user_id (str): User ID.

    Returns:
        list[Message]: List of messages from the conversation.
    """
    return (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id, Message.user_id == user_id)
        .all()
    )


@validate_transaction
def update_message(
    db: Session, message: Message, new_message: UpdateMessage
) -> Message:
    """
    Update a message by ID.

    Args:
        db (Session): Database session.
        message (Message): Message to be updated.
        new_message (Message): New message data.

    Returns:
        Message: Updated message.
    """
    for attr, value in new_message.model_dump().items():
        setattr(message, attr, value)
    db.commit()
    db.refresh(message)
    return message


@validate_transaction
def delete_message(db: Session, message_id: str, user_id: str) -> None:
    """
    Delete a message by ID.

    Args:
        db (Session): Database session.
        message_id (str): Message ID.
        user_id (str): User ID.
    """
    message = db.query(Message).filter(
        Message.id == message_id, Message.user_id == user_id
    )
    message.delete()
    db.commit()
