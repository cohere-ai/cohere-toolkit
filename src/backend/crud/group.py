from sqlalchemy.orm import Session

from backend.database_models import UserGroupAssociation
from backend.database_models.group import Group


def get_group_by_name(db: Session, name: str) -> Group | None:
    """
    Get a group by name.

    Args:
        db (Session): Database session.
        name (str): Group name.

    Returns:
        Group | None: Group with the given name or None if not found.
    """
    return db.query(Group).filter(Group.display_name == name).first()


def get_group(db: Session, group_id: str) -> Group | None:
    """
    Get a group by ID.

    Args:
        db (Session): Database session.
        group_id (str): Group ID.

    Returns:
        Group | None: Group with the given name or None if not found.
    """
    return db.query(Group).filter(Group.id == group_id).first()


def get_groups(db: Session, offset: int = 0, limit: int = 100) -> list[Group]:
    """
    Get a list of groups.

    Args:
        db (Session): Database session.
        offset (int): Offset.
        limit (int): Limit.

    Returns:
        list[Group]: List of groups.
    """
    return db.query(Group).offset(offset).limit(limit).all()


def create_group(db: Session, group: Group) -> Group:
    """
    Create a group.

    Args:
        db (Session): Database session.
        group (Group): Group to be created.

    Returns:
        Group: Created group.
    """
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


def delete_group(db: Session, group_id: str) -> None:
    """
    Delete a group by ID.

    Args:
        db (Session): Database session.
        group_id (str): Group ID.
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
    Set the users of a group. Overwrites existing users.

    Args:
        db (Session): Database session.
        group (Group): Group to add the users.
        members (list[GroupMember]): Users to be added to the group.

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
