import time

from backend.config.settings import Settings
from backend.services.compass import Compass
from backend.services.logger.utils import LoggerFactory
from backend.services.sync import app
from backend.services.sync.constants import DEFAULT_TIME_OUT, Status
from backend.tools.google_drive.sync.actions.utils import (
    check_if_file_exists_in_artifact,
    get_file_details,
)

ACTION_NAME = "edit"
logger = LoggerFactory().get_logger()


@app.task(time_limit=DEFAULT_TIME_OUT)
def edit(file_id: str, index_name: str, user_id: str, **kwargs):
    # check if file exists
    # NOTE Important when a file has a move and create action
    artifact_id = kwargs["artifact_id"]
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
    if not exists:
        return {
            "action": ACTION_NAME,
            "status": Status.CANCELLED.value,
            "file_id": file_id,
        }

    # Get file bytes, web view link, title
    file_details = get_file_details(file_id=file_id, user_id=user_id)
    file_bytes, web_view_link, extension, permissions = (
        file_details[key]
        for key in ("file_bytes", "web_view_link", "extension", "permissions")
    )
    if not file_bytes:
        return {
            "action": ACTION_NAME,
            "status": Status.FAIL.value,
            "message": "File bytes could not be parsed.",
            "file_id": file_id,
        }

    compass = Compass(
        compass_api_url=Settings().compass.api_url,
        compass_parser_url=Settings().compass.parser_url,
        compass_username=Settings().compass.username,
        compass_password=Settings().compass.password,
    )
    try:
        # Update doc
        logger.info(
            event="[Google Drive Edit] Initiating Compass update action for file",
            web_view_link=web_view_link,
        )
        compass.invoke(
            compass.ValidActions.UPDATE,
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
        compass.invoke(
            compass.ValidActions.ADD_CONTEXT,
            {
                "index": index_name,
                "file_id": file_id,
                "context": {
                    "url": web_view_link,
                    "title": title,
                    "last_updated": int(time.time()),
                    "permissions": permissions,
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
