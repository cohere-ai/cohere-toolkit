from enum import StrEnum

from backend.config.settings import Settings
from backend.schemas.tool import ToolCategory, ToolDefinition
from backend.services.logger.utils import LoggerFactory
from backend.tools import (
    BraveWebSearch,
    Calculator,
    GoogleDrive,
    GoogleWebSearch,
    HybridWebSearch,
    LangChainWikiRetriever,
    PythonInterpreter,
    ReadFileTool,
    SearchFileTool,
    TavilyWebSearch,
    WebScrapeTool,
)

logger = LoggerFactory().get_logger()

"""
Tool Name enum, mapping to the tool's main implementation class.
"""
class Tool(StrEnum):
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

ALL_TOOLS = {
    Tool.Hybrid_Web_Search: ToolDefinition(
        display_name="Hybrid Web Search",
        implementation=HybridWebSearch,
        parameter_definitions={
            "query": {
                "description": "Query for retrieval.",
                "type": "str",
                "required": True,
            }
        },
        is_visible=True,
        is_available=HybridWebSearch.is_available(),
        error_message="HybridWebSearch not available, please make sure to set at least one option in the tools.hybrid_web_search.enabled_web_searches variable in your configuration.yaml",
        category=ToolCategory.WebSearch,
        description="Returns a list of relevant document snippets for a textual query retrieved from the internet using a mix of any existing Web Search tools.",
    ),
}


def get_available_tools() -> dict[Tool, dict]:
    use_community_tools = Settings().feature_flags.use_community_features

    # Iterate through values in the Tool enum

    tools = ALL_TOOLS.copy()
    if use_community_tools:
        try:
            from community.config.tools import COMMUNITY_TOOLS

            tools = ALL_TOOLS.copy()
            tools.update(COMMUNITY_TOOLS)
        except ImportError:
            logger.warning(
                event="[Tools] Error loading tools: Community tools not available."
            )

    for tool in tools.values():
        # Conditionally set error message
        tool.error_message = tool.error_message if not tool.is_available else None
        # Retrieve name
        tool.name = tool.implementation.ID

    enabled_tools = Settings().tools.enabled_tools
    if enabled_tools is not None and len(enabled_tools) > 0:
        tools = {key: value for key, value in tools.items() if key in enabled_tools}
    return tools
