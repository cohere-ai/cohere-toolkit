import time

from backend.services.logger.utils import LoggerFactory
from backend.services.sync import app
from backend.services.sync.constants import DEFAULT_TIME_OUT, Status
from backend.services.sync.env import env
from backend.tools.google_drive.sync.actions.utils import get_file_details

ACTION_NAME = "rename"
logger = LoggerFactory().get_logger()


@app.task(time_limit=DEFAULT_TIME_OUT)
def rename(file_id: str, index_name: str, user_id: str, **kwargs):
    file_details = get_file_details(file_id=file_id, user_id=user_id, just_title=True)
    if file_details is None:
        return {
            "action": ACTION_NAME,
            "status": Status.CANCELLED.value,
            "file_id": file_id,
        }

    title = file_details["title"]

    # Modify title
    logger.info(
        event="[Google Drive Rename] Initiating Compass add context for file",
        file_id=file_id,
    )
    env().COMPASS.invoke(
        env().COMPASS.ValidActions.ADD_CONTEXT,
        {
            "index": index_name,
            "file_id": file_id,
            "context": {
                "title": title,
                "last_updated": int(time.time()),
            },
        },
    )
    logger.info(
        event="[Google Drive Rename] Finished Compass add context action for file",
        file_id=file_id,
    )
    return {
        "action": ACTION_NAME,
        "status": Status.SUCCESS.value,
        "file_id": file_id,
    }
