import logging
import os
from distutils.util import strtobool
from enum import StrEnum

from backend.schemas.tool import Category, ManagedTool
from backend.tools import (
    Calculator,
    LangChainVectorDBRetriever,
    LangChainWikiRetriever,
    PythonInterpreter,
    TavilyInternetSearch,
)

"""
List of available tools. Each tool should have a name, implementation, is_visible and category. 
They can also have kwargs if necessary.

You can switch the visibility of a tool by changing the is_visible parameter to True or False. 
If a tool is not visible, it will not be shown in the frontend.

If you want to add a new tool, check the instructions on how to implement a retriever in the documentation.
Don't forget to add the implementation to this AVAILABLE_TOOLS dictionary!
"""


class ToolName(StrEnum):
    Wiki_Retriever_LangChain = "Wikipedia"
    File_Upload_Langchain = "File Reader"
    Python_Interpreter = "Python_Interpreter"
    Calculator = "Calculator"
    Tavily_Internet_Search = "Internet Search"


ALL_TOOLS = {
    ToolName.Wiki_Retriever_LangChain: ManagedTool(
        name=ToolName.Wiki_Retriever_LangChain,
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
    ToolName.File_Upload_Langchain: ManagedTool(
        name=ToolName.File_Upload_Langchain,
        implementation=LangChainVectorDBRetriever,
        parameter_definitions={
            "query": {
                "description": "Query for retrieval.",
                "type": "str",
                "required": True,
            }
        },
        is_visible=True,
        is_available=LangChainVectorDBRetriever.is_available(),
        error_message="LangChainVectorDBRetriever not available, please make sure to set the COHERE_API_KEY environment variable.",
        category=Category.FileLoader,
        description="Retrieves documents from a file using LangChain.",
    ),
    ToolName.Python_Interpreter: ManagedTool(
        name=ToolName.Python_Interpreter,
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
        error_message="PythonInterpreterFunctionTool not available, please make sure to set the PYTHON_INTERPRETER_URL environment variable.",
        category=Category.Function,
        description="Runs python code in a sandbox.",
    ),
    ToolName.Calculator: ManagedTool(
        name=ToolName.Calculator,
        implementation=Calculator,
        parameter_definitions={
            "code": {
                "description": "Arithmetic expression to evaluate",
                "type": "str",
                "required": True,
            }
        },
        is_visible=True,
        is_available=Calculator.is_available(),
        error_message="Calculator tool not available.",
        category=Category.Function,
        description="Evaluate arithmetic expressions.",
    ),
    ToolName.Tavily_Internet_Search: ManagedTool(
        name=ToolName.Tavily_Internet_Search,
        implementation=TavilyInternetSearch,
        parameter_definitions={
            "query": {
                "description": "Query for retrieval.",
                "type": "str",
                "required": True,
            }
        },
        is_visible=True,
        is_available=TavilyInternetSearch.is_available(),
        error_message="TavilyInternetSearch not available, please make sure to set the TAVILY_API_KEY environment variable.",
        category=Category.DataLoader,
        description="Returns a list of relevant document snippets for a textual query retrieved from the internet using Tavily.",
    ),
}


def get_available_tools() -> dict[ToolName, dict]:
    langchain_tools = [ToolName.Python_Interpreter, ToolName.Tavily_Internet_Search]
    use_langchain_tools = bool(
        strtobool(os.getenv("USE_EXPERIMENTAL_LANGCHAIN", "False"))
    )
    use_community_tools = bool(strtobool(os.getenv("USE_COMMUNITY_FEATURES", "False")))

    if use_langchain_tools:
        return {
            key: value for key, value in ALL_TOOLS.items() if key in langchain_tools
        }

    if use_community_tools:
        try:
            from community.config.tools import COMMUNITY_TOOLS

            tools = ALL_TOOLS.copy()
            tools.update(COMMUNITY_TOOLS)
            return tools
        except ImportError:
            logging.warning("Community tools are not available. Skipping.")

    return ALL_TOOLS


AVAILABLE_TOOLS = get_available_tools()
