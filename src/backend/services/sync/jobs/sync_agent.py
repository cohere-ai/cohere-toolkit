from backend.config.tools import ToolName
from backend.crud.agent import get_agent_by_id
from backend.crud.agent_tool_metadata import get_all_agent_tool_metadata_by_agent_id
from backend.database_models.database import get_session
from backend.schemas.agent import Agent, AgentToolMetadata
from backend.services.sync import app
from backend.services.sync.constants import DEFAULT_TIME_OUT
from backend.tools.google_drive import GoogleDrive


@app.task(time_limit=DEFAULT_TIME_OUT)
def sync_agent(agent_id: str):
    """
    sync_agent is a job that aims to one time sync the remote artifact with Compass
    Once that job is complete, future jobs will be purely about recent activity (sync_agent_activity)
    """
    agent_tool_metadata = []
    with next(get_session()) as session:
        agent = get_agent_by_id(session, agent_id, override_user_id=True)
        agent_schema = Agent.model_validate(agent)
        agent_tool_metadata = get_all_agent_tool_metadata_by_agent_id(session, agent_id)
        agent_tool_metadata_schema = [
            AgentToolMetadata.model_validate(x) for x in agent_tool_metadata
        ]
        for metadata in agent_tool_metadata_schema:
            match metadata.tool_name:
                case ToolName.Google_Drive:
                    GoogleDrive.handle_agent_creation(session, agent_schema, metadata)
                case _:
                    continue
