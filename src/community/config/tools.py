from enum import StrEnum

from community.tools import (
    ArxivRetriever,
    ToolCategory,
    ClinicalTrials,
    ConnectorRetriever,
    LlamaIndexUploadPDFRetriever,
    ToolDefinition,
    PubMedRetriever,
    WolframAlpha,
)


class CommunityToolName(StrEnum):
    Arxiv = ArxivRetriever.ID
    Connector = ConnectorRetriever.ID
    Pub_Med = PubMedRetriever.ID
    File_Upload_LlamaIndex = LlamaIndexUploadPDFRetriever.ID
    Wolfram_Alpha = WolframAlpha.ID
    ClinicalTrials = ClinicalTrials.ID


COMMUNITY_TOOLS = {
    CommunityToolName.Arxiv: ToolDefinition(
        display_name="Arxiv",
        implementation=ArxivRetriever,
        parameter_definitions={
            "query": {
                "description": "Query for retrieval.",
                "type": "str",
                "required": True,
            }
        },
        is_visible=True,
        is_available=ArxivRetriever.is_available(),
        error_message="ArxivRetriever is not available.",
        category=ToolCategory.DataLoader,
        description="Retrieves documents from Arxiv.",
    ),
    CommunityToolName.Connector: ToolDefinition(
        display_name="Example Connector",
        implementation=ConnectorRetriever,
        is_visible=True,
        is_available=ConnectorRetriever.is_available(),
        error_message="ConnectorRetriever is not available.",
        category=ToolCategory.DataLoader,
        description="Connects to a data source.",
    ),
    CommunityToolName.Pub_Med: ToolDefinition(
        display_name="PubMed",
        implementation=PubMedRetriever,
        parameter_definitions={
            "query": {
                "description": "Query for retrieval.",
                "type": "str",
                "required": True,
            }
        },
        is_visible=True,
        is_available=PubMedRetriever.is_available(),
        error_message="PubMedRetriever is not available.",
        category=ToolCategory.DataLoader,
        description="Retrieves documents from Pub Med.",
    ),
    CommunityToolName.File_Upload_LlamaIndex: ToolDefinition(
        display_name="Llama File Reader",
        implementation=LlamaIndexUploadPDFRetriever,
        parameter_definitions={
            "query": {
                "description": "Query for retrieval.",
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
        is_available=LlamaIndexUploadPDFRetriever.is_available(),
        error_message="LlamaIndexUploadPDFRetriever is not available.",
        category=ToolCategory.FileLoader,
        description="Retrieves the most relevant documents from the uploaded files based on the query using Llama Index.",
    ),
    CommunityToolName.Wolfram_Alpha: ToolDefinition(
        display_name="Wolfram Alpha",
        implementation=WolframAlpha,
        is_visible=False,
        is_available=WolframAlpha.is_available(),
        error_message="WolframAlphaFunctionTool is not available, please set tools.wolfram_alpha.app_id in secrets.yaml",
        category=ToolCategory.Function,
        description="Evaluate arithmetic expressions.",
    ),
    CommunityToolName.ClinicalTrials: ToolDefinition(
        display_name="Clinical Trials",
        implementation=ClinicalTrials,
        is_visible=True,
        is_available=ClinicalTrials.is_available(),
        error_message="ClinicalTrialsTool is not available.",
        category=ToolCategory.Function,
        description="Retrieves clinical studies from ClinicalTrials.gov.",
        parameter_definitions={
            "condition": {
                "description": "Filters clinical studies to a specified disease or condition",
                "type": "str",
                "required": False,
            },
            "location": {
                "description": "Filters clinical studies to a specified city, state, or country.",
                "type": "str",
                "required": False,
            },
            "intervention": {
                "description": "Filters clinical studies to a specified drug or treatment.",
                "type": "str",
                "required": False,
            },
            "is_recruiting": {
                "description": "Filters clinical studies to those that are actively recruiting.",
                "type": "bool",
                "required": False,
            },
        },
    ),
}

# For main.py cli setup script
COMMUNITY_TOOLS_SETUP = {
    CommunityToolName.Wolfram_Alpha: {
        "secrets": {
            "WOLFRAM_APP_ID": None,  # default value
        },
    },
}
