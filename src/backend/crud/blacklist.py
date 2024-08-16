from sqlalchemy.orm import Session

from backend.database_models.blacklist import Blacklist
from backend.services.transaction import validate_transaction


@validate_transaction
def create_blacklist(db: Session, blacklist: Blacklist) -> Blacklist:
    """ "
    Create a blacklist token.

    Args:
        db (Session): Database session.
        blacklist (Blacklist): Blacklist data to be created.

    Returns:
        Blacklist: Created blacklist.
    """
    db.add(blacklist)
    db.commit()
    db.refresh(blacklist)
    return blacklist


@validate_transaction
def get_blacklist(db: Session, token_id: str) -> Blacklist:
    """
    Get a blacklist token by token_id column.

    Args:
        db (Session): Database session.
        token_id (str): Token ID.

    Returns:
        Blacklist: Blacklist with the given token_id.
    """
    return db.query(Blacklist).filter(Blacklist.token_id == token_id).first()
