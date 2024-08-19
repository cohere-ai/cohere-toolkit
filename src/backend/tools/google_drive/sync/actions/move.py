from backend.config.settings import Settings
from backend.services.compass import Compass
from backend.services.logger.utils import LoggerFactory
from backend.services.sync import app
from backend.services.sync.constants import DEFAULT_TIME_OUT, Status
from backend.tools.google_drive.sync.actions.utils import (
    check_if_file_exists_in_artifact,
    get_file_details,
)
from .utils import persist_agent_task

ACTION_NAME = "move"
logger = LoggerFactory().get_logger()


@app.task(time_limit=DEFAULT_TIME_OUT, bind=True)
@persist_agent_task
def move(file_id: str, index_name: str, user_id: str, agent_id: str, **kwargs):
    artifact_id = kwargs["artifact_id"]
    if artifact_id == file_id:
        return {
            "action": ACTION_NAME,
            "status": Status.CANCELLED.value,
            "file_id": file_id,
        }

    file_details = get_file_details(file_id=file_id, user_id=user_id, just_title=True)
    if file_details is None:
        err_msg = f"empty file details for file_id: {file_id}"
        raise Exception(err_msg)

    file_meta = file_details.copy()
    del file_meta["file_bytes"]

    title = file_details["title"]
    exists = check_if_file_exists_in_artifact(
        file_id=file_id,
        artifact_id=artifact_id,
        user_id=user_id,
        title=title,
    )
    compass = Compass(
        compass_api_url=Settings().compass.api_url,
        compass_parser_url=Settings().compass.parser_url,
        compass_username=Settings().compass.username,
        compass_password=Settings().compass.password,
    )
    if exists:
        return {
            "action": ACTION_NAME,
            "status": Status.CANCELLED.value,
            "file_id": file_id,
        }

    # Delete file if moved out of agent's artifacts
    try:
        logger.info(
            event="[Google Drive Move] Initiating Compass delete action for file_id",
            file_id=file_id,
        )
        compass.invoke(
            compass.ValidActions.DELETE,
            {
                "index": index_name,
                "file_id": file_id,
            },
        )
        logger.info(
            event="[Google Drive Move] Finished Compass delete action for file_id",
            file_id=file_id,
        )
        return {
            "action": ACTION_NAME,
            "status": Status.SUCCESS.value,
            "file_id": file_id,
            **file_meta,
        }
    except Exception as error:
        logger.error(
            event="Failed to delete document in Compass",
            user_id=user_id,
            index_name=index_name,
            file_id=file_id,
            agent_id=agent_id,
        )
        err_msg = f"Error deleting file {file_id} on Compass: {error}"
        raise Exception(err_msg)
