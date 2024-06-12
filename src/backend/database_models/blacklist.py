from sqlalchemy import Index, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.database_models.base import Base


class Blacklist(Base):
    """
    Table that contains the list of JWT access tokens that are blacklisted during logout.
    """

    __tablename__ = "blacklist"

    token_id: Mapped[str] = mapped_column(String)

    __table_args__ = (Index("blacklist_token_id", token_id),)
