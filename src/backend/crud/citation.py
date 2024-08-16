from sqlalchemy.orm import Session

from backend.database_models.citation import Citation
from backend.services.transaction import validate_transaction


@validate_transaction
def create_citation(db: Session, citation: Citation) -> Citation:
    """
    Create a new citation.

    Args:
        db (Session): Database session.
        citation (Citation): Citation data to be created.

    Returns:
        Citation: Created citation.
    """
    db.add(citation)
    db.commit()
    db.refresh(citation)
    return citation


@validate_transaction
def get_citation(db: Session, citation_id: str) -> Citation:
    """
    Get a citation by ID.

    Args:
        db (Session): Database session.
        citation_id (str): Citation ID.

    Returns:
        Citation: Citation with the given ID.
    """
    return db.query(Citation).filter(Citation.id == citation_id).first()


@validate_transaction
def get_citations(db: Session, offset: int = 0, limit: int = 100) -> list[Citation]:
    """
    List all citations.

    Args:
        db (Session): Database session.
        offset (int): Offset to start the list.
        limit (int): Limit of citations to be listed.

    Returns:
        list[Citation]: List of citations.
    """
    return db.query(Citation).offset(offset).limit(limit).all()


@validate_transaction
def get_citations_by_message_id(db: Session, message_id: str) -> list[Citation]:
    """
    List all citations from a message.

    Args:
        db (Session): Database session.
        message_id (str): Conversation ID.

    Returns:
        list[Citation]: List of citations.
    """
    return db.query(Citation).filter(Citation.message_id == message_id).all()


@validate_transaction
def delete_citation(db: Session, citation_id: str) -> None:
    """
    Delete a citation by ID.

    Args:
        db (Session): Database session.
        citation_id (str): Citation ID.
    """
    citation = db.query(Citation).filter(Citation.id == citation_id)
    citation.delete()
    db.commit()
