from enum import StrEnum

from community.tools import Category, ManagedTool
from community.tools.function_tools import wolfram
from community.tools.retrieval import arxiv, llama_index, pub_med


class ToolName(StrEnum):
    Arxiv = "Arxiv"
    Pub_Med = "Pub Med"
    File_Upload_LlamaIndex = "File Reader - LlamaIndex"
    Wolfram_Alpha = "Wolfram_Alpha"


COMMUNITY_TOOLS = {
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
    ToolName.File_Upload_LlamaIndex: ManagedTool(
        name=ToolName.File_Upload_LlamaIndex,
        implementation=llama_index.LlamaIndexUploadPDFRetriever,
        is_visible=True,
        category=Category.FileLoader,
        description="Retrieves documents from a file using LlamaIndex.",
    ),
    ToolName.Wolfram_Alpha: ManagedTool(
        name=ToolName.Wolfram_Alpha,
        implementation=wolfram.WolframAlphaFunctionTool,
        is_visible=False,
        category=Category.Function,
        description="Evaluate arithmetic expressions.",
    ),
}


COMMUNITY_TOOLS_SETUP = {
    ToolName.Wolfram_Alpha: {
        "secrets": [
            "WOLFRAM_ALPHA_APP_ID",
        ],
    },
}
