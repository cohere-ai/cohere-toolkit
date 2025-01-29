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
from backend.tools.sharepoint.constants import SHAREPOINT_TOOL_ID
from backend.tools.utils.mixins import ToolAuthenticationCacheMixin

logger = LoggerFactory().get_logger()


class SharepointAuth(BaseToolAuthentication, ToolAuthenticationCacheMixin):
    TOOL_ID = SHAREPOINT_TOOL_ID
    AUTH_ENDPOINT = "https://login.microsoftonline.com"
    SCOPES = [
        "offline_access",
        "https://graph.microsoft.com/.default",
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.REDIRECT_URL = f"{self.BACKEND_HOST}/v1/tool/auth"

        self.SHAREPOINT_TENANT_ID = Settings().get('tools.sharepoint.tenant_id')
        self.SHAREPOINT_CLIENT_ID = Settings().get('tools.sharepoint.client_id')
        self.SHAREPOINT_CLIENT_SECRET = Settings().get('tools.sharepoint.client_secret')

        if not any([self.SHAREPOINT_TENANT_ID, self.SHAREPOINT_CLIENT_ID, self.SHAREPOINT_CLIENT_SECRET]):
            raise ValueError(
                "SHAREPOINT_TENANT_ID, SHAREPOINT_CLIENT_ID and SHAREPOINT_CLIENT_SECRET must be set to use Sharepoint Tool Auth."
            )

    def get_auth_url(self, user_id: str) -> str:
        key = self.insert_tool_auth_cache(user_id, self.TOOL_ID)
        state = {"key": key}

        params = {
            "response_type": "code",
            "client_id": self.SHAREPOINT_CLIENT_ID,
            "scope": " ".join(self.SCOPES or []),
            "redirect_uri": self.REDIRECT_URL,
            "prompt": "select_account",
            "state": json.dumps(state),
        }

        return f"{self.AUTH_ENDPOINT}/{self.SHAREPOINT_TENANT_ID}/oauth2/v2.0/authorize?{urllib.parse.urlencode(params)}"

    def retrieve_auth_token(
        self, request: Request, session: DBSessionDep, user_id: str
    ) -> str|None:
        url = f"{self.AUTH_ENDPOINT}/{self.SHAREPOINT_TENANT_ID}/oauth2/v2.0/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        code = request.query_params.get("code", "")
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "scope": " ".join(self.SCOPES),
            "redirect_uri": self.REDIRECT_URL,
            "client_id": self.SHAREPOINT_CLIENT_ID,
            "client_secret": self.SHAREPOINT_CLIENT_SECRET,
        }

        error_message = "Error retrieving access token from Sharepoint Tool"
        try:
            response = requests.post(url, data=payload, headers=headers)
            body = response.json()
        except Exception as exc:
            logger.error(event=f"[Sharepoint] Auth token error: {exc}")
            return error_message
        if not response.ok:
            error = body.get("error")
            error_description = body.get("error_description")
            error_message = f"{error_message}: {error}. {error_description}"
            logger.error(event=f"[Sharepoint] Auth token error: {error_message}")
            return error_message

        tool_auth_crud.create_tool_auth(
            session,
            ToolAuthModel(
                user_id=user_id,
                tool_id=self.TOOL_ID,
                token_type=body["token_type"],
                encrypted_access_token=encrypt(body["access_token"]),
                encrypted_refresh_token=encrypt(body["refresh_token"]),
                expires_at=datetime.datetime.now()
                + datetime.timedelta(seconds=int(body["expires_in"])),
            ),
        )

    def try_refresh_token(
        self, session: DBSessionDep, user_id: str, tool_auth: ToolAuthModel
    ) -> bool:
        url = f"{self.AUTH_ENDPOINT}/{self.SHAREPOINT_TENANT_ID}/oauth2/v2.0/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": tool_auth.refresh_token,
            "scope": " ".join(self.SCOPES),
            "client_id": self.SHAREPOINT_CLIENT_ID,
            "client_secret": self.SHAREPOINT_CLIENT_SECRET,
        }

        error_message = "Error retrieving refreshing token from Sharepoint Tool"
        try:
            response = requests.post(url, data=payload, headers=headers)
            body = response.json()
        except Exception as exc:
            logger.error(event=f"[Sharepoint] Auth token error: {exc}")
            return False
        if not response.ok:
            error = body.get("error")
            error_description = body.get("error_description")
            error_message = f"{error_message}: {error}. {error_description}"
            logger.error(event=f"[Sharepoint] Auth token error: {error_message}")
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
                token_type=body["token_type"],
                encrypted_access_token=encrypt(body["access_token"]),
                encrypted_refresh_token=encrypt(body["refresh_token"]),
                expires_at=datetime.datetime.now()
                + datetime.timedelta(seconds=body["expires_in"]),
            ),
        )
        return True
