from sqlalchemy.orm import Session

from backend.database_models.document import Document
from backend.services.transaction import validate_transaction


@validate_transaction
def create_document(db: Session, document: Document) -> Document:
    """
    Create a new document.

    Args:
        db (Session): Database session.
        document (Document): Document data to be created.

    Returns:
        Document: Created document.
    """
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


@validate_transaction
def get_document(db: Session, document_id: str) -> Document:
    """
    Get a document by ID.

    Args:
        db (Session): Database session.
        document_id (str): Document ID.

    Returns:
        Document: Document with the given ID.
    """
    return db.query(Document).filter(Document.id == document_id).first()


@validate_transaction
def get_documents(db: Session, offset: int = 0, limit: int = 100) -> list[Document]:
    """
    List all documents.

    Args:
        db (Session): Database session.
        offset (int): Offset to start the list.
        limit (int): Limit of documents to be listed.

    Returns:
        list[Document]: List of documents.
    """
    return db.query(Document).offset(offset).limit(limit).all()


def delete_document(db: Session, document_id: str) -> None:
    """
    Delete a document by ID.

    Args:
        db (Session): Database session.
        document_id (str): Document ID.
    """
    document = db.query(Document).filter(Document.id == document_id)
    document.delete()
    db.commit()
