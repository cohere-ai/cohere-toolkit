import time

from backend.config.settings import Settings
from backend.services.compass import Compass
from backend.services.logger.utils import LoggerFactory
from backend.services.sync import app
from backend.services.sync.constants import DEFAULT_TIME_OUT, Status
from backend.tools.google_drive.sync.actions.utils import (
    check_if_file_exists_in_artifact,
    get_file_details,
    list_permissions,
)
from .utils import init_compass, persist_agent_task

ACTION_NAME = "permission_change"
logger = LoggerFactory().get_logger()


@app.task(time_limit=DEFAULT_TIME_OUT, bind=True)
@persist_agent_task
def permission_change(
    file_id: str, index_name: str, user_id: str, agent_id: str, **kwargs
):
    # check if file exists
    # NOTE Important when a file has a move and permission_change action
    artifact_id = kwargs["artifact_id"]
    file_details = get_file_details(file_id=file_id, user_id=user_id, just_title=True)
    if file_details is None:
        err_msg = f"empty file details for file_id: {file_id}"
        raise Exception(err_msg)

    title = file_details["title"]
    exists = check_if_file_exists_in_artifact(
        file_id=file_id,
        artifact_id=artifact_id,
        user_id=user_id,
        title=title,
    )
    if not exists:
        err_msg = f"{file_id} does not exist agent_id"
        raise Exception(err_msg)

    permissions = list_permissions(file_id=file_id, user_id=user_id)
    compass = init_compass()

    # Update permissions array
    logger.info(
        event="[Google Drive Permission Change] Initiating Compass add_context action for file",
        file_id=file_id,
    )
    try:
        compass.invoke(
            compass.ValidActions.ADD_CONTEXT,
            {
                "index": index_name,
                "file_id": file_id,
                "context": {
                    "last_updated": int(time.time()),
                    "permissions": permissions,
                },
            },
        )
        logger.info(
            event="[Google Drive Permission Change] Finished Compass add_context action for file",
            file_id=file_id,
        )
        return {
            "action": ACTION_NAME,
            "status": Status.SUCCESS.value,
            "file_id": file_id,
        }
    except Exception as error:
        logger.error(
            event="Failed to update permissions in Compass for file",
            user_id=user_id,
            agent_id=agent_id,
            index_name=index_name,
            file_id=file_id,
        )
        err_msg = f"Error updating permissions for file {file_id} on Compass: {error}"
        raise Exception(err_msg)
