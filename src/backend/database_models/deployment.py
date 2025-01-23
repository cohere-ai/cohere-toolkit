from typing import List, Optional

from sqlalchemy import JSON, Boolean, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database_models.base import Base

DEFAULT_MODEL_DEPLOYMENTS_MODULE = "backend.model_deployments"
COMMUNITY_MODEL_DEPLOYMENTS_MODULE = "community.model_deployments"


class Deployment(Base):
    __tablename__ = "deployments"

    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, default="")
    deployment_class_name: Mapped[Optional[str]] = mapped_column(Text)
    is_community: Mapped[bool] = mapped_column(Boolean, default=False)
    default_deployment_config: Mapped[Optional[dict]] = mapped_column(JSON)

    models = relationship("Model", back_populates="deployment")

    __table_args__ = (UniqueConstraint("name", name="deployment_name_uc"),)

    def __str__(self):
        return self.name

    @property
    def is_available(self) -> bool:
        # Check if the deployment has a default config
        if not self.default_deployment_config:
            return False
        return all(value != "" for value in self.default_deployment_config.values())

    @property
    def env_vars(self) -> List[str]:
        return (
            list(self.default_deployment_config.keys())
            if self.default_deployment_config
            else []
        )

    @property
    def deployment_class(self):
        from backend.model_deployments.utils import get_module_class

        if not self.deployment_class_name:
            return None
        cls = get_module_class(
            DEFAULT_MODEL_DEPLOYMENTS_MODULE, self.deployment_class_name
        )
        if not cls:
            cls = get_module_class(
                COMMUNITY_MODEL_DEPLOYMENTS_MODULE, self.deployment_class_name
            )

        return cls
