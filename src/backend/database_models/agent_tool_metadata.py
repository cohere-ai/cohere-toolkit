from typing import List

from sqlalchemy import JSON, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database_models.base import Base


class AgentToolMetadata(Base):
    __tablename__ = "agent_tool_metadata"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    agent_id: Mapped[str] = mapped_column(
        ForeignKey("agents.id", ondelete="CASCADE"), nullable=False
    )
    tool_id: Mapped[str] = mapped_column(
        ForeignKey("tools.id", name="metadata_tool_id_fkey", ondelete="CASCADE"),
        nullable=False,
    )

    agent = relationship("Agent", back_populates="tools_metadata")

    tool = relationship("Tool", back_populates="tool_metadata")

    artifacts: Mapped[List[dict]] = mapped_column(JSON, default=[], nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "agent_id",
            "tool_id",
            name="_user_agent_tool_name_uc",
        ),
    )

    @property
    def tool_name(self):
        return self.tool.name
