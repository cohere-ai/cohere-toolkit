import datetime
import json
import os
import urllib.parse
from typing import Any, Dict, List

import requests
from fastapi import HTTPException, Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from backend.crud import tool_auth as tool_auth_crud
from backend.database_models.database import DBSessionDep
from backend.database_models.tool_auth import ToolAuth
from backend.services.auth.crypto import encrypt
from backend.services.logger import get_logger
from backend.tools.base import BaseTool, BaseToolAuthentication

logger = get_logger()


class GoogleDrive(BaseTool):
    """
    Experimental (In development): Tool that searches Google Drive
    """

    NAME = "google_drive"

    @classmethod
    def is_available(cls) -> bool:
        return True

    def call(self, parameters: dict, **kwargs: Any) -> List[Dict[str, Any]]:
        auth = tool_auth_crud.get_tool_auth(
            kwargs.get("session"), self.NAME, kwargs.get("user_id")
        )

        if not auth:
            error_message = f"Could not find ToolAuth with tool_id: {self.NAME} and user_id: {kwargs.get('user_id')}"
            logger.error(error_message)
            raise HTTPException(status_code=401, detail=error_message)

        # TODO: Improve the getting of files
        query = parameters.get("query", "")
        conditions = [
            "("
            + " or ".join(
                [
                    f"mimeType = '{mime_type}'"
                    for mime_type in [
                        "application/vnd.google-apps.document",
                        "application/vnd.google-apps.spreadsheet",
                        "application/vnd.google-apps.presentation",
                    ]
                ]
            )
            + ")",
            "("
            + " or ".join([f"fullText contains '{word}'" for word in [query]])
            + ")",
        ]
        q = " and ".join(conditions)

        try:
            creds = Credentials(auth.access_token)
            service = build("drive", "v3", credentials=creds)
            results = (
                service.files()
                .list(pageSize=10, q=q, fields="nextPageToken, files(id, name)")
                .execute()
            )
            items = results.get("files", [])

            return [dict({"text": item["name"]}) for item in items]
        except Exception as e:
            error_message = (
                f"Could not query GoogleDrive tool with q: {q} and auth: {str(auth)}."
            )
            logger.error(error_message)
            raise HTTPException(status_code=401, detail=error_message)


class GoogleDriveAuth(BaseToolAuthentication):
    GOOGLE_DRIVE_CLIENT_ID = os.getenv("GOOGLE_DRIVE_CLIENT_ID")
    GOOGLE_DRIVE_CLIENT_SECRET = os.getenv("GOOGLE_DRIVE_CLIENT_SECRET")
    TOOL_ID = GoogleDrive.NAME
    AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"

    def __init__(self):
        if any(
            [
                self.GOOGLE_DRIVE_CLIENT_ID is None,
                self.GOOGLE_DRIVE_CLIENT_SECRET is None,
                self.BACKEND_HOST is None,
            ]
        ):
            raise ValueError(
                "GOOGLE_DRIVE_CLIENT_ID, GOOGLE_DRIVE_CLIENT_SECRET and NEXT_PUBLIC_API_HOSTNAME must be set to use Google Drive Tool Auth."
            )

    def get_auth_url(self, user_id: str) -> str:
        redirect_uri = f"{self.BACKEND_HOST}/v1/tool/auth"

        state = {"user_id": user_id, "tool_id": self.TOOL_ID}

        # Query parameters
        params = {
            "response_type": "code",
            "client_id": self.GOOGLE_DRIVE_CLIENT_ID,
            "scope": "https://www.googleapis.com/auth/drive",
            "redirect_uri": redirect_uri,
            "prompt": "select_account consent",
            "state": json.dumps(state),
            "access_type": "offline",
            "include_granted_scopes": "true",
        }

        return f"{self.AUTH_ENDPOINT}?{urllib.parse.urlencode(params)}"

    def is_auth_required(self, session: DBSessionDep, user_id: str) -> bool:
        auth = tool_auth_crud.get_tool_auth(session, self.TOOL_ID, user_id)

        if auth is None:
            return True

        if datetime.datetime.now() > auth.expires_at:
            if self.try_refresh_token(session, user_id, auth):
                # Refreshed token successfully
                return False

            # Refresh failed, delete existing Auth
            tool_auth_crud.delete_tool_auth(session, self.TOOL_ID, user_id)
            return True

        # ToolAuth retrieved and is not expired
        return False

    def try_refresh_token(
        self, session: DBSessionDep, user_id: str, tool_auth: ToolAuth
    ) -> bool:
        body = {
            "client_id": self.GOOGLE_DRIVE_CLIENT_ID,
            "client_secret": self.GOOGLE_DRIVE_CLIENT_SECRET,
            "refresh_token": tool_auth.refresh_token,
            "grant_type": "refresh_token",
        }

        response = requests.post(self.TOKEN_ENDPOINT, json=body)
        response_body = response.json()

        if response.status_code != 200:
            logger.error(
                f"Error while refreshing token with GoogleDriveAuth: {response_body}"
            )
            return False

        existing_tool_auth = tool_auth_crud.get_tool_auth(
            session, self.TOOL_ID, user_id
        )
        tool_auth_crud.update_tool_auth(
            session,
            existing_tool_auth,
            ToolAuth(
                token_type=response_body["token_type"],
                encrypted_access_token=encrypt(response_body["access_token"]),
                expires_at=datetime.datetime.now()
                + datetime.timedelta(seconds=response_body["expires_in"]),
            ),
        )

        return True

    def retrieve_auth_token(self, request: Request, session: DBSessionDep) -> str:
        if request.query_params.get("error"):
            error = request.query_params.get("error")
            logger.error(
                f"Error from Google OAuth provider while retrieving Google Auth token: {error}."
            )
            return error

        state = json.loads(request.query_params.get("state"))
        redirect_url = f"{self.BACKEND_HOST}/v1/tool/auth"
        body = {
            "code": request.query_params.get("code"),
            "client_id": self.GOOGLE_DRIVE_CLIENT_ID,
            "client_secret": self.GOOGLE_DRIVE_CLIENT_SECRET,
            "redirect_uri": redirect_url,
            "grant_type": "authorization_code",
        }

        response = requests.post(self.TOKEN_ENDPOINT, json=body)
        response_body = response.json()

        if response.status_code != 200:
            logger.error(
                f"Error while retrieving auth token with GoogleDriveAuth: {response_body}"
            )
            return response

        import pdb

        pdb.set_trace()
        tool_auth_crud.create_tool_auth(
            session,
            ToolAuth(
                user_id=state["user_id"],
                tool_id=self.TOOL_ID,
                token_type=response_body["token_type"],
                encrypted_access_token=encrypt(response_body["access_token"]),
                encrypted_refresh_token=encrypt(response_body["refresh_token"]),
                expires_at=datetime.datetime.now()
                + datetime.timedelta(seconds=response_body["expires_in"]),
            ),
        )
