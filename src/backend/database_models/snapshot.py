from typing import Optional

from sqlalchemy import JSON, ForeignKey, ForeignKeyConstraint, Index, String
from sqlalchemy.orm import Mapped, mapped_column, validates

from backend.database_models.base import Base


class Snapshot(Base):
    __tablename__ = "snapshots"

    user_id: Mapped[str] = mapped_column(String, nullable=True)
    organization_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey(
            "organizations.id",
            name="conversations_organization_id_fkey",
            ondelete="CASCADE",
        )
    )
    conversation_id: Mapped[str] = mapped_column(String)

    last_message_id: Mapped[str] = mapped_column(
        ForeignKey("messages.id", ondelete="CASCADE")
    )
    version: Mapped[int] = mapped_column()

    # snapshot is a json column
    snapshot: Mapped[str] = mapped_column(JSON)

    __table_args__ = (
        ForeignKeyConstraint(
            ["conversation_id", "user_id"],
            ["conversations.id", "conversations.user_id"],
            name="snapshot_conversation_id_user_id_fkey",
            ondelete="CASCADE",
        ),
        Index("snapshot_user_id", user_id),
        Index("snapshot_last_message_id", last_message_id),
        Index("snapshot_conversation_id", conversation_id),
    )


# TODO: Implement different access levels for snapshots
class SnapshotLink(Base):
    __tablename__ = "snapshot_links"

    snapshot_id: Mapped[str] = mapped_column(
        ForeignKey("snapshots.id", ondelete="CASCADE")
    )

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )

    __table_args__ = (Index("snapshot_link_snapshot_id", snapshot_id),)


class SnapshotAccess(Base):
    __tablename__ = "snapshot_access"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    snapshot_id: Mapped[str] = mapped_column(
        ForeignKey("snapshots.id", ondelete="CASCADE")
    )
    link_id: Mapped[str] = mapped_column(
        ForeignKey("snapshot_links.id", ondelete="CASCADE")
    )

    __table_args__ = (
        Index("snapshot_access_user_id", user_id),
        Index("snapshot_access_link_id", link_id),
    )
