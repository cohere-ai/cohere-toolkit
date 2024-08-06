from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database_models.agent import Agent
from backend.database_models.base import Base
from backend.database_models.conversation import Conversation
from backend.database_models.user import User


class Organization(Base):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column()
    users: Mapped[List[User]] = relationship(
        "User", secondary="user_organization", backref="organizations"
    )
    conversations: Mapped[List[Conversation]] = relationship(backref="organization")
    agents: Mapped[List[Agent]] = relationship(backref="organization")
