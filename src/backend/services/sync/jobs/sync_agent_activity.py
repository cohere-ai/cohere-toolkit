from backend.config.tools import ToolName
from backend.crud.agent import get_agent_by_id
from backend.crud.agent_tool_metadata import get_all_agent_tool_metadata_by_agent_id
from backend.database_models.database import get_session
from backend.services.logger.utils import LoggerFactory
from backend.services.sync import app
from backend.services.sync.constants import DEFAULT_TIME_OUT
from backend.tools.google_drive import GoogleDrive

logger = LoggerFactory().get_logger()


@app.task(time_limit=DEFAULT_TIME_OUT)
def sync_agent_activity(agent_id: str):
    """
    sync_agent_activity is a job that aims to sync Compass with the agent artifacts recent activity
    """
    agent_tool_metadata = []
    with next(get_session()) as session:
        agent = get_agent_by_id(session, agent_id, override_user_id=True)
        agent_tool_metadata = get_all_agent_tool_metadata_by_agent_id(session, agent_id)
        for metadata in agent_tool_metadata:
            try:
                match metadata.tool_name:
                    case ToolName.Google_Drive:
                        GoogleDrive.handle_activity_sync(session, agent, metadata)
                    case _:
                        continue
            except Exception as e:
                logger.error(
                    event=f"Error syncing agent activity for agent {agent_id}",
                    exception=e,
                )
                continue
