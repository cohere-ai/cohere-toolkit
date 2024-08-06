from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database_models.base import Base


class Group(Base):
    __tablename__ = "groups"

    display_name: Mapped[str] = mapped_column(String, nullable=True)

    users = relationship("User", secondary="user_group", backref="groups")
    user_associations = relationship("UserGroupAssociation", back_populates="group")
