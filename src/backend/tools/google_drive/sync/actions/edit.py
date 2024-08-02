import time

from backend.services.logger.utils import LoggerFactory
from backend.services.sync import app
from backend.services.sync.constants import DEFAULT_TIME_OUT, Status
from backend.services.sync.env import env
from backend.tools.google_drive.sync.actions.utils import get_file_details

ACTION_NAME = "edit"
logger = LoggerFactory().get_logger()


@app.task(time_limit=DEFAULT_TIME_OUT)
def edit(file_id: str, index_name: str, user_id: str, **kwargs):
    # Get file bytes, web view link, title
    file_details = get_file_details(file_id=file_id, user_id=user_id)
    if file_details is None:
        return {
            "action": ACTION_NAME,
            "status": Status.CANCELLED.value,
            "file_id": file_id,
        }

    file_bytes, web_view_link, extension = (
        file_details[key] for key in ("file_bytes", "web_view_link", "extension")
    )
    if not file_bytes:
        return {
            "action": ACTION_NAME,
            "status": Status.FAIL.value,
            "message": "File bytes could not be parsed.",
            "file_id": file_id,
        }

    # take compass action
    try:
        # Update doc
        logger.info(
            event="[Google Drive Edit] Initiating Compass update action for file",
            web_view_link=web_view_link,
        )
        env().COMPASS.invoke(
            env().COMPASS.ValidActions.UPDATE,
            {
                "index": index_name,
                "file_id": file_id,
                "file_bytes": file_bytes,
                "file_extension": extension,
            },
        )
        logger.info(
            event="[Google Drive Edit] Finished Compass update action for file",
            web_view_link=web_view_link,
        )
        logger.info(
            event="[Google Drive Edit] Initiating Compass add context for file",
            web_view_link=web_view_link,
        )
        # Update last_updated
        env().COMPASS.invoke(
            env().COMPASS.ValidActions.ADD_CONTEXT,
            {
                "index": index_name,
                "file_id": file_id,
                "context": {
                    "last_updated": int(time.time()),
                },
            },
        )
        logger.info(
            event="[Google Drive Edit] Finished Compass add context action for file",
            web_view_link=web_view_link,
        )
    except Exception:
        logger.info(
            event="[Google Drive Edit] Failed to edit document in Compass for file",
            web_view_link=web_view_link,
        )
        return {"action": ACTION_NAME, "status": Status.FAIL.value, "file_id": file_id}

    return {"action": ACTION_NAME, "status": Status.SUCCESS.value, "file_id": file_id}
