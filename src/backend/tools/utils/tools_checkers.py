from backend.schemas.tool import ToolCategory, ToolDefinition
from community.config.tools import CommunityTool


def tool_has_category(tool: ToolDefinition, category: ToolCategory) -> bool:
    """
    Check if a tool has a specific category.

    Args:
        tool (ToolDefinition): The tool to check.
        category (ToolCategory): The category to check for.

    Returns:
        bool: True if the tool has the category, False otherwise.
    """
    return tool.category == category


def is_community_tool(tool: ToolDefinition) -> bool:
    """
    Check if a tool is a community tool.

    Args:
        tool (ToolDefinition): The tool to check.

    Returns:
        bool: True if the tool is a community tool, False otherwise.
    """
    return tool.name in CommunityTool
