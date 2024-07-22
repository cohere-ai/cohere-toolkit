from typing import Optional

from sqlalchemy import ForeignKey, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from backend.database_models.base import Base


class AgentToolMetadata(Base):
    __tablename__ = "agent_tool_metadata"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    agent_id: Mapped[str] = mapped_column(
        ForeignKey("agents.id", ondelete="CASCADE"), nullable=False
    )
    tool_name: Mapped[str] = mapped_column(Text, nullable=False)
    artifacts: Mapped[list[dict]] = mapped_column(ARRAY(JSONB), nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "agent_id",
            "tool_name",
            name="_user_agent_tool_name_uc",
        ),
    )
