from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column

from backend.database_models.base import Base


class User(Base):
    __tablename__ = "users"

    fullname: Mapped[str] = mapped_column()
    email: Mapped[Optional[str]] = mapped_column()
