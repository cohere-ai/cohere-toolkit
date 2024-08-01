import time

from backend.services.logger.utils import logger
from backend.services.sync import app
from backend.services.sync.constants import DEFAULT_TIME_OUT, Status
from backend.services.sync.env import env

ACTION_NAME = "rename"


@app.task(time_limit=DEFAULT_TIME_OUT)
def rename(file_id: str, index_name: str, user_id: str, **kwargs):
    title = kwargs["title"]

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
