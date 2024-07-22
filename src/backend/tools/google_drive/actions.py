from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from backend.database_models.database import db_sessionmaker
from backend.services.logger import get_logger
from backend.services.sync import app
from backend.services.sync.constants import DEFAULT_TIME_OUT
from backend.services.sync.env import env
from backend.tools.utils import download

from .auth import GoogleDriveAuth
from .constants import NATIVE_SEARCH_MIME_TYPES, GoogleDriveActions, Status
from .utils import (
    extract_export_link,
    extract_title,
    extract_web_view_link,
    perform_native_single,
    perform_non_native_single,
    process_shortcut_file,
)

logger = get_logger()


@app.task(time_limit=DEFAULT_TIME_OUT)
def create(event_type: str, file_id: str, index_name: str, user_id: str):
    # Get google credentials for create and edit events
    creds = None
    if event_type in [GoogleDriveActions.CREATE.value, GoogleDriveActions.EDIT.value]:
        gdrive_auth = GoogleDriveAuth()
        agent_creator_auth_token = None

        with db_sessionmaker() as session, session.begin():
            agent_creator_auth_token = gdrive_auth.get_token(
                session=session, user_id=user_id
            )
            if agent_creator_auth_token is None:
                raise Exception("Sync GDrive Error: No agent creator credentials found")

            if gdrive_auth.is_auth_required(session, user_id=user_id):
                raise Exception(
                    "Sync GDrive Error: Agent creator credentials need to re-authenticate"
                )

        creds = Credentials(agent_creator_auth_token)

    service = build("drive", "v3", credentials=creds, cache_discovery=False)

    file_get = perform_native_single(file_id=file_id, creds=creds)
    if file_get["trashed"]:
        # # Delete file if trashed
        # logger.info("Initiating Compass delete action for file {}".format(file_id))
        # compass.invoke(
        #     compass.ValidActions.DELETE,
        #     {
        #         "index": index_name,
        #         "file_id": file_id,
        #     },
        # )
        # logger.info("Finished Compass delete action for file {}".format(file_id))
        return {"action": "create", "status": Status.CANCELLED.value}

    processed_file = process_shortcut_file(service, file_get)
    web_view_link = extract_web_view_link(processed_file)
    title = extract_title(file_get)

    file_text = ""
    if processed_file["mimeType"] in NATIVE_SEARCH_MIME_TYPES:
        # native files
        export_link = extract_export_link(processed_file)
        if export_link:
            file_text = download.perform_single(
                httpx_client=env().HTTPX_CLIENT,
                url=export_link,
                access_token=creds.token,
            )
    else:
        # non-native files
        file_text = perform_non_native_single(
            service=service, file_id=processed_file["id"]
        )

    if not file_text:
        return {
            "action": "create",
            "status": Status.FAIL.value,
            "message": "File text is empty or could not be parsed.",
            "file_id": file_id,
        }

    try:
        # idempotent create index
        logger.info("Initiating Compass create action for file {}".format(file_id))
        env().COMPASS.invoke(
            env().COMPASS.ValidActions.CREATE_INDEX,
            {
                "index": index_name,
            },
        )
        # Create or replace doc (if already exists)
        env().COMPASS.invoke(
            env().COMPASS.ValidActions.CREATE,
            {
                "index": index_name,
                "file_id": file_id,
                "file_text": file_text,
            },
        )
        logger.info("Finished Compass create action for file {}".format(file_id))
    except Exception as e:
        logger.error("Failed to create document in Compass: {}".format(str(e)))
        return {"action": "create", "status": Status.FAIL.value, "file_id": file_id}

    return {"action": "create", "status": Status.SUCCESS.value, "file_id": file_id}
