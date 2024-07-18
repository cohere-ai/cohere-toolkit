from typing import Optional

from sqlalchemy import Float, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database_models.agent_tool_metadata import AgentToolMetadata
from backend.database_models.base import Base


class Agent(Base):
    __tablename__ = "agents"

    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    preamble: Mapped[str] = mapped_column(Text, default="", nullable=False)
    temperature: Mapped[float] = mapped_column(Float, default=0.3, nullable=False)
    tools: Mapped[list[str]] = mapped_column(ARRAY(Text), default=[], nullable=False)
    tools_metadata: Mapped[list[AgentToolMetadata]] = relationship("AgentToolMetadata")

    # TODO @scott-cohere: eventually switch to Fkey when new deployment tables are implemented
    # TODO @scott-cohere: deployments have different names for models, need to implement mapping later
    # enum place holders
    model: Mapped[str] = mapped_column(Text, nullable=False)
    # This is not used for now, just default it to Cohere Platform
    deployment: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    organization_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey(
            "organizations.id", name="agents_organization_id_fkey", ondelete="CASCADE"
        )
    )

    __table_args__ = (UniqueConstraint("name", "version", name="_name_version_uc"),)
