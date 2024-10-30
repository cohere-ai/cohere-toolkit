from enum import StrEnum

from backend.config.settings import Settings
from backend.schemas.tool import ToolCategory, ToolDefinition
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
Tool Name enum. To add a tool definition, ensure you create a ToolName entry, and
add your tool definition to the `ALL_TOOLS` list.
"""
class ToolName(StrEnum):
    Wiki_Retriever_LangChain = LangChainWikiRetriever.ID
    Search_File = SearchFileTool.ID
    Read_File = ReadFileTool.ID
    Python_Interpreter = PythonInterpreter.ID
    Calculator = Calculator.ID
    Google_Drive = GoogleDrive.ID
    Web_Scrape = WebScrapeTool.ID
    Tavily_Web_Search = TavilyWebSearch.ID
    Google_Web_Search = GoogleWebSearch.ID
    Brave_Web_Search = BraveWebSearch.ID
    Hybrid_Web_Search = HybridWebSearch.ID

"""
Full list of all tools. Key is the enum value defined above, and the value should
be a dictionary containing non-optional variables in the `ToolDefinition` schema.

During run-time, the availables tools will be filtered out based on the tool's implemented
`is_available()` method. Generally, this depends on some configuration variables.
"""
ALL_TOOLS = {
    ToolName.Search_File: ToolDefinition(
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
        category=ToolCategory.FileLoader,
        description="Performs a search over a list of one or more of the attached files for a textual search query",
    ),
    ToolName.Read_File: ToolDefinition(
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
        category=ToolCategory.FileLoader,
        description="Returns the textual contents of an uploaded file, broken up in text chunks.",
    ),
    ToolName.Python_Interpreter: ToolDefinition(
        display_name="Python Interpreter",
        implementation=PythonInterpreter,
        parameter_definitions={
            "code": {
                "description": (
                    "Python code to execute using the Python interpreter with no internet access. "
                    "Do not generate code that tries to open files directly, instead use file contents passed to the interpreter, "
                    "then print output or save output to a file."
                ),
                "type": "str",
                "required": True,
            }
        },
        is_visible=True,
        is_available=PythonInterpreter.is_available(),
        error_message="PythonInterpreterFunctionTool not available, please make sure to set the tools.python_interpreter.url variable in your configuration.yaml",
        category=ToolCategory.Function,
        description="Runs python code in a sandbox.",
    ),
    ToolName.Wiki_Retriever_LangChain: ToolDefinition(
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
        category=ToolCategory.DataLoader,
        description="Retrieves documents from Wikipedia using LangChain.",
    ),
    ToolName.Calculator: ToolDefinition(
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
        category=ToolCategory.Function,
        description="This is a powerful multi-purpose calculator which is capable of a wide array of math calculations.",
    ),
    ToolName.Google_Drive: ToolDefinition(
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
        category=ToolCategory.DataLoader,
        description="Returns a list of relevant document snippets for the user's google drive.",
    ),
    ToolName.Web_Scrape: ToolDefinition(
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
        category=ToolCategory.DataLoader,
        description="Scrape and returns the textual contents of a webpage as a list of passages for a given url.",
    ),
    ToolName.Tavily_Web_Search: ToolDefinition(
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
        category=ToolCategory.WebSearch,
        description="Returns a list of relevant document snippets for a textual query retrieved from the internet.",
    ),
    ToolName.Google_Web_Search: ToolDefinition(
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
        category=ToolCategory.WebSearch,
        description="Returns relevant results by performing a Google web search.",
    ),
    ToolName.Brave_Web_Search: ToolDefinition(
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
        category=ToolCategory.WebSearch,
        description="Returns a list of relevant document snippets for a textual query retrieved from the internet using Brave Search.",
    ),
    ToolName.Hybrid_Web_Search: ToolDefinition(
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
        tool.name = tool.implementation.ID

    enabled_tools = Settings().tools.enabled_tools
    if enabled_tools is not None and len(enabled_tools) > 0:
        tools = {key: value for key, value in tools.items() if key in enabled_tools}
    return tools
