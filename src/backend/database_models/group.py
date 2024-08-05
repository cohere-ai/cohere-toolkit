from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped, relationship

from backend.database_models import User, UserGroupAssociation
from backend.database_models.base import Base


class Group(Base):
    __tablename__ = "groups"

    display_name: Mapped[str] = mapped_column(String, nullable=True)

    users: Mapped[list[User]] = relationship(
        "User", secondary="user_group", backref="groups"
    )

    user_associations: Mapped[list["UserGroupAssociation"]] = relationship(
        back_populates="group"
    )
