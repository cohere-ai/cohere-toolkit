from typing import Optional

from sqlalchemy import JSON, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database_models.base import Base


class Model(Base):
    __tablename__ = "models"

    name: Mapped[str] = mapped_column(Text, nullable=False)
    cohere_name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, default="")

    deployment_id: Mapped[str] = mapped_column(
        ForeignKey("deployments.id", ondelete="CASCADE")
    )

    deployment = relationship("Deployment", back_populates="models")
    agent_deployment_associations = relationship(
        "AgentDeploymentModel", back_populates="model"
    )
    agents = relationship(
        "Agent",
        secondary="agent_deployment_model",
        back_populates="models",
        overlaps="deployments,models,agents,agent,agent_deployment_associations,model",
    )

    def __str__(self):
        return self.name
