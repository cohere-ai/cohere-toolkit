from backend.config.settings import Settings
from backend.services.compass import Compass
from backend.services.logger.utils import LoggerFactory
from backend.services.sync import app
from backend.services.sync.constants import DEFAULT_TIME_OUT, Status
from backend.tools.google_drive.sync.actions.utils import (
    check_if_file_exists_in_artifact,
    get_file_details,
)

ACTION_NAME = "move"
logger = LoggerFactory().get_logger()


@app.task(time_limit=DEFAULT_TIME_OUT)
def move(file_id: str, index_name: str, user_id: str, **kwargs):
    artifact_id = kwargs["artifact_id"]
    if artifact_id == file_id:
        return {
            "action": ACTION_NAME,
            "status": Status.CANCELLED.value,
            "file_id": file_id,
        }

    file_details = get_file_details(file_id=file_id, user_id=user_id, just_title=True)
    if file_details is None:
        return {
            "action": ACTION_NAME,
            "status": Status.CANCELLED.value,
            "file_id": file_id,
        }

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

    # Delete file if moved out of agent's artifacts
    if not exists:
        # Delete document
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
        }

    return {"action": ACTION_NAME, "status": Status.CANCELLED.value, "file_id": file_id}
