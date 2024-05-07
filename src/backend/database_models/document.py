from sqlalchemy import JSON, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.database_models.base import Base


class Document(Base):
    __tablename__ = "documents"

    text: Mapped[str]
    # TODO: Swap to foreign key once User management implemented
    user_id: Mapped[str] = mapped_column(String)
    title: Mapped[str] = mapped_column(String, nullable=True)
    url: Mapped[str] = mapped_column(String, nullable=True)
    fields: Mapped[dict] = mapped_column(JSON, nullable=True)
    tool_name: Mapped[str] = mapped_column(String, nullable=True)

    conversation_id: Mapped[str] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE")
    )
    message_id: Mapped[str] = mapped_column(
        ForeignKey("messages.id", ondelete="CASCADE")
    )
    # User facing ID returned from model, not storage UUID ex: doc_0
    document_id: Mapped[str]

    __table_args__ = (
        Index("document_conversation_id_user_id", conversation_id, user_id),
        Index("document_conversation_id", conversation_id),
        Index("document_message_id", message_id),
        Index("document_user_id", user_id),
    )
