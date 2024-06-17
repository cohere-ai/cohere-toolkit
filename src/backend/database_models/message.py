from enum import StrEnum
from typing import List

from sqlalchemy import Boolean, Enum, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database_models.base import Base
from backend.database_models.citation import Citation
from backend.database_models.document import Document
from backend.database_models.file import File


class MessageAgent(StrEnum):
    USER = "USER"
    CHATBOT = "CHATBOT"


class Message(Base):
    """
    Default Message model for conversation text.
    """

    __tablename__ = "messages"

    text: Mapped[str]

    # TODO: Swap to foreign key once User management implemented
    user_id: Mapped[str] = mapped_column(String)
    conversation_id: Mapped[str] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE")
    )
    position: Mapped[int]
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    generation_id: Mapped[str] = mapped_column(String, nullable=True)

    documents: Mapped[List["Document"]] = relationship()
    citations: Mapped[List["Citation"]] = relationship()
    files: Mapped[List["File"]] = relationship()

    agent: Mapped[MessageAgent] = mapped_column(
        Enum(MessageAgent, native_enum=False),
    )

    __table_args__ = (
        Index("message_conversation_id_user_id", conversation_id, user_id),
        Index("message_conversation_id", conversation_id),
        Index("message_is_active", is_active),
        Index("message_user_id", user_id),
    )
