from typing import List

from sqlalchemy import Column, ForeignKey, Index, String, Table
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database_models.base import Base
from backend.database_models.document import Document

citation_documents = Table(
    "citation_documents",
    Base.metadata,
    Column("left_id", ForeignKey("documents.id", ondelete="CASCADE")),
    Column("right_id", ForeignKey("citations.id", ondelete="CASCADE")),
)


class Citation(Base):
    __tablename__ = "citations"

    text: Mapped[str]
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    start: Mapped[int]
    end: Mapped[int]

    message_id: Mapped[str] = mapped_column(
        ForeignKey("messages.id", ondelete="CASCADE")
    )
    document_ids: Mapped[List[str]] = mapped_column(ARRAY(String))

    documents: Mapped[List[Document]] = relationship(secondary=citation_documents)

    __table_args__ = (
        Index("citation_message_id_user_id", message_id, user_id),
        Index("citation_message_id", message_id),
        Index("citation_user_id", user_id),
    )
