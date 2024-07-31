from sqlalchemy.orm import mapped_column, Mapped

from backend.database_models.base import Base


class Group(Base):
    __tablename__ = "groups"

    display_name: Mapped[str] = mapped_column()