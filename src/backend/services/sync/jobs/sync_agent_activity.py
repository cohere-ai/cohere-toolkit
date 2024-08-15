from backend.config.tools import ToolName
from backend.crud.agent import get_agent_by_id
from backend.crud.agent_tool_metadata import get_all_agent_tool_metadata_by_agent_id
from backend.database_models.database import get_session
from backend.services.logger.utils import LoggerFactory
from backend.services.sync import app
from backend.services.sync.constants import DEFAULT_TIME_OUT
from backend.tools.google_drive import (
    handle_google_drive_activity_event,
    query_google_drive_activity,
)
from backend.tools.google_drive.sync.consolidation import consolidate

logger = LoggerFactory().get_logger()


@app.task(time_limit=DEFAULT_TIME_OUT)
def sync_agent_activity(agent_id: str):
    """
    sync_agent_activity is a job that aims to sync Compass with the agent artifacts recent activity
    """
    agent_tool_metadata = []
    session = next(get_session())
    agent = get_agent_by_id(session, agent_id, override_user_id=True)
    agent_tool_metadata = get_all_agent_tool_metadata_by_agent_id(session, agent_id)
    for metadata in agent_tool_metadata:
        try:
            match metadata.tool_name:
                case ToolName.Google_Drive:
                    activities = query_google_drive_activity(
                        session=session,
                        user_id=agent.user_id,
                        agent_artifacts=metadata.artifacts,
                    )
                    session.close()

                    consolidated_activities = {
                        key: consolidate(activities=value)
                        for key, value in activities.items()
                    }
                    logger.info(
                        event=f"Publishing {sum([len(x) for x in consolidated_activities.values()])} activity tasks for agent {agent_id}"
                    )
                    for artifact_id, activity in consolidated_activities.items():
                        for activity_item in activity:
                            event_type = list(
                                activity_item["primaryActionDetail"].keys()
                            )[0]
                            # NOTE: This is an unfortunate hack because the Google APi
                            # does not provide consistency over the request and response
                            # format of this action
                            if event_type == "permissionChange":
                                event_type = "permission_change"

                            handle_google_drive_activity_event(
                                event_type=event_type,
                                activity=activity_item,
                                agent_id=agent_id,
                                user_id=agent.user_id,
                                artifact_id=artifact_id,
                            )
                case _:
                    continue
        except Exception as e:
            logger.error(
                event=f"Error syncing agent activity for agent {agent_id}",
                exception=e,
            )
            continue
