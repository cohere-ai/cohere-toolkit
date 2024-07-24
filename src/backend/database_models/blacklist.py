from sqlalchemy import DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.database_models.base import Base


class Blacklist(Base):
    """
    Table that contains the list of JWT access tokens that are blacklisted during logout.
    """

    __tablename__ = "blacklist"

    token_id: Mapped[str] = mapped_column(String)
    effective_at = mapped_column(DateTime, nullable=False)
    expires_at = mapped_column(DateTime, nullable=False)

    __table_args__ = (Index("blacklist_token_id", token_id),)
