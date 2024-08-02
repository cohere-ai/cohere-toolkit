from backend.services.logger.utils import LoggerFactory
from backend.services.sync import app
from backend.services.sync.constants import DEFAULT_TIME_OUT, Status
from backend.services.sync.env import env

ACTION_NAME = "delete"
logger = LoggerFactory().get_logger()


@app.task(time_limit=DEFAULT_TIME_OUT)
def delete(file_id: str, index_name: str, user_id: str, **kwargs):
    # Delete document
    logger.info(
        event="[Google Drive Delete] Initiating Compass delete for file",
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
        event="[Google Drive Delete] Finished Compass delete action for file",
        file_id=file_id,
    )
    return {
        "action": ACTION_NAME,
        "status": Status.SUCCESS.value,
        "file_id": file_id,
    }
