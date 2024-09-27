from enum import StrEnum

from backend.config.settings import Settings
from backend.schemas.tool import Category, ManagedTool
from backend.services.logger.utils import LoggerFactory
from backend.tools import (
    BraveWebSearch,
    Calculator,
    GoogleDrive,
    GoogleDriveAuth,
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
List of available tools. Each tool should have a name, implementation, is_visible and category.
They can also have kwargs if necessary.

You can switch the visibility of a tool by changing the is_visible parameter to True or False.
If a tool is not visible, it will not be shown in the frontend.

If you want to add a new tool, check the instructions on how to implement a retriever in the documentation.
Don't forget to add the implementation to this AVAILABLE_TOOLS dictionary!
"""

class ToolName(StrEnum):
    Wiki_Retriever_LangChain = LangChainWikiRetriever.NAME
    Search_File = SearchFileTool.NAME
    Read_File = ReadFileTool.NAME
    Python_Interpreter = PythonInterpreter.NAME
    Calculator = Calculator.NAME
    Google_Drive = GoogleDrive.NAME
    Web_Scrape = WebScrapeTool.NAME
    Tavily_Web_Search = TavilyWebSearch.NAME
    Google_Web_Search = GoogleWebSearch.NAME
    Brave_Web_Search = BraveWebSearch.NAME
    Hybrid_Web_Search = HybridWebSearch.NAME


ALL_TOOLS = {
    ToolName.Search_File: ManagedTool(
        display_name="Search File",
        implementation=SearchFileTool,
        parameter_definitions={
            "search_query": {
                "description": "Textual search query to search over the file's content for",
                "type": "str",
                "required": True,
            },
            "files": {
                "description": "A list of files represented as tuples of (filename, file ID) to search over",
                "type": "list[tuple[str, str]]",
                "required": True,
            },
        },
        is_visible=True,
        is_available=SearchFileTool.is_available(),
        error_message="SearchFileTool not available.",
        category=Category.FileLoader,
        description="Performs a search over a list of one or more of the attached files for a textual search query",
    ),
    ToolName.Read_File: ManagedTool(
        display_name="Read Document",
        implementation=ReadFileTool,
        parameter_definitions={
            "file": {
                "description": "A file represented as a tuple (filename, file ID) to read over",
                "type": "tuple[str, str]",
                "required": True,
            }
        },
        is_visible=True,
        is_available=ReadFileTool.is_available(),
        error_message="ReadFileTool not available.",
        category=Category.FileLoader,
        description="Returns the textual contents of an uploaded file, broken up in text chunks.",
    ),
    ToolName.Python_Interpreter: ManagedTool(
        display_name="Python Interpreter",
        implementation=PythonInterpreter,
        parameter_definitions={
            "code": {
                "description": "Python code to execute using an interpreter",
                "type": "str",
                "required": True,
            }
        },
        is_visible=True,
        is_available=PythonInterpreter.is_available(),
        error_message="PythonInterpreterFunctionTool not available, please make sure to set the tools.python_interpreter.url variable in your configuration.yaml",
        category=Category.Function,
        description="Runs python code in a sandbox.",
    ),
    ToolName.Wiki_Retriever_LangChain: ManagedTool(
        display_name="Wikipedia",
        implementation=LangChainWikiRetriever,
        parameter_definitions={
            "query": {
                "description": "Query for retrieval.",
                "type": "str",
                "required": True,
            }
        },
        kwargs={"chunk_size": 300, "chunk_overlap": 0},
        is_visible=True,
        is_available=LangChainWikiRetriever.is_available(),
        error_message="LangChainWikiRetriever not available.",
        category=Category.DataLoader,
        description="Retrieves documents from Wikipedia using LangChain.",
    ),
    ToolName.Calculator: ManagedTool(
        display_name="Calculator",
        implementation=Calculator,
        parameter_definitions={
            "code": {
                "description": "The expression for the calculator to evaluate, it should be a valid mathematical expression.",
                "type": "str",
                "required": True,
            }
        },
        is_visible=False,
        is_available=Calculator.is_available(),
        error_message="Calculator tool not available.",
        category=Category.Function,
        description="This is a powerful multi-purpose calculator which is capable of a wide array of math calculations.",
    ),
    ToolName.Google_Drive: ManagedTool(
        display_name="Google Drive",
        implementation=GoogleDrive,
        parameter_definitions={
            "query": {
                "description": "Query to search Google Drive documents with.",
                "type": "str",
                "required": True,
            }
        },
        is_visible=True,
        is_available=GoogleDrive.is_available(),
        auth_implementation=GoogleDriveAuth,
        error_message="Google Drive not available, please enable it in the GoogleDrive tool class.",
        category=Category.DataLoader,
        description="Returns a list of relevant document snippets for the user's google drive.",
    ),
    ToolName.Web_Scrape: ManagedTool(
        name=ToolName.Web_Scrape,
        display_name="Web Scrape",
        implementation=WebScrapeTool,
        parameter_definitions={
            "url": {
                "description": "The url to scrape.",
                "type": "str",
                "required": True,
            },
            "query": {
                "description": "The query to use to select the most relevant passages to return. Using an empty string will return the passages in the order they appear on the webpage",
                "type": "str",
                "required": False,
            },
        },
        is_visible=True,
        is_available=WebScrapeTool.is_available(),
        error_message="WebScrapeTool not available.",
        category=Category.DataLoader,
        description="Scrape and returns the textual contents of a webpage as a list of passages for a given url.",
    ),
    ToolName.Tavily_Web_Search: ManagedTool(
        display_name="Web Search",
        implementation=TavilyWebSearch,
        parameter_definitions={
            "query": {
                "description": "Query to search the internet with",
                "type": "str",
                "required": True,
            }
        },
        is_visible=False,
        is_available=TavilyWebSearch.is_available(),
        error_message="TavilyWebSearch not available, please make sure to set the tools.tavily_web_search.api_key variable in your secrets.yaml",
        category=Category.WebSearch,
        description="Returns a list of relevant document snippets for a textual query retrieved from the internet.",
    ),
    ToolName.Google_Web_Search: ManagedTool(
        display_name="Google Web Search",
        implementation=GoogleWebSearch,
        parameter_definitions={
            "query": {
                "description": "A search query for the Google search engine.",
                "type": "str",
                "required": True,
            }
        },
        is_visible=False,
        is_available=GoogleWebSearch.is_available(),
        error_message="Google Web Search not available, please enable it in the GoogleWebSearch tool class.",
        category=Category.WebSearch,
        description="Returns relevant results by performing a Google web search.",
    ),
    ToolName.Brave_Web_Search: ManagedTool(
        display_name="Brave Web Search",
        implementation=BraveWebSearch,
        parameter_definitions={
            "query": {
                "description": "Query for retrieval.",
                "type": "str",
                "required": True,
            }
        },
        is_visible=False,
        is_available=BraveWebSearch.is_available(),
        error_message="BraveWebSearch not available, please make sure to set the tools.brave_web_search.api_key variable in your secrets.yaml",
        category=Category.WebSearch,
        description="Returns a list of relevant document snippets for a textual query retrieved from the internet using Brave Search.",
    ),
    ToolName.Hybrid_Web_Search: ManagedTool(
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
        category=Category.WebSearch,
        description="Returns a list of relevant document snippets for a textual query retrieved from the internet using a mix of any existing Web Search tools.",
    ),
}


def get_available_tools() -> dict[ToolName, dict]:
    use_community_tools = Settings().feature_flags.use_community_features

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
        tool.name = tool.implementation.NAME

    enabled_tools = Settings().tools.enabled_tools
    if enabled_tools is not None and len(enabled_tools) > 0:
        tools = {key: value for key, value in tools.items() if key in enabled_tools}
    return tools


AVAILABLE_TOOLS = get_available_tools()
