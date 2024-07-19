import os

from dotenv import load_dotenv
from sqlalchemy.orm import Session

from backend.config.tools import ALL_TOOLS, ToolName
from community.config.tools import COMMUNITY_TOOLS, CommunityToolName

from backend.database_models import (
    Agent,
    User,
    Organization,
    Tool
)

load_dotenv()

tools = ALL_TOOLS.copy()
tools.update(COMMUNITY_TOOLS)


TOOLS_CONFIGS = {

}


def seed_tools(op):
    """
    Seed default deployments, models, organization, user and agent.
    """
    session = Session(op.get_bind())
    for tool_name, tool in tools:
        if tool_name in TOOLS_CONFIGS:
            default_tool_config = TOOLS_CONFIGS[tool_name]
        is_community = isinstance(tool_name, CommunityToolName)
        db_tool = Tool(
            name=str(tool_name),
            display_name=tool.display_name,
            implementation_class_name=tool.implementation.__name__,
            description=tool.description,
            parameter_definitions=tool.parameter_definitions,
            default_tool_config=default_tool_config,
            is_visible=tool.is_visible,
            is_community=is_community,
            auth_implementation=tool.auth_implementation,
            error_message=tool.error_message,
            category=tool.category,
        )
        session.add(db_tool)
        session.commit()


def delete_default_models(op):
    """
    Delete deployments and models.
    """
    session = Session(op.get_bind())
    session.query(User).filter_by(id="user-id").delete()
    session.query(Organization).filter_by(id="default").delete()
    session.commit()
