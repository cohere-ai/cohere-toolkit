import os
from distutils.util import strtobool
from enum import StrEnum

from backend.schemas.tool import Category, ManagedTool
from backend.tools.function_tools import (
    CalculatorFunctionTool,
    PythonInterpreterFunctionTool,
)
from backend.tools.retrieval import (
    ArxivRetriever,
    LangChainVectorDBRetriever,
    LangChainWikiRetriever,
    LlamaIndexUploadPDFRetriever,
    PubMedRetriever,
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
    File_Upload_LlamaIndex = "File Reader - LlamaIndex"
    Python_Interpreter = "Python_Interpreter"
    Calculator = "Calculator"
    Tavily_Internet_Search = "Internet Search"
    Arxiv = "Arxiv"
    Pub_Med = "Pub Med"


ALL_TOOLS = {
    ToolName.Wiki_Retriever_LangChain: ManagedTool(
        name=ToolName.Wiki_Retriever_LangChain,
        implementation=LangChainWikiRetriever,
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
        is_visible=True,
        is_available=LangChainVectorDBRetriever.is_available(),
        error_message="LangChainVectorDBRetriever not available, please make sure to set the COHERE_API_KEY environment variable.",
        category=Category.FileLoader,
        description="Retrieves documents from a file using LangChain.",
    ),
    ToolName.File_Upload_LlamaIndex: ManagedTool(
        name=ToolName.File_Upload_LlamaIndex,
        implementation=LlamaIndexUploadPDFRetriever,
        is_visible=False,
        is_available=LlamaIndexUploadPDFRetriever.is_available(),
        error_message="LlamaIndexUploadPDFRetriever not available.",
        category=Category.FileLoader,
        description="Retrieves documents from a file using LlamaIndex.",
    ),
    ToolName.Python_Interpreter: ManagedTool(
        name=ToolName.Python_Interpreter,
        implementation=PythonInterpreterFunctionTool,
        parameter_definitions={
            "code": {
                "description": "Python code to execute using an interpreter",
                "type": "str",
                "required": True,
            }
        },
        is_visible=True,
        is_available=PythonInterpreterFunctionTool.is_available(),
        error_message="PythonInterpreterFunctionTool not available, please make sure to set the PYTHON_INTERPRETER_URL environment variable.",
        category=Category.Function,
        description="Runs python code in a sandbox.",
    ),
    ToolName.Calculator: ManagedTool(
        name=ToolName.Calculator,
        implementation=CalculatorFunctionTool,
        parameter_definitions={
            "code": {
                "description": "Arithmetic expression to evaluate",
                "type": "str",
                "required": True,
            }
        },
        is_visible=True,
        is_available=CalculatorFunctionTool.is_available(),
        error_message="CalculatorFunctionTool not available.",
        category=Category.Function,
        description="Evaluate arithmetic expressions.",
    ),
    ToolName.Tavily_Internet_Search: ManagedTool(
        name=ToolName.Tavily_Internet_Search,
        implementation=TavilyInternetSearch,
        is_visible=True,
        is_available=TavilyInternetSearch.is_available(),
        error_message="TavilyInternetSearch not available, please make sure to set the TAVILY_API_KEY environment variable.",
        category=Category.DataLoader,
        description="Returns a list of relevant document snippets for a textual query retrieved from the internet using Tavily.",
    ),
    ToolName.Arxiv: ManagedTool(
        name=ToolName.Arxiv,
        implementation=ArxivRetriever,
        is_visible=True,
        is_available=ArxivRetriever.is_available(),
        error_message="ArxivRetriever not available.",
        category=Category.DataLoader,
        description="Retrieves documents from Arxiv.",
    ),
    ToolName.Pub_Med: ManagedTool(
        name=ToolName.Pub_Med,
        implementation=PubMedRetriever,
        is_visible=True,
        is_available=PubMedRetriever.is_available(),
        error_message="PubMedRetriever not available.",
        category=Category.DataLoader,
        description="Retrieves documents from Pub Med.",
    ),
}

# Langchain tools are all functional tools and must have to_langchain_tool() method defined
LANGCHAIN_TOOLS = {
    key: value
    for key, value in ALL_TOOLS.items()
    if key in [ToolName.Python_Interpreter, ToolName.Tavily_Internet_Search]
}

USE_LANGCHAIN = bool(strtobool(os.getenv("USE_EXPERIMENTAL_LANGCHAIN", "False")))
if USE_LANGCHAIN:
    AVAILABLE_TOOLS = LANGCHAIN_TOOLS
else:
    AVAILABLE_TOOLS = ALL_TOOLS
