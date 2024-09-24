from sqlalchemy import desc
from sqlalchemy.orm import Session

from backend.database_models.conversation import (
    Conversation,
    ConversationFileAssociation,
)
from backend.schemas.conversation import (
    ToggleConversationPinRequest,
    UpdateConversationRequest,
)
from backend.services.transaction import validate_transaction


@validate_transaction
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


@validate_transaction
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


@validate_transaction
def get_conversations(
    db: Session,
    user_id: str,
    offset: int = 0,
    limit: int = 100,
    order_by: str | None = None,
    agent_id: str | None = None,
    organization_id: str | None = None,
) -> list[Conversation]:
    """
    List all conversations.

    Args:
        db (Session): Database session.
        user_id (str): User ID.
        organization_id (str): Organization ID.
        agent_id (str): Agent ID.
        offset (int): Offset to start the list.
        limit (int): Limit of conversations to be listed.
        order_by (str): A field by which to order the conversations.

    Returns:
        list[Conversation]: List of conversations.
    """
    query = db.query(Conversation).filter(Conversation.user_id == user_id)
    if agent_id is not None:
        query = query.filter(Conversation.agent_id == agent_id)
    if organization_id is not None:
        query = query.filter(Conversation.organization_id == organization_id)
    if order_by is not None:
        order_column = getattr(Conversation, order_by)
        query = query.order_by(desc(order_column))
    query = query.order_by(Conversation.updated_at.desc()).offset(offset).limit(limit)

    return query.all()


@validate_transaction
def update_conversation(
    db: Session, conversation: Conversation, new_conversation: UpdateConversationRequest
) -> Conversation:
    """
    Update a conversation by ID.

    Args:
        db (Session): Database session.
        conversation (Conversation): Conversation to be updated.
        new_conversation (UpdateConversationRequest): New conversation data.

    Returns:
        Conversation: Updated conversation.
    """
    for attr, value in new_conversation.model_dump().items():
        if value is not None:
            setattr(conversation, attr, value)
    db.commit()
    db.refresh(conversation)
    return conversation


@validate_transaction
def toggle_conversation_pin(
    db: Session, conversation: Conversation, new_conversation_pin: ToggleConversationPinRequest
) -> Conversation:
    """
    Update conversation pin by conversation ID.

    Args:
        db (Session): Database session.
        conversation (Conversation): Conversation to be updated.
        new_conversation_pin (ToggleConversationPinRequest): New conversation pin data.

    Returns:
        Conversation: Updated conversation.
    """
    db.query(Conversation).filter(Conversation.id == conversation.id).update({
        Conversation.is_pinned: new_conversation_pin.is_pinned,
        Conversation.updated_at: conversation.updated_at
    })
    db.commit()
    db.refresh(conversation)
    return conversation


@validate_transaction
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


def create_conversation_file_association(
    db: Session, conversation_file_association: ConversationFileAssociation
) -> ConversationFileAssociation:
    """
    Create a new conversation file association.

    Args:
        db (Session): Database session.
        conversation_file_association (ConversationFileAssociation): Conversation file association data to be created.

    Returns:
        ConversationFileAssociation: Created conversation file association.
    """
    db.add(conversation_file_association)
    db.commit()
    db.refresh(conversation_file_association)
    return conversation_file_association


def delete_conversation_file_association(
    db: Session, conversation_id: str, file_id: str, user_id: str
) -> None:
    """
    Delete a conversation file association by ID.

    Args:
        db (Session): Database session.
        conversation_id (str): Conversation ID.
        file_id (str): File ID.
        user_id (str): User ID.
    """
    conversation_file_association = db.query(ConversationFileAssociation).filter(
        ConversationFileAssociation.conversation_id == conversation_id,
        ConversationFileAssociation.user_id == user_id,
        ConversationFileAssociation.file_id == file_id,
    )
    conversation_file_association.delete()
    db.commit()
