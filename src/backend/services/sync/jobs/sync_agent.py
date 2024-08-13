from backend.config.tools import ToolName
from backend.crud.agent import get_agent_by_id_sync
from backend.crud.agent_tool_metadata import get_all_agent_tool_metadata_by_agent_id
from backend.database_models.database import get_session
from backend.schemas.agent import Agent, AgentToolMetadata
from backend.services.sync import app
from backend.services.sync.constants import DEFAULT_TIME_OUT
from backend.tools.google_drive import (
    handle_google_drive_sync,
    list_google_drive_artifacts_file_ids,
)


@app.task(time_limit=DEFAULT_TIME_OUT)
def sync_agent(agent_id: str):
    """
    sync_agent is a job that aims to one time sync the remote artifact with Compass
    Once that job is complete, future jobs will be purely about recent activity (sync_agent_activity)
    """
    agent_tool_metadata = []
    session = next(get_session())
    agent = get_agent_by_id_sync(session, agent_id)
    agent_schema = Agent.model_validate(agent)
    agent_tool_metadata = get_all_agent_tool_metadata_by_agent_id(session, agent_id)
    agent_tool_metadata_schema = [
        AgentToolMetadata.model_validate(x) for x in agent_tool_metadata
    ]
    for metadata in agent_tool_metadata_schema:
        match metadata.tool_name:
            case ToolName.Google_Drive:
                file_ids = list_google_drive_artifacts_file_ids(
                    session=session,
                    user_id=agent_schema.user_id,
                    agent_artifacts=metadata.artifacts,
                    verbose=True,
                )
                session.close()
                handle_google_drive_sync(
                    file_ids=file_ids, agent_id=agent_id, user_id=agent_schema.user_id
                )
            case _:
                continue
