from typing import List

from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database_models.base import Base
from backend.database_models.document import Document


class CitationDocuments(Base):
    __tablename__ = "citation_documents"

    left_id: Mapped[str] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"))
    right_id: Mapped[str] = mapped_column(
        ForeignKey("citations.id", ondelete="CASCADE")
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

    documents: Mapped[List[Document]] = relationship(secondary="citation_documents")

    @property
    def document_ids(self) -> List[str]:
        return [document.document_id for document in self.documents]

    __table_args__ = (
        Index("citation_message_id_user_id", message_id, user_id),
        Index("citation_message_id", message_id),
        Index("citation_user_id", user_id),
    )
