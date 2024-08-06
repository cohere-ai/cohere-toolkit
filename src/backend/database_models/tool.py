from typing import Optional

from sqlalchemy import JSON, Boolean, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.database_models.base import Base


class Tool(Base):
    __tablename__ = "tools"

    name: Mapped[str] = mapped_column(Text, nullable=False)
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    implementation: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, default="")
    parameter_definitions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True)
    auth_implementation: Mapped[Optional[str]] = mapped_column(Text)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[Optional[str]] = mapped_column(Text)
