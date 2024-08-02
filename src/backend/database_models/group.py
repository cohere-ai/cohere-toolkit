from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database_models.base import Base


class Group(Base):
    __tablename__ = "groups"

    display_name: Mapped[str] = mapped_column(String, nullable=True)
    members = relationship("UserGroup", back_populates="group")


class UserGroup(Base):
    __tablename__ = "user_group"

    group_id: Mapped[str] = mapped_column(
        String, ForeignKey("groups.id"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    display: Mapped[str] = mapped_column(String, nullable=True)
    group = relationship("Group", back_populates="members")
