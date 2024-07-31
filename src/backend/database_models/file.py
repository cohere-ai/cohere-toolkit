from sqlalchemy import ForeignKey, ForeignKeyConstraint, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.database_models.base import Base


class File(Base):
    __tablename__ = "files"

    user_id: Mapped[str] = mapped_column(String, nullable=True)
    file_name: Mapped[str]
    file_path: Mapped[str]
    file_size: Mapped[int] = mapped_column(default=0)
    file_content: Mapped[str] = mapped_column(default="")

    __table_args__ = ()
