from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship

from backend.database_models.base import Base


class Group(Base):
    __tablename__ = "groups"

    display_name: Mapped[str] = mapped_column(String, nullable=True)
    members = relationship(
        "UserGroup", back_populates="group", cascade="all, delete-orphan"
    )


class UserGroup(Base):
    __tablename__ = "user_group"

    group_id: Mapped[str] = mapped_column(
        String, ForeignKey("groups.id"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    display: Mapped[str] = mapped_column(String, nullable=True)
    group = relationship("Group", back_populates="members")

    __table_args__ = (UniqueConstraint("group_id", "user_id", name="uix_group_user"),)
