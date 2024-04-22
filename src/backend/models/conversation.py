from typing import List

from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy import String

from backend.models.base import Base
from backend.models.message import Message
from backend.models.file import File


class Conversation(Base):
    __tablename__ = "conversations"

    user_id: Mapped[str]
    title: Mapped[str] = mapped_column(String, default="New Conversation")
    description: Mapped[str] = mapped_column(String, nullable=True, default=None)

    text_messages: Mapped[List["Message"]] = relationship()
    files: Mapped[List["File"]] = relationship()

    @property
    def messages(self):
        return sorted(self.text_messages, key=lambda x: x.position)
