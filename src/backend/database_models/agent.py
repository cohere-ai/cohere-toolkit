from enum import StrEnum

from sqlalchemy import Enum, Float, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database_models.base import Base


class Deployment(StrEnum):
    COHERE_PLATFORM = "Cohere Platform"
    SAGE_MAKER = "SageMaker"
    AZURE = "Azure"
    BEDROCK = "Bedrock"


class Model(StrEnum):
    COMMAND_R = "command-r"
    COMMAND_R_PLUS = "command-r-plus"
    COMMAND_LIGHT = "command-light"
    COMMAND = "command"


class Agent(Base):
    __tablename__ = "agents"

    version: Mapped[int] = mapped_column(Integer, default=1, nullable=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=True)
    preamble: Mapped[str] = mapped_column(Text, default="", nullable=True)
    temperature: Mapped[float] = mapped_column(Float, default=0.3, nullable=True)
    # tool: Mapped[List["Tool"]] = relationship()

    # TODO @scott-cohere: eventually switch to Fkey when new deployment tables are implemented
    # TODO @scott-cohere: deployments have different names for models, need to implement mapping later
    # enum place holders
    model: Mapped[Model] = mapped_column(Enum(Model, native_enum=False), nullable=False)
    deployment: Mapped[Deployment] = mapped_column(
        Enum(Deployment, native_enum=False), nullable=False
    )

    user_id: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (UniqueConstraint("name", "version", name="_name_version_uc"),)
