from typing import List, Optional

from sqlalchemy import JSON, Boolean, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database_models.base import Base

DEFAULT_TOOLS_MODULE = "backend.tools"
COMMUNITY_TOOLS_MODULE = "community.tools"
DEFAULT_AUTH_MODULE = "backend.services.auth"


class Tool(Base):
    __tablename__ = "tools"
    # TODO Eugene: change column list after Cohere confirmation
    name: Mapped[str] = mapped_column(Text, nullable=False)
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    implementation_class_name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, default="")
    parameter_definitions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    kwargs: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    default_tool_config: Mapped[Optional[dict]] = mapped_column(JSON)
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True)
    is_community: Mapped[bool] = mapped_column(Boolean, default=False)
    error_message_text: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[Optional[str]] = mapped_column(Text)
    auth_implementation_class_name: Mapped[Optional[str]] = mapped_column(Text)

    agent_tool_associations = relationship("AgentTool", back_populates="tool")

    agents = relationship(
        "Agent",
        secondary="agent_tool",
        back_populates="associated_tools",
        overlaps="tools,agents,agent,agent_tool_associations,tool",
    )

    tool_metadata = relationship("AgentToolMetadata", back_populates="tool")

    __table_args__ = (UniqueConstraint("name", name="tool_name_uc"),)

    @property
    def is_available(self) -> bool:
        # Check if an agent has a tool config set
        for agent_assoc in self.agent_tool_associations:
            if not agent_assoc.tool_config:
                continue
            if not agent_assoc.tool_config or all(
                value for value in agent_assoc.tool_config.values()
            ):
                return True
        # if no agent has a tool config set, check if the tool has a default config or no config
        if not self.default_tool_config:
            return True
        return all(value for value in self.default_tool_config.values())

    @property
    def error_message(self) -> str:
        return self.error_message_text if not self.is_available else None

    @property
    def env_vars(self) -> List[str]:
        return list(self.default_tool_config.keys()) if self.default_tool_config else []

    @property
    def implementation(self):
        from backend.services.get_module_class import get_module_class

        if not self.implementation_class_name:
            return None
        cls = get_module_class(DEFAULT_TOOLS_MODULE, self.implementation_class_name)
        if not cls:
            cls = get_module_class(
                COMMUNITY_TOOLS_MODULE, self.implementation_class_name
            )

        return cls

    @property
    def auth_implementation(self):
        from backend.services.get_module_class import get_module_class

        if not self.auth_implementation_class_name:
            return None
        cls = get_module_class(DEFAULT_AUTH_MODULE, self.implementation_class_name)
        return cls
