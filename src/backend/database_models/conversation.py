from typing import List, Optional
from uuid import uuid4

from sqlalchemy import ForeignKey, Index, PrimaryKeyConstraint, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database_models.base import Base
from backend.database_models.message import Message


class ConversationFileAssociation(Base):
    __tablename__ = "conversation_files"

    conversation_id: Mapped[str] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE")
    )
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    file_id: Mapped[str] = mapped_column(String, default=None, nullable=False)
    conversation: Mapped["Conversation"] = relationship(
        "Conversation", back_populates="conversation_file_associations"
    )

    __table_args__ = (
        UniqueConstraint("conversation_id", "file_id", name="unique_conversation_file"),
    )


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String, default=lambda: str(uuid4()), unique=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String, default="New Conversation")
    description: Mapped[str] = mapped_column(String, nullable=True, default=None)
    text_messages: Mapped[List["Message"]] = relationship()
    conversation_file_associations: Mapped[List["ConversationFileAssociation"]] = (
        relationship("ConversationFileAssociation", back_populates="conversation")
    )
    agent_id: Mapped[str] = mapped_column(
        ForeignKey("agents.id", ondelete="CASCADE"), nullable=True
    )
    organization_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey(
            "organizations.id",
            name="conversations_organization_id_fkey",
            ondelete="CASCADE",
        )
    )

    @property
    def messages(self):
        return sorted(self.text_messages, key=lambda x: x.created_at)

    @property
    def file_ids(self):
        return [
            conversation_file_association.file_id
            for conversation_file_association in self.conversation_file_associations
        ]

    __table_args__ = (
        UniqueConstraint("id", "user_id", name="conversation_id_user_id"),
        PrimaryKeyConstraint("id", "user_id", name="conversation_pkey"),
        Index("conversation_user_agent_index", "user_id", "agent_id"),
        Index("conversation_user_id_index", "id", "user_id", unique=True),
    )
