from typing import List

from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base
from backend.models.document import Document

citation_documents = Table(
    "citation_documents",
    Base.metadata,
    Column("left_id", ForeignKey("documents.id", ondelete="CASCADE")),
    Column("right_id", ForeignKey("citations.id", ondelete="CASCADE")),
)


class Citation(Base):
    __tablename__ = "citations"

    text: Mapped[str]
    user_id: Mapped[str]
    start: Mapped[int]
    end: Mapped[int]

    message_id: Mapped[str] = mapped_column(
        ForeignKey("messages.id", ondelete="CASCADE")
    )
    documents: Mapped[List[Document]] = relationship(secondary=citation_documents)

    document_ids: Mapped[List[str]] = mapped_column(ARRAY(String))
