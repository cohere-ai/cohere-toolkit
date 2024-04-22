from sqlalchemy.orm import Session

from backend.models.conversation import Conversation
from backend.schemas.conversation import UpdateConversation


def create_conversation(db: Session, conversation: Conversation) -> Conversation:
    """
    Create a new conversation.

    Args:
        db (Session): Database session.
        conversation (Conversation): Conversation data to be created.

    Returns:
        Conversation: Created conversation.
    """
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def get_conversation(
    db: Session, conversation_id: str, user_id: str
) -> Conversation | None:
    """
    Get a conversation by ID.

    Args:
        db (Session): Database session.
        conversation_id (str): Conversation ID.
        user_id (str): User ID.

    Returns:
        Conversation: Conversation with the given conversation ID and user ID.
    """
    return (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id, Conversation.user_id == user_id)
        .first()
    )


def get_conversations(
    db: Session, user_id: str, offset: int = 0, limit: int = 100
) -> list[Conversation]:
    """
    List all conversations.

    Args:
        db (Session): Database session.
        user_id (str): User ID.
        offset (int): Offset to start the list.
        limit (int): Limit of conversations to be listed.

    Returns:
        list[Conversation]: List of conversations.
    """
    return (
        db.query(Conversation)
        .filter(Conversation.user_id == user_id)
        .offset(offset)
        .limit(limit)
        .all()
    )


def update_conversation(
    db: Session, conversation: Conversation, new_conversation: UpdateConversation
) -> Conversation:
    """
    Update a conversation by ID.

    Args:
        db (Session): Database session.
        conversation (Conversation): Conversation to be updated.
        new_conversation (Conversation): New conversation data.

    Returns:
        Conversation: Updated conversation.
    """
    for attr, value in new_conversation.model_dump().items():
        if value is not None:
            setattr(conversation, attr, value)

    db.commit()
    db.refresh(conversation)
    return conversation


def delete_conversation(db: Session, conversation_id: str, user_id: str) -> None:
    """
    Delete a conversation by ID.

    Args:
        db (Session): Database session.
        conversation_id (str): Conversation ID.
        user_id (str): User ID.
    """
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id, Conversation.user_id == user_id
    )
    conversation.delete()
    db.commit()
