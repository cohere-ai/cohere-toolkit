from enum import Enum

from backend.schemas.tool import ToolDefinition
from community.tools import (
    ArxivRetriever,
    ClinicalTrials,
    ConnectorRetriever,
    LlamaIndexUploadPDFRetriever,
    PubMedRetriever,
    WolframAlpha,
)


class CommunityTool(Enum):
    Arxiv = ArxivRetriever
    Connector = ConnectorRetriever
    Pub_Med = PubMedRetriever
    File_Upload_LlamaIndex = LlamaIndexUploadPDFRetriever
    Wolfram_Alpha = WolframAlpha
    ClinicalTrials = ClinicalTrials


def get_community_tools() -> dict[str, ToolDefinition]:
    # Get list of implementations from Tool Enum
    tool_classes = [tool.value for tool in CommunityTool]
    # Generate dictionary of ToolDefinitions keyed by Tool ID
    community_tools = {
        tool.ID: tool.get_tool_definition() for tool in tool_classes
    }

    return community_tools
