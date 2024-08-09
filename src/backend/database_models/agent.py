from typing import Optional

from sqlalchemy import JSON, Boolean, Float, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database_models.agent_tool_metadata import AgentToolMetadata
from backend.database_models.base import Base


class AgentDeploymentModel(Base):
    __tablename__ = "agent_deployment_model"

    agent_id: Mapped[str] = mapped_column(ForeignKey("agents.id", ondelete="CASCADE"))
    deployment_id: Mapped[str] = mapped_column(
        ForeignKey("deployments.id", ondelete="CASCADE")
    )
    model_id: Mapped[str] = mapped_column(ForeignKey("models.id", ondelete="CASCADE"))
    deployment_config: Mapped[Optional[dict]] = mapped_column(JSON)
    is_default_deployment: Mapped[bool] = mapped_column(Boolean, default=False)
    is_default_model: Mapped[bool] = mapped_column(Boolean, default=False)

    agent = relationship("Agent", back_populates="agent_deployment_associations")
    deployment = relationship(
        "Deployment", back_populates="agent_deployment_associations"
    )
    model = relationship("Model", back_populates="agent_deployment_associations")

    __table_args__ = (
        UniqueConstraint(
            "deployment_id", "agent_id", "model_id", name="deployment_agent_model_uc"
        ),
    )


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

    deployments = relationship(
        "Deployment",
        secondary="agent_deployment_model",
        back_populates="agents",
        overlaps="deployments,models,agents,agent,agent_deployment_associations,deployment,model",
    )
    models = relationship(
        "Model",
        secondary="agent_deployment_model",
        back_populates="agents",
        overlaps="deployments,models,agents,agent,agent_deployment_associations,model",
    )
    agent_deployment_associations = relationship(
        "AgentDeploymentModel", back_populates="agent"
    )

    user = relationship("User", back_populates="agents")
    # TODO Eugene  - add the composite index here if needed
    __table_args__ = (
        UniqueConstraint("name", "version", "user_id", name="_name_version_user_uc"),
    )

    @property
    def default_model_association(self):
        default_association = next(
            (
                agent_deployment
                for agent_deployment in self.agent_deployment_associations
                if agent_deployment.is_default_deployment
                and agent_deployment.is_default_model
            ),
            None,
        )
        if not default_association:
            default_association = (
                self.agent_deployment_associations[0]
                if self.agent_deployment_associations
                else None
            )
        return default_association

    @property
    def deployment(self):
        default_model_association = next(
            (
                agent_deployment
                for agent_deployment in self.agent_deployment_associations
                if agent_deployment.is_default_deployment
                and agent_deployment.is_default_model
            ),
            None,
        )
        if not default_model_association:
            default_model_association = (
                self.agent_deployment_associations[0]
                if self.agent_deployment_associations
                else None
            )
        # TODO Eugene - return the deployment object here when FE is ready Discuss with Scott
        return (
            default_model_association.deployment.name
            if default_model_association
            else None
        )

    @property
    def model(self):
        default_model_association = next(
            (
                agent_deployment
                for agent_deployment in self.agent_deployment_associations
                if agent_deployment.is_default_deployment
                and agent_deployment.is_default_model
            ),
            None,
        )
        if not default_model_association:
            default_model_association = (
                self.agent_deployment_associations[0]
                if self.agent_deployment_associations
                else None
            )
        # TODO Eugene - return the model object here when FE is ready Discuss with Scott
        return (
            default_model_association.model.name if default_model_association else None
        )

    def set_default_agent_deployment_model(self, deployment_id: str, model_id: str):
        default_model_deployment = next(
            (
                agent_deployment
                for agent_deployment in self.agent_deployment_associations
                if agent_deployment.is_default_deployment
                and agent_deployment.is_default_model
            ),
            None,
        )
        if default_model_deployment:
            default_model_deployment.is_default_deployment = False
            default_model_deployment.is_default_model = False

        new_default_model_deployment = next(
            (
                agent_deployment
                for agent_deployment in self.agent_deployment_associations
                if agent_deployment.deployment_id == deployment_id
                and agent_deployment.model_id == model_id
            ),
            None,
        )
        if new_default_model_deployment:
            new_default_model_deployment.is_default_deployment = True
            new_default_model_deployment.is_default_model = True
