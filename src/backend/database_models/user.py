from typing import Optional

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database_models.base import Base


class UserOrganizationAssociation(Base):
    __tablename__ = "user_organization"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    organization_id: Mapped[str] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), primary_key=True
    )


class UserGroupAssociation(Base):
    __tablename__ = "user_group"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    group_id: Mapped[str] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True
    )
    display: Mapped[str] = mapped_column()

    group = relationship("Group", back_populates="user_associations")


class User(Base):
    __tablename__ = "users"

    user_name: Mapped[Optional[str]] = mapped_column()
    fullname: Mapped[str] = mapped_column()
    external_id: Mapped[Optional[str]] = mapped_column()
    active: Mapped[Optional[bool]] = mapped_column()

    email: Mapped[Optional[str]] = mapped_column()
    hashed_password: Mapped[Optional[bytes]] = mapped_column()

    __table_args__ = (
        UniqueConstraint("email", name="unique_user_email"),
        UniqueConstraint("user_name", name="unique_user_name"),
    )

    agents = relationship("Agent", back_populates="user")
