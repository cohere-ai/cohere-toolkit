from enum import Enum

from backend.config.settings import Settings
from backend.schemas.tool import ToolDefinition
from backend.services.logger.utils import LoggerFactory
from backend.tools import (
    BraveWebSearch,
    Calculator,
    GmailTool,
    GoogleDrive,
    GoogleWebSearch,
    HybridWebSearch,
    LangChainWikiRetriever,
    PythonInterpreter,
    ReadFileTool,
    SearchFileTool,
    SharepointTool,
    SlackTool,
    TavilyWebSearch,
    WebScrapeTool,
)
from backend.tools.github.tool import GithubTool

logger = LoggerFactory().get_logger()

"""
Tool Name enum, mapping to the tool's main implementation class.
"""
class Tool(Enum):
    Wiki_Retriever_LangChain = LangChainWikiRetriever
    Read_File = ReadFileTool
    Search_File = SearchFileTool
    Python_Interpreter = PythonInterpreter
    Calculator = Calculator
    Google_Drive = GoogleDrive
    Web_Scrape = WebScrapeTool
    Tavily_Web_Search = TavilyWebSearch
    Google_Web_Search = GoogleWebSearch
    Brave_Web_Search = BraveWebSearch
    Hybrid_Web_Search = HybridWebSearch
    Slack = SlackTool
    Gmail = GmailTool
    Github = GithubTool
    Sharepoint = SharepointTool


def get_available_tools() -> dict[str, ToolDefinition]:
    # Get list of implementations from Tool Enum
    tool_classes = [tool.value for tool in Tool]
    # Generate dictionary of ToolDefinitions keyed by Tool ID
    tools = {
        tool.ID: tool.get_tool_definition() for tool in tool_classes
    }

    # Handle adding Community-implemented tools
    use_community_tools = Settings().get('feature_flags.use_community_features')
    if use_community_tools:
        try:
            from community.config.tools import get_community_tools
            community_tools = get_community_tools()
            tools.update(community_tools)
        except ImportError:
            logger.warning(
                event="[Tools] Error loading tools: Community tools not available."
            )

    return tools
