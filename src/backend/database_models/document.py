from sqlalchemy import JSON, ForeignKey, ForeignKeyConstraint, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.database_models.base import Base


class Document(Base):
    __tablename__ = "documents"

    text: Mapped[str]
    user_id: Mapped[str] = mapped_column(String, nullable=True)
    title: Mapped[str] = mapped_column(String, nullable=True)
    url: Mapped[str] = mapped_column(String, nullable=True)
    fields: Mapped[dict] = mapped_column(JSON, nullable=True)
    tool_name: Mapped[str] = mapped_column(String, nullable=True)

    conversation_id: Mapped[str] = mapped_column(String, nullable=True)
    message_id: Mapped[str] = mapped_column(
        ForeignKey("messages.id", ondelete="CASCADE")
    )
    # User facing ID returned from model, not storage UUID ex: doc_0
    document_id: Mapped[str]

    __table_args__ = (
        ForeignKeyConstraint(
            ["conversation_id", "user_id"],
            ["conversations.id", "conversations.user_id"],
            name="document_conversation_id_user_id_fkey",
            ondelete="CASCADE",
        ),
        Index("document_conversation_id_user_id", conversation_id, user_id),
        Index("document_conversation_id", conversation_id),
        Index("document_message_id", message_id),
        Index("document_user_id", user_id),
    )
