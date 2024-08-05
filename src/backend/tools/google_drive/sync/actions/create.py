import time

from backend.services.logger.utils import LoggerFactory
from backend.services.sync import app
from backend.services.sync.constants import DEFAULT_TIME_OUT, Status
from backend.services.sync.env import env
from backend.tools.google_drive.sync.actions.utils import (
    check_if_file_exists_in_artifact,
    get_file_details,
)

ACTION_NAME = "create"
logger = LoggerFactory().get_logger()


@app.task(time_limit=DEFAULT_TIME_OUT)
def create(file_id: str, index_name: str, user_id: str, **kwargs):
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
    if not kwargs.get("skip_file_exists"):
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
    file_details = get_file_details(
        file_id=file_id, user_id=user_id, include_permissions=True
    )
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

    # take compass action
    try:
        # idempotent create index
        logger.info(
            event="[Google Drive Create] Initiating Compass create_index action for index",
            index_name=index_name,
        )
        env().COMPASS.invoke(
            env().COMPASS.ValidActions.CREATE_INDEX,
            {
                "index": index_name,
            },
        )
        logger.info(
            event="[Google Drive Create] Finished Compass create_index action for index",
            index_name=index_name,
        )
        # Create or replace doc (if already exists)
        logger.info(
            event="[Google Drive Create] Initiating Compass create action for file",
            web_view_link=web_view_link,
        )
        env().COMPASS.invoke(
            env().COMPASS.ValidActions.CREATE,
            {
                "index": index_name,
                "file_id": file_id,
                "file_bytes": file_bytes,
                "file_extension": extension,
            },
        )
        logger.info(
            event="[Google Drive Create] Finished Compass create action for file",
            web_view_link=web_view_link,
        )
        logger.info(
            event="[Google Drive Create] Initiating Compass add context for file",
            web_view_link=web_view_link,
        )
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
                    "permissions": permissions,
                },
            },
        )
        logger.info(
            event="[Google Drive Create] Finished Compass add context action for file",
            web_view_link=web_view_link,
        )
    except Exception as error:
        logger.error(
            event="Failed to create document in Compass for file",
            web_view_link=web_view_link,
        )
        return {
            "action": ACTION_NAME,
            "status": Status.FAIL.value,
            "file_id": file_id,
            "message": str(error),
        }

    return {"action": ACTION_NAME, "status": Status.SUCCESS.value, "file_id": file_id}
