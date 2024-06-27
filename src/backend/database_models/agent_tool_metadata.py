from typing import Optional

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.database_models.base import Base


class AgentToolMetadata(Base):
    __tablename__ = "agent_tool_metadata"

    user_id: Mapped[str] = mapped_column(String)
    agent_id: Mapped[str] = mapped_column(
        ForeignKey("agents.id", ondelete="CASCADE"), nullable=False
    )
    tool_name: Mapped[str] = mapped_column(String)
    artifact_id: Mapped[str] = mapped_column(String)

    __table_args__ = (UniqueConstraint("user_id", "agent_id", "tool_name", name="_user_agent_tool_name_uc"),)
