from enum import StrEnum

from sqlalchemy import Enum, Float, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from backend.database_models.base import Base
from backend.config.tools import ToolName


class AgentDeployment(StrEnum):
    COHERE_PLATFORM = "Cohere Platform"
    SAGE_MAKER = "SageMaker"
    AZURE = "Azure"
    BEDROCK = "Bedrock"


class AgentModel(StrEnum):
    COMMAND_R = "command-r"
    COMMAND_R_PLUS = "command-r-plus"
    COMMAND_LIGHT = "command-light"
    COMMAND = "command"


class Agent(Base):
    __tablename__ = "agents"

    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    preamble: Mapped[str] = mapped_column(Text, default="", nullable=False)
    temperature: Mapped[float] = mapped_column(Float, default=0.3, nullable=False)
    tools: Mapped[list[ToolName]] = mapped_column(ARRAY(Text), default=[], nullable=False)

    # TODO @scott-cohere: eventually switch to Fkey when new deployment tables are implemented
    # TODO @scott-cohere: deployments have different names for models, need to implement mapping later
    # enum place holders
    model: Mapped[AgentModel] = mapped_column(
        Enum(AgentModel, native_enum=False), nullable=False
    )
    deployment: Mapped[AgentDeployment] = mapped_column(
        Enum(AgentDeployment, native_enum=False), nullable=False
    )

    user_id: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (UniqueConstraint("name", "version", name="_name_version_uc"),)
