from enum import StrEnum
from typing import List

from sqlalchemy import Boolean, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base
from backend.models.citation import Citation
from backend.models.document import Document
from backend.models.file import File


class MessageAgent(StrEnum):
    USER = "USER"
    CHATBOT = "CHATBOT"


class MessageType(StrEnum):
    TEXT = "TEXT"


class MessageBase(Base):
    """
    Abstract base class that Message models should inherit from.
    """

    __abstract__ = True

    user_id: Mapped[str]
    conversation_id: Mapped[str] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE")
    )
    type: Mapped[MessageType] = mapped_column(
        Enum(MessageType, native_enum=False), default=MessageType.TEXT
    )
    position: Mapped[int]
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Message(MessageBase):
    """
    Default Message model for conversation text.
    """

    __tablename__ = "messages"

    text: Mapped[str]

    generation_id: Mapped[str] = mapped_column(String, nullable=True)

    documents: Mapped[List["Document"]] = relationship()
    citations: Mapped[List["Citation"]] = relationship()
    files: Mapped[List["File"]] = relationship()

    agent: Mapped[MessageAgent] = mapped_column(
        Enum(MessageAgent, native_enum=False),
    )
