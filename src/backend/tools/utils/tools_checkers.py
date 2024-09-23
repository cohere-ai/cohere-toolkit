from backend.schemas.tool import Category, ManagedTool
from community.config.tools import CommunityToolName


def tool_has_category(tool: ManagedTool, category: Category) -> bool:
    """
    Check if a tool has a specific category.

    Args:
    tool (ManagedTool): The tool to check.
    category (Category): The category to check for.

    Returns:
    bool: True if the tool has the category, False otherwise.
    """
    return tool.category == category


def is_community_tool(tool: ManagedTool) -> bool:
    """
    Check if a tool is a community tool.

    Args:
    tool (ManagedTool): The tool to check.

    Returns:
    bool: True if the tool is a community tool, False otherwise.
    """
    return tool.name in CommunityToolName
