from enum import StrEnum
from typing import List

from sqlalchemy import (
    Boolean,
    Enum,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database_models.base import Base
from backend.database_models.citation import Citation
from backend.database_models.document import Document
from backend.database_models.tool_call import ToolCall


class MessageAgent(StrEnum):
    USER = "USER"
    CHATBOT = "CHATBOT"


class MessageFileAssociation(Base):
    __tablename__ = "message_files"

    message_id: Mapped[str] = mapped_column(
        ForeignKey("messages.id", ondelete="CASCADE")
    )
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    file_id: Mapped[str] = mapped_column(String, default=None, nullable=False)
    message: Mapped["Message"] = relationship(
        "Message", back_populates="message_file_associations"
    )

    __table_args__ = (
        UniqueConstraint("message_id", "file_id", name="unique_message_file"),
        Index("message_file_file_id", file_id),
    )


class Message(Base):
    """
    Default Message model for conversation text.
    """

    __tablename__ = "messages"

    text: Mapped[str]

    user_id: Mapped[str] = mapped_column(String, nullable=True)
    conversation_id: Mapped[str] = mapped_column(String, nullable=True)
    position: Mapped[int]
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    generation_id: Mapped[str] = mapped_column(String, nullable=True)
    tool_plan: Mapped[str] = mapped_column(String, nullable=True)

    documents: Mapped[List[Document]] = relationship()
    citations: Mapped[List[Citation]] = relationship()
    message_file_associations: Mapped[List["MessageFileAssociation"]] = relationship(
        "MessageFileAssociation", back_populates="message"
    )
    tool_calls: Mapped[List[ToolCall]] = relationship()

    agent: Mapped[MessageAgent] = mapped_column(
        Enum(MessageAgent, native_enum=False),
    )

    @property
    def file_ids(self):
        return [
            message_file_association.file_id
            for message_file_association in self.message_file_associations
        ]

    __table_args__ = (
        ForeignKeyConstraint(
            ["conversation_id", "user_id"],
            ["conversations.id", "conversations.user_id"],
            name="message_conversation_id_user_id_fkey",
            ondelete="CASCADE",
        ),
        Index("message_conversation_id_user_id", conversation_id, user_id),
        Index("message_conversation_id", conversation_id),
        Index("message_is_active", is_active),
        Index("message_user_id", user_id),
    )
