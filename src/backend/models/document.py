from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.models.base import Base


class Document(Base):
    __tablename__ = "documents"

    text: Mapped[str]
    user_id: Mapped[str]
    title: Mapped[str] = mapped_column(String, nullable=True)
    url: Mapped[str] = mapped_column(String, nullable=True)

    conversation_id: Mapped[str] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE")
    )
    message_id: Mapped[str] = mapped_column(
        ForeignKey("messages.id", ondelete="CASCADE")
    )
    # User facing ID returned from model, not storage UUID ex: doc_0
    document_id: Mapped[str]
