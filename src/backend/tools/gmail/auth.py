import datetime
import json
import urllib.parse

import requests
from fastapi import Request

from backend.config.settings import Settings
from backend.crud import tool_auth as tool_auth_crud
from backend.database_models.database import DBSessionDep
from backend.database_models.tool_auth import ToolAuth as ToolAuthModel
from backend.schemas.tool_auth import UpdateToolAuth
from backend.services.auth.crypto import encrypt
from backend.services.logger.utils import LoggerFactory
from backend.tools.base import BaseToolAuthentication
from backend.tools.gmail.constants import GMAIL_TOOL_ID
from backend.tools.utils.mixins import ToolAuthenticationCacheMixin

logger = LoggerFactory().get_logger()


class GmailAuth(BaseToolAuthentication, ToolAuthenticationCacheMixin):
    TOOL_ID = GMAIL_TOOL_ID
    AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
    DEFAULT_USER_SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

    def __init__(self):
        super().__init__()

        self.GMAIL_CLIENT_ID = Settings().get("tools.gmail.client_id")
        self.GMAIL_CLIENT_SECRET = Settings().get("tools.gmail.client_secret")
        self.REDIRECT_URL = f"{self.BACKEND_HOST}/v1/tool/auth"
        self.USER_SCOPES = Settings().get("tools.gmail.user_scopes") or self.DEFAULT_USER_SCOPES

        if any([
            self.GMAIL_CLIENT_ID is None,
            self.GMAIL_CLIENT_SECRET is None
        ]):
            raise ValueError(
                "GMAIL_CLIENT_ID and GMAIL_CLIENT_SECRET must be set to use Gmail Tool Auth."
            )

    def get_auth_url(self, user_id: str) -> str:
        key = self.insert_tool_auth_cache(user_id, self.TOOL_ID)
        state = {"key": key}

        params = {
            "response_type": "code",
            "client_id": self.GMAIL_CLIENT_ID,
            "scope": " ".join(self.USER_SCOPES or []),
            "redirect_uri": self.REDIRECT_URL,
            "prompt": "select_account consent",
            "state": json.dumps(state),
            "access_type": "offline",
            "include_granted_scopes": "true",
        }

        return f"{self.AUTH_ENDPOINT}?{urllib.parse.urlencode(params)}"

    def retrieve_auth_token(
        self, request: Request, session: DBSessionDep, user_id: str
    ) -> str:
        if request.query_params.get("error"):
            error = request.query_params.get("error") or "Unknown error"
            logger.error(event=f"[Gmail Tool] Auth token error: {error}.")
            return error

        body = {
            "code": request.query_params.get("code"),
            "client_id": self.GMAIL_CLIENT_ID,
            "client_secret": self.GMAIL_CLIENT_SECRET,
            "redirect_uri": self.REDIRECT_URL,
            "grant_type": "authorization_code",
        }

        response = requests.post(self.TOKEN_ENDPOINT, json=body)
        response_body = response.json()

        if response.status_code != 200:
            logger.error(
                event=f"[Gmail] Error retrieving auth token: {response_body}"
            )
            return ""

        tool_auth_crud.create_tool_auth(
            session,
            ToolAuthModel(
                user_id=user_id,
                tool_id=self.TOOL_ID,
                token_type=response_body["token_type"],
                encrypted_access_token=encrypt(response_body["access_token"]),
                encrypted_refresh_token=encrypt(response_body["refresh_token"]),
                expires_at=datetime.datetime.now()
                + datetime.timedelta(seconds=response_body["expires_in"]),
            ),
        )

        return ""

    def try_refresh_token(
        self, session: DBSessionDep, user_id: str, tool_auth: ToolAuthModel
    ) -> bool:
        body = {
            "client_id": self.GMAIL_CLIENT_ID,
            "client_secret": self.GMAIL_CLIENT_SECRET,
            "refresh_token": tool_auth.refresh_token,
            "grant_type": "refresh_token",
        }

        response = requests.post(self.TOKEN_ENDPOINT, json=body)
        response_body = response.json()

        if response.status_code != 200:
            logger.error(
                event=f"[Gmail] Error refreshing token: {response_body}"
            )
            return False

        existing_tool_auth = tool_auth_crud.get_tool_auth(
            session, self.TOOL_ID, user_id
        )
        tool_auth_crud.update_tool_auth(
            session,
            existing_tool_auth,
            UpdateToolAuth(
                user_id=user_id,
                tool_id=self.TOOL_ID,
                token_type=response_body["token_type"],
                encrypted_access_token=encrypt(response_body["access_token"]),
                encrypted_refresh_token=tool_auth.encrypted_refresh_token,
                expires_at=datetime.datetime.now()
                + datetime.timedelta(seconds=response_body["expires_in"]),
            ),
        )

        return True
