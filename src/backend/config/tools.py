import os
from distutils.util import strtobool
from enum import StrEnum

from backend.schemas.tool import Category, ManagedTool
from backend.tools.function_tools import calculator, python_interpreter
from backend.tools.retrieval import arxiv, lang_chain, llama_index, pub_med, tavily

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


use_langchain = bool(strtobool(os.getenv("USE_EXPERIMENTAL_LANGCHAIN", "false")))

COHERE_DEPLOYMENT_TOOLS = {
    ToolName.Wiki_Retriever_LangChain: ManagedTool(
        name=ToolName.Wiki_Retriever_LangChain,
        implementation=lang_chain.LangChainWikiRetriever,
        kwargs={"chunk_size": 300, "chunk_overlap": 0},
        is_visible=True,
        category=Category.DataLoader,
        description="Retrieves documents from Wikipedia using LangChain.",
    ),
    ToolName.File_Upload_Langchain: ManagedTool(
        name=ToolName.File_Upload_Langchain,
        implementation=lang_chain.LangChainVectorDBRetriever,
        is_visible=True,
        category=Category.FileLoader,
        description="Retrieves documents from a file using LangChain.",
    ),
    ToolName.File_Upload_LlamaIndex: ManagedTool(
        name=ToolName.File_Upload_LlamaIndex,
        implementation=llama_index.LlamaIndexUploadPDFRetriever,
        is_visible=False,
        category=Category.FileLoader,
        description="Retrieves documents from a file using LlamaIndex.",
    ),
    ToolName.Python_Interpreter: ManagedTool(
        name=ToolName.Python_Interpreter,
        implementation=python_interpreter.PythonInterpreterFunctionTool,
        parameter_definitions={
            "code": {
                "description": "Python code to execute using an interpreter",
                "type": "str",
                "required": True,
            }
        },
        is_visible=True,
        category=Category.Function,
        description="Runs python code in a sandbox.",
    ),
    ToolName.Calculator: ManagedTool(
        name=ToolName.Calculator,
        implementation=calculator.CalculatorFunctionTool,
        parameter_definitions={
            "code": {
                "description": "Arithmetic expression to evaluate",
                "type": "str",
                "required": True,
            }
        },
        is_visible=True,
        category=Category.Function,
        description="Evaluate arithmetic expressions.",
    ),
    ToolName.Tavily_Internet_Search: ManagedTool(
        name=ToolName.Tavily_Internet_Search,
        implementation=tavily.TavilyInternetSearch,
        is_visible=True,
        category=Category.DataLoader,
        description="Returns a list of relevant document snippets for a textual query retrieved from the internet using Tavily.",
    ),
    ToolName.Arxiv: ManagedTool(
        name=ToolName.Arxiv,
        implementation=arxiv.ArxivRetriever,
        is_visible=True,
        category=Category.DataLoader,
        description="Retrieves documents from Arxiv.",
    ),
    ToolName.Pub_Med: ManagedTool(
        name=ToolName.Pub_Med,
        implementation=pub_med.PubMedRetriever,
        is_visible=True,
        category=Category.DataLoader,
        description="Retrieves documents from Pub Med.",
    ),
}

# Langchain tools are all functional tools and must have to_langchain_tool() method defined
LANGCHAIN_TOOLS = {
    ToolName.Python_Interpreter: ManagedTool(
        name=ToolName.Python_Interpreter,
        implementation=python_interpreter.PythonInterpreterFunctionTool,
        is_visible=True,
        description="Runs python code in a sandbox.",
    ),
    ToolName.Tavily_Internet_Search: ManagedTool(
        name=ToolName.Tavily_Internet_Search,
        implementation=tavily.TavilyInternetSearch,
        is_visible=True,
        description="Returns a list of relevant document snippets for a textual query retrieved from the internet using Tavily.",
    ),
}

if use_langchain:
    AVAILABLE_TOOLS = LANGCHAIN_TOOLS
else:
    AVAILABLE_TOOLS = COHERE_DEPLOYMENT_TOOLS
