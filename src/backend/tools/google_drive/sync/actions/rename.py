import time

from backend.config.settings import Settings
from backend.services.compass import Compass
from backend.services.logger.utils import LoggerFactory
from backend.services.sync import app
from backend.services.sync.constants import DEFAULT_TIME_OUT, Status
from backend.tools.google_drive.sync.actions.utils import get_file_details
from .utils import init_compass, persist_agent_task

ACTION_NAME = "rename"
logger = LoggerFactory().get_logger()


@app.task(time_limit=DEFAULT_TIME_OUT, bind=True)
@persist_agent_task
def rename(file_id: str, index_name: str, user_id: str, agent_id: str, **kwargs):
    file_details = get_file_details(file_id=file_id, user_id=user_id, just_title=True)
    if file_details is None:
        err_msg = f"empty file details for file_id: {file_id}"
        raise Exception(err_msg)

    title = file_details["title"]
    compass = init_compass()

    # Modify title
    logger.info(
        event="[Google Drive Rename] Initiating Compass add context for file",
        file_id=file_id,
    )
    try:
        compass.invoke(
            compass.ValidActions.ADD_CONTEXT,
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
    except Exception as error:
        logger.error(
            event="Failed to rename document in Compass for file",
            user_id=user_id,
            index_name=index_name,
            file_id=file_id,
            agent_id=agent_id,
        )
        err_msg = f"Error renaming file {file_id} on Compass: {error}"
        raise Exception(err_msg)
