from sqlalchemy.orm import Session

from backend.database_models.user import User
from backend.schemas.user import UpdateUser
from backend.services.transaction import validate_transaction


@validate_transaction
def create_user(db: Session, user: User) -> User:
    """ "
    Create a new user.

    Args:
        db (Session): Database session.
        user (User): User data to be created.

    Returns:
        User: Created user.
    """
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@validate_transaction
def get_user(db: Session, user_id: str) -> User:
    """
    Get a user by ID.

    Args:
        db (Session): Database session.
        user_id (str): User ID.

    Returns:
        User: User with the given ID.
    """
    return db.query(User).filter(User.id == user_id).first()


@validate_transaction
def get_users(db: Session, offset: int = 0, limit: int = 100) -> list[User]:
    """
    List all users.

    Args:
        db (Session): Database session.
        offset (int): Offset to start the list.
        limit (int): Limit of users to be listed.

    Returns:
        list[User]: List of users.
    """
    return db.query(User).order_by(User.fullname).offset(offset).limit(limit).all()


@validate_transaction
def get_user_by_email(db: Session, email: str) -> User:
    """
    Get a user by email.

    Args:
        db (Session): Database session.
        email (str): User email.

    Returns:
        User: User with the given email.
    """
    return db.query(User).filter(User.email == email).first()


@validate_transaction
def update_user(db: Session, user: User, new_user: UpdateUser) -> User:
    """
    Update a user by ID.

    Args:
        db (Session): Database session.
        user (User): User to be updated.
        new_user (User): New user data.

    Returns:
        User: Updated user.
    """
    for attr, value in new_user.model_dump(exclude_none=True).items():
        setattr(user, attr, value)
    db.commit()
    db.refresh(user)
    return user


@validate_transaction
def delete_user(db: Session, user_id: str) -> None:
    """
    Delete a user by ID.

    Args:
        db (Session): Database session.
        user_id (str): User ID.
    """
    user = db.query(User).filter(User.id == user_id)
    user.delete()
    db.commit()
