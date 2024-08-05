from backend.services.logger.utils import LoggerFactory
from backend.services.sync import app
from backend.services.sync.constants import DEFAULT_TIME_OUT, Status
from backend.services.sync.env import env
from backend.tools.google_drive.sync.actions.utils import (
    check_if_file_exists_in_artifact,
    get_file_details,
)

ACTION_NAME = "move"
logger = LoggerFactory().get_logger()


@app.task(time_limit=DEFAULT_TIME_OUT)
def move(file_id: str, index_name: str, user_id: str, **kwargs):
    artifact_id = kwargs["artifact_id"]
    title = get_file_details(file_id=file_id, user_id=user_id, just_title=True)["title"]
    exists = check_if_file_exists_in_artifact(
        file_id=file_id,
        artifact_id=artifact_id,
        user_id=user_id,
        title=title,
    )

    # Delete file if moved out of agent's artifacts
    if not exists:
        # Delete document
        logger.info(
            event="[Google Drive Move] Initiating Compass delete action for file_id",
            file_id=file_id,
        )
        env().COMPASS.invoke(
            env().COMPASS.ValidActions.DELETE,
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
