import time

from backend.services.compass import get_compass
from backend.services.logger.utils import LoggerFactory
from backend.services.sync import app
from backend.services.sync.constants import DEFAULT_TIME_OUT, Status
from backend.tools.google_drive.sync.actions.utils import (
    check_if_file_exists_in_artifact,
    get_file_details,
)
from backend.tools.google_drive.sync.utils import persist_agent_task

ACTION_NAME = "create"
logger = LoggerFactory().get_logger()


@app.task(time_limit=DEFAULT_TIME_OUT, bind=True)
@persist_agent_task
def create(self, file_id: str, index_name: str, user_id: str, agent_id: str, **kwargs):
    # check if file exists
    # NOTE Important when a file has a move and create action
    artifact_id = kwargs["artifact_id"]
    file_details = get_file_details(file_id=file_id, user_id=user_id, just_title=True)
    if file_details is None:
        err_msg = f"empty file details for file_id: {file_id}"
        raise Exception(err_msg)

    title = file_details["title"]
    if not kwargs.get("skip_file_exists"):
        exists = check_if_file_exists_in_artifact(
            file_id=file_id,
            artifact_id=artifact_id,
            user_id=user_id,
            title=title,
        )
        if not exists:
            err_msg = f"{file_id} does not exist agent_id"
            raise Exception(err_msg)

    # Get file bytes, web view link, title
    file_details = get_file_details(
        file_id=file_id, user_id=user_id, include_permissions=True
    )
    if not file_details:
        err_msg = f"Error creating file {file_id} with link on Compass. File details could not be parsed"
        raise Exception(err_msg)
    file_bytes, web_view_link, extension, permissions = (
        file_details[key]
        for key in ("file_bytes", "web_view_link", "extension", "permissions")
    )
    if not file_bytes:
        err_msg = f"Error creating file {file_id} with link: {web_view_link} on Compass. File bytes could not be parsed"
        raise Exception(err_msg)

    file_meta = file_details.copy()
    del file_meta["file_bytes"]

    compass = get_compass()
    try:
        # idempotent create index
        logger.info(
            event="[Google Drive Create] Initiating Compass create_index action for index",
            index_name=index_name,
        )
        compass.invoke(
            compass.ValidActions.CREATE_INDEX,
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
        compass.invoke(
            compass.ValidActions.CREATE,
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
            event="[Google Drive Create] Finished Compass add context action for file",
            web_view_link=web_view_link,
        )
    except Exception as error:
        logger.info(
            event="[Google Drive Create] Errors indexing on compass",
            web_view_link=web_view_link,
            error=str(error),
        )
        err_msg = f"Error creating file {file_id} with link: {web_view_link} on Compass: {error}"
        raise Exception(err_msg)

    action_name = kwargs.get("action_name_override", ACTION_NAME)
    return {
        "action": action_name,
        "status": Status.SUCCESS.value,
        "file_id": file_id,
        **file_meta,
    }
