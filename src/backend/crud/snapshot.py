from sqlalchemy.orm import Session

from backend.database_models.snapshot import Snapshot, SnapshotAccess, SnapshotLink
from backend.schemas.snapshot import Snapshot as SnapshotSchema
from backend.schemas.snapshot import SnapshotAccess as SnapshotAccessSchema
from backend.schemas.snapshot import SnapshotLink as SnapshotLinkSchema


# Snapshot
def create_snapshot(db: Session, snapshot: SnapshotSchema) -> Snapshot:
    """
    Create a new snapshot.

    Args:
        db (Session): Database session.
        snapshot (SnapshotSchema): Snapshot data to be created.

    Returns:
        Snapshot: Created snapshot.
    """
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    return snapshot


def get_snapshot(db: Session, snapshot_id: str) -> SnapshotSchema | None:
    """
    Get a snapshot by ID.

    Args:
        db (Session): Database session.
        snapshot_id (str): Snapshot ID.

    Returns:
        SnapshotSchema: Snapshot with the given snapshot ID.
    """
    return db.query(Snapshot).filter(Snapshot.id == snapshot_id).first()


def get_snapshot_by_last_message_id(
    db: Session, last_message_id: str
) -> SnapshotSchema | None:
    """
    Get a snapshot by last message ID.

    Args:
        db (Session): Database session.
        last_message_id (str): Last message ID.

    Returns:
        SnapshotSchema: Snapshot with the given last message ID.
    """
    return (
        db.query(Snapshot).filter(Snapshot.last_message_id == last_message_id).first()
    )


def list_snapshots(db: Session, user_id: str) -> list[SnapshotSchema]:
    """
    List all snapshots.

    Args:
        db (Session): Database session.
        user_id (str): User ID.

    Returns:
        list[SnapshotSchema]: List of all snapshots.
    """
    return db.query(Snapshot).filter(Snapshot.user_id == user_id).all()


def delete_snapshot(db: Session, snapshot_id: str, user_id: str) -> None:
    """
    Delete a snapshot by ID.

    Args:
        db (Session): Database session.
        snapshot_id (str): Snapshot ID.
        user_id (str): User ID.
    """
    db.query(Snapshot).filter(
        Snapshot.id == snapshot_id, Snapshot.user_id == user_id
    ).delete()
    db.commit()


# SnapshotLink
def create_snapshot_link(
    db: Session, snapshot_link: SnapshotLinkSchema
) -> SnapshotLink:
    """
    Create a new snapshot link.

    Args:
        db (Session): Database session.
        snapshot_link (SnapshotLinkSchema): Snapshot link data to be created.

    Returns:
        SnapshotLink: Created snapshot link.
    """
    db.add(snapshot_link)
    db.commit()
    db.refresh(snapshot_link)
    return snapshot_link


def get_snapshot_link(db: Session, snapshot_link_id: str) -> SnapshotLinkSchema | None:
    """
    Get a snapshot link by ID.

    Args:
        db (Session): Database session.
        snapshot_link_id (str): Snapshot link ID.

    Returns:
        SnapshotLinkSchema: Snapshot link with the given snapshot link ID.
    """
    return db.query(SnapshotLink).filter(SnapshotLink.id == snapshot_link_id).first()


def list_snapshot_links(db: Session, snapshot_id: str) -> list[SnapshotLinkSchema]:
    """
    List all snapshot links.

    Args:
        db (Session): Database session.
        snapshot_id (str): Snapshot ID.

    Returns:
        list[SnapshotLinkSchema]: List of all snapshot links.
    """
    return db.query(SnapshotLink).filter(SnapshotLink.snapshot_id == snapshot_id).all()


def delete_snapshot_link(db: Session, snapshot_link_id: str, user_id: str) -> None:
    """
    Delete a snapshot link by ID.

    Args:
        db (Session): Database session.
        snapshot_link_id (str): Snapshot link ID.
        user_id (str): User ID.
    """
    db.query(SnapshotLink).filter(
        SnapshotLink.id == snapshot_link_id, SnapshotLink.user_id == user_id
    ).delete()
    db.commit()


# SnapshotAccess
def create_snapshot_access(
    db: Session, snapshot_access: SnapshotAccessSchema
) -> SnapshotAccess:
    """
    Create a new snapshot access.

    Args:
        db (Session): Database session.
        snapshot_access (SnapshotAccessSchema): Snapshot access data to be created.

    Returns:
        SnapshotAccess: Created snapshot access.
    """
    db.add(snapshot_access)
    db.commit()
    db.refresh(snapshot_access)
    return snapshot_access


def get_snapshot_access(
    db: Session, snapshot_access_id: str
) -> SnapshotAccessSchema | None:
    """
    Get a snapshot access by ID.

    Args:
        db (Session): Database session.
        snapshot_access_id (str): Snapshot access ID.

    Returns:
        SnapshotAccessSchema: Snapshot access with the given snapshot access ID.
    """
    return (
        db.query(SnapshotAccess).filter(SnapshotAccess.id == snapshot_access_id).first()
    )
