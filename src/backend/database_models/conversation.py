from typing import List

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database_models.agent import Agent
from backend.database_models.base import Base
from backend.database_models.file import File
from backend.database_models.message import Message


class Conversation(Base):
    __tablename__ = "conversations"

    # TODO: Swap to foreign key once User management implemented
    user_id: Mapped[str] = mapped_column(String)
    title: Mapped[str] = mapped_column(String, default="New Conversation")
    description: Mapped[str] = mapped_column(String, nullable=True, default=None)

    text_messages: Mapped[List["Message"]] = relationship()
    files: Mapped[List["File"]] = relationship()
    agent_id: Mapped[str] = mapped_column(ForeignKey("agents.id", ondelete="CASCADE"), nullable=True)

    @property
    def messages(self):
        return sorted(self.text_messages, key=lambda x: x.position)

    __table_args__ = (
        Index("conversation_user_id", user_id),
        Index("conversation_agent_id", agent_id),
    )
