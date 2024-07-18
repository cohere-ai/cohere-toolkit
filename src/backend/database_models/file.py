from sqlalchemy import ForeignKey, ForeignKeyConstraint, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.database_models.base import Base


class File(Base):
    __tablename__ = "files"

    user_id: Mapped[str] = mapped_column(String, nullable=True)
    message_id: Mapped[str] = mapped_column(
        ForeignKey("messages.id", ondelete="CASCADE"), nullable=True
    )
    conversation_id: Mapped[str] = mapped_column(String, nullable=True)

    file_name: Mapped[str]
    file_path: Mapped[str]
    file_size: Mapped[int] = mapped_column(default=0)
    file_content: Mapped[str] = mapped_column(default="")

    __table_args__ = (
        ForeignKeyConstraint(
            ["conversation_id", "user_id"],
            ["conversations.id", "conversations.user_id"],
            name="file_conversation_id_user_id_fkey",
            ondelete="CASCADE",
        ),
        Index("file_conversation_id_user_id", conversation_id, user_id),
        Index("file_conversation_id", conversation_id),
        Index("file_message_id", message_id),
        Index("file_user_id", user_id),
    )
