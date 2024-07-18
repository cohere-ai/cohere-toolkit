from concurrent import futures
from typing import Any, Dict, List

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from sqlalchemy.orm import Session

from backend.database_models.agent import Agent

from .auth import GoogleDriveAuth
from .constants import ACTIVITY_TRACKING_WINDOW, GoogleDriveActions
from .utils import get_current_timestamp_in_ms


def query_google_drive_activity(
    session: Session, agent: Agent, agent_artifacts: List[Dict[str, str]]
):
    user_id = agent.user_id
    g_auth = GoogleDriveAuth()
    agent_creator_auth_token = g_auth.get_token(session=session, user_id=user_id)
    if agent_creator_auth_token is None:
        raise Exception("Sync GDrive Error: No agent creator credentials found")

    creds = Credentials(agent_creator_auth_token)
    service = build("driveactivity", "v2", credentials=creds)

    activity_ts_filter = get_current_timestamp_in_ms(
        negative_offset=ACTIVITY_TRACKING_WINDOW
    )
    activities = []
    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures_list = [
            executor.submit(_get_activity, service, artifact, activity_ts_filter)
            for artifact in agent_artifacts
        ]
        for future in futures.as_completed(futures_list):
            try:
                activities.append(future.result())
            except Exception as e:
                raise e

    return {
        agent_artifacts[index]["id"]: activities[index]
        for index in range(len(activities))
    }


def _get_activity(
    service: Any,
    artifact: Dict[str, str],
    activity_ts_filter: int,
    next_page_token: str = "",
):
    artifact_id = artifact["id"]
    artifact_type = artifact["type"]
    response = (
        service.activity()
        .query(
            body={
                "filter": "time >= {}".format(activity_ts_filter),
                **(
                    {"ancestorName": "items/{}".format(artifact_id)}
                    if artifact_type == "folder"
                    else {}
                ),
                **(
                    {"itemName": "items/{}".format(artifact_id)}
                    if artifact_type == "file"
                    else {}
                ),
                "pageToken": next_page_token,
                # "consolidationStrategy": {
                #     "legacy": {},
                # },
            }
        )
        .execute()
    )
    if response_next_page_token := response.get("nextPageToken", None):
        print("response_next_page_token:", response_next_page_token)
        return [
            *response["activities"],
            *_get_activity(
                service=service,
                artifact=artifact,
                activity_ts_filter=activity_ts_filter,
                next_page_token=response_next_page_token,
            ),
        ]
    return response["activities"] if response else []


def handle_google_drive_activity_event(event: GoogleDriveActions):
    match event.value:
        case GoogleDriveActions.CREATE.value:
            pass
        case GoogleDriveActions.EDIT:
            pass
        case GoogleDriveActions.MOVE.value:
            pass
        case GoogleDriveActions.RENAME.value:
            pass
        case GoogleDriveActions.DELETE.value:
            pass
        case GoogleDriveActions.RESTORE.value:
            pass
        case GoogleDriveActions.PERMISSION_CHANGE.value:
            pass
        case _:
            raise Exception("This action is not tracked in Google Drive")
