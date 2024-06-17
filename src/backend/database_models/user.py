from typing import List, Optional

from sqlalchemy import Column, ForeignKey, Table, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database_models.base import Base

user_organization_association = Table(
    "user_organization",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "organization_id",
        ForeignKey("organizations.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class User(Base):
    __tablename__ = "users"

    fullname: Mapped[str] = mapped_column()
    email: Mapped[Optional[str]] = mapped_column()
    hashed_password: Mapped[Optional[bytes]] = mapped_column()
    __table_args__ = (UniqueConstraint("email", name="unique_user_email"),)
