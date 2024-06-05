from typing import List
from enum import StrEnum

from sqlalchemy import UniqueConstraint, Integer, String, Float, Enum
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

    version: Mapped[int] = mapped_column(Integer, default=1)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    preamble: Mapped[str] = mapped_column(String, nullable=True)
    temperature: Mapped[float] = mapped_column(Float, default=0.3)
    # tool: Mapped[List["Tool"]] = relationship()

    model: Mapped[Model] = mapped_column(Enum(Model, native_enum=False), nullable=False)
    deployment: Mapped[Deployment] = mapped_column(Enum(Deployment, native_enum=False), nullable=False)

    # org_id: Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[str] = mapped_column(String, nullable=False)

    # __table_args__ = (UniqueConstraint('org_id', 'name', name='_org_id_name_uc'),)