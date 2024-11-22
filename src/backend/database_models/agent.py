from typing import Optional

from sqlalchemy import JSON, Boolean, Float, ForeignKey, Integer, Text, UniqueConstraint
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

    tools: Mapped[list[str]] = mapped_column(JSON, default=[], nullable=False)
    tools_metadata: Mapped[list[AgentToolMetadata]] = relationship("AgentToolMetadata")

    user_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.id", name="agents_user_id_fkey", ondelete="CASCADE")
    )
    organization_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey(
            "organizations.id", name="agents_organization_id_fkey", ondelete="CASCADE"
        )
    )
    is_private: Mapped[bool] = mapped_column(Boolean, default=False)

    deployment_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey(
            "deployments.id", name="agents_deployment_id_fkey", ondelete="CASCADE"
        )
    )

    model_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey(
            "models.id", name="agents_model_id_fkey", ondelete="CASCADE"
        )
    )

    user = relationship("User", back_populates="agents")
    assigned_deployment = relationship("Deployment", backref="agents")
    assigned_model = relationship("Model", backref="agents")

    # TODO Eugene  - add the composite index here if needed
    __table_args__ = (
        UniqueConstraint("name", "version", "user_id", name="_name_version_user_uc"),
    )

    @property
    def model(self) -> Optional[str]:
        return self.assigned_model.name if self.assigned_model else None

    # Property for deployment name
    @property
    def deployment(self) -> Optional[str]:
        return self.assigned_deployment.name if self.assigned_deployment else None
