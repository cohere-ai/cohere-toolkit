import copy
import os

from dotenv import load_dotenv
from sqlalchemy.orm import Session

from backend.config.tools import ALL_TOOLS, ToolName
from backend.database_models import Agent, AgentTool, Organization, Tool, User
from community.config.tools import COMMUNITY_TOOLS, CommunityToolName

load_dotenv()

tools = copy.deepcopy(ALL_TOOLS)
tools.update(COMMUNITY_TOOLS)


TOOLS_CONFIGS = {
    ToolName.Wiki_Retriever_LangChain: {
        "COHERE_API_KEY": os.environ.get("COHERE_API_KEY") or "",
    },
    ToolName.Search_File: {},
    ToolName.Read_File: {},
    ToolName.Python_Interpreter: {
        "INTERPRETER_URL": os.environ.get("PYTHON_INTERPRETER_URL") or "",
    },
    ToolName.Calculator: {},
    ToolName.Tavily_Internet_Search: {
        "TAVILY_API_KEY": os.environ.get("TAVILY_API_KEY") or "",
    },
    ToolName.Google_Drive: {
        "GOOGLE_DRIVE_CLIENT_ID": os.environ.get("GOOGLE_DRIVE_CLIENT_ID") or "",
        "GOOGLE_DRIVE_CLIENT_SECRET": os.environ.get("GOOGLE_DRIVE_CLIENT_SECRET")
        or "",
    },
    ToolName.Web_Scrape: {},
    CommunityToolName.Pub_Med: {},
    CommunityToolName.Arxiv: {},
    CommunityToolName.Connector: {},
    CommunityToolName.File_Upload_LlamaIndex: {},
    CommunityToolName.Wolfram_Alpha: {
        "WOLFRAM_APP_ID": os.environ.get("WOLFRAM_APP_ID") or "",
    },
    CommunityToolName.ClinicalTrials: {},
}


def seed_tools_data(op):
    """
    Seed default tools and set default tools for default agent.
    """
    session = Session(op.get_bind())
    # Creating tools
    for tool_name, tool in tools.items():
        if tool_name in TOOLS_CONFIGS:
            default_tool_config = TOOLS_CONFIGS[tool_name]
        is_community = isinstance(tool_name, CommunityToolName)
        db_tool = Tool(
            name=str(tool_name),
            display_name=tool.display_name,
            implementation_class_name=(
                tool.implementation.__name__ if tool.implementation else ""
            ),
            description=tool.description,
            parameter_definitions=tool.parameter_definitions,
            kwargs=tool.kwargs,
            default_tool_config=default_tool_config,
            is_visible=tool.is_visible,
            is_community=is_community,
            auth_implementation_class_name=(
                tool.auth_implementation.__name__ if tool.auth_implementation else ""
            ),
            error_message_text=tool.error_message,
            category=tool.category,
        )
        session.add(db_tool)
        session.commit()

    # assign tools to default agent
    default_agent = session.query(Agent).filter_by(id="default").first()
    all_tools = session.query(Tool).all()
    for tool in all_tools:
        if tool.name in [
            "web_search",
            "search_file",
            "read_document",
            "toolkit_python_interpreter",
            "toolkit_calculator",
            "wikipedia",
            "google_drive",
            "arxiv",
            "example_connector",
            "pub_med",
            "file_reader_llamaindex",
            "wolfram_alpha",
            "clinical_trials",
        ]:
            association = AgentTool(
                agent_id=default_agent.id,
                tool_id=tool.id,
                tool_config=tool.default_tool_config,
            )
            session.add(association)
    session.commit()


def delete_tools_data(op):
    """
    Delete deployments and models.
    """
    session = Session(op.get_bind())
    session.query(Tool).delete()
    session.commit()
