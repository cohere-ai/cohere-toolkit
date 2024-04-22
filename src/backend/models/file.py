from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from backend.models.base import Base


class File(Base):
    __tablename__ = "files"

    user_id: Mapped[str]
    message_id: Mapped[str] = mapped_column(
        ForeignKey("messages.id", ondelete="CASCADE"), nullable=True
    )
    conversation_id: Mapped[str] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE")
    )

    file_name: Mapped[str]
    file_path: Mapped[str]
    file_size: Mapped[int] = mapped_column(default=0)
