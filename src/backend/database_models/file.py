from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.database_models.base import Base


class File(Base):
    __tablename__ = "files"

    # TODO: Swap to foreign key once User management implemented
    user_id: Mapped[str] = mapped_column(String)
    message_id: Mapped[str] = mapped_column(
        ForeignKey("messages.id", ondelete="CASCADE"), nullable=True
    )
    conversation_id: Mapped[str] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE")
    )

    file_name: Mapped[str]
    file_path: Mapped[str]
    file_size: Mapped[int] = mapped_column(default=0)

    __table_args__ = (
        Index("file_conversation_id_user_id", conversation_id, user_id),
        Index("file_conversation_id", conversation_id),
        Index("file_message_id", message_id),
        Index("file_user_id", user_id),
    )
