from sqlalchemy.orm import Session

from backend.database_models.message import Message, MessageFileAssociation
from backend.schemas.message import UpdateMessage


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


def create_message_file_association(db: Session, message_file_association: MessageFileAssociation) -> MessageFileAssociation:
    db.add(message_file_association)
    db.commit()
    db.refresh(message_file_association)
    return message_file_association    


def get_message_file_association_by_file_id(db: Session, file_id: str, user_id: str) -> MessageFileAssociation:
    return (
        db.query(MessageFileAssociation)
        .filter(MessageFileAssociation.file_id == file_id, Message.user_id == user_id)
        .first()
    )


def delete_message_file_association(db: Session, message_id: str, file_id: str, user_id: str) -> None:
    message_file_association = db.query(MessageFileAssociation).filter(
        MessageFileAssociation.message_id == message_id, MessageFileAssociation.user_id == user_id, MessageFileAssociation.file_id == file_id
    )
    message_file_association.delete()
    db.commit()
