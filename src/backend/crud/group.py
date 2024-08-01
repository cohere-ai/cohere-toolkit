from sqlalchemy.orm import Session
from backend.database_models.group import Group


def get_group_by_name(db: Session, name: str) -> Group | None:
    """
    Get a user by ID.

    Args:
        db (Session): Database session.
        user_name (str): username.

    Returns:
        User: User with the given username.
    """
    return db.query(Group).filter(Group.display_name == name).first()

def  create_group(db: Session, group: Group) -> Group:
    """ "
    Create a new user.

    Args:
        db (Session): Database session.
        user (User): User data to be created.

    Returns:
        User: Created user.
    """
    db.add(group)
    db.commit()
    db.refresh(group)
    return group