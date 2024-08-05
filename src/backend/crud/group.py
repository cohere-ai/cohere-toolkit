from sqlalchemy.orm import Session

from backend.database_models import User, UserGroupAssociation
from backend.database_models.group import Group
from backend.schemas.scim import GroupMember


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


def get_group(db: Session, group_id: str) -> Group:
    """
    Get a user by ID.

    Args:
        db (Session): Database session.
        user_id (str): User ID.

    Returns:
        User: User with the given ID.
    """
    return db.query(Group).filter(Group.id == group_id).first()


def get_groups(db: Session, offset: int = 0, limit: int = 100) -> list[Group]:
    """
    List all groups

    Args:
        db (Session): Database session.
        offset (int): Offset to start the list.
        limit (int): Limit of users to be listed.

    Returns:
        list[Group]: List of groups.
    """
    return db.query(Group).offset(offset).limit(limit).all()


def create_group(db: Session, group: Group) -> Group:
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


def delete_group(db: Session, group_id: str) -> None:
    """
    Delete a user by ID.

    Args:
        db (Session): Database session.
        user_id (str): User ID.
    """
    group = db.query(Group).filter(Group.id == group_id)
    group.delete()
    db.commit()


def add_users(db: Session, group: Group, members: list[UserGroupAssociation]) -> Group:
    """
    Add users to a group.

    Args:
        db (Session): Database session.
        group (Group): Group to add the users.
        members (list[GroupMember]): Users to be added to the group.

    Returns:
        Group: Updated group.
    """
    group.user_associations.extend(members)
    db.commit()
    db.refresh(group)
    return group


def set_users(db: Session, group: Group, members: list[UserGroupAssociation]) -> Group:
    """
    Set the users of a group.

    Args:
        db (Session): Database session.
        group (Group): Group to add the users.
        users (list[User]): Users to be assigned to the group.

    Returns:
        Group: Updated group.
    """
    group.users = []
    db.flush()

    group.user_associations = members
    db.commit()
    db.refresh(group)
    return group


def update_group(db: Session, group: Group) -> Group:
    """
    Update a group.

    Args:
        db (Session): Database session.
        group (Group): Group to be updated.

    Returns:
        Group: Updated group.
    """
    db.commit()
    db.refresh(group)
    return group
