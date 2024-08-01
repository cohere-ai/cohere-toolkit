import time

from backend.services.logger.utils import logger
from backend.services.sync import app
from backend.services.sync.constants import DEFAULT_TIME_OUT, Status
from backend.services.sync.env import env
from backend.tools.google_drive.actions.utils import get_file_details

ACTION_NAME = "create"


@app.task(time_limit=DEFAULT_TIME_OUT)
def create(file_id: str, index_name: str, user_id: str, **kwargs):
    # Get file bytes, web view link, title
    file_details = get_file_details(file_id=file_id, user_id=user_id)
    if file_details is None:
        return {
            "action": ACTION_NAME,
            "status": Status.CANCELLED.value,
            "file_id": file_id,
        }

    file_bytes, web_view_link, title, extension = (
        file_details[key]
        for key in ("file_bytes", "web_view_link", "title", "extension")
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
        # idempotent create index
        logger.info(
            "Initiating Compass create_index action for index {}".format(index_name)
        )
        env().COMPASS.invoke(
            env().COMPASS.ValidActions.CREATE_INDEX,
            {
                "index": index_name,
            },
        )
        logger.info(
            "Finished Compass create_index action for index {}".format(index_name)
        )
        logger.info(
            "Initiating Compass create action for file {}".format(web_view_link)
        )
        # Create or replace doc (if already exists)
        env().COMPASS.invoke(
            env().COMPASS.ValidActions.CREATE,
            {
                "index": index_name,
                "file_id": file_id,
                "file_bytes": file_bytes,
                "file_extension": extension,
            },
        )
        logger.info("Finished Compass create action for file {}".format(web_view_link))
        logger.info("Initiating Compass add context for file {}".format(web_view_link))
        # Add title and url context
        env().COMPASS.invoke(
            env().COMPASS.ValidActions.ADD_CONTEXT,
            {
                "index": index_name,
                "file_id": file_id,
                "context": {
                    "url": web_view_link,
                    "title": title,
                    "last_updated": int(time.time()),
                    "permissions": [],
                },
            },
        )
        logger.info(
            "Finished Compass add context action for file {}".format(web_view_link)
        )
    except Exception:
        logger.error(
            "Failed to create document in Compass for file {}".format(web_view_link)
        )
        return {"action": ACTION_NAME, "status": Status.FAIL.value, "file_id": file_id}

    return {"action": ACTION_NAME, "status": Status.SUCCESS.value, "file_id": file_id}
