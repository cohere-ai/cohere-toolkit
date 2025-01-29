import datetime
import json
import urllib.parse

import requests
from fastapi import Request

from backend.config.settings import Settings
from backend.crud import tool_auth as tool_auth_crud
from backend.database_models import ToolAuth
from backend.database_models.database import DBSessionDep
from backend.database_models.tool_auth import ToolAuth as ToolAuthModel
from backend.schemas.tool_auth import UpdateToolAuth
from backend.services.auth.crypto import encrypt
from backend.services.logger.utils import LoggerFactory
from backend.tools.base import BaseToolAuthentication
from backend.tools.github.constants import GITHUB_TOOL_ID
from backend.tools.utils.mixins import ToolAuthenticationCacheMixin

logger = LoggerFactory().get_logger()


class GithubAuth(BaseToolAuthentication, ToolAuthenticationCacheMixin):
    TOOL_ID = GITHUB_TOOL_ID
    AUTH_ENDPOINT = "https://github.com/login/oauth/authorize"
    TOKEN_ENDPOINT = "https://github.com/login/oauth/access_token"
    DEFAULT_USER_SCOPES = ['public_repo', 'read:org']

    def __init__(self):
        super().__init__()

        self.GITHUB_CLIENT_ID = Settings().get('tools.github.client_id')
        self.GITHUB_CLIENT_SECRET = Settings().get('tools.github.client_secret')
        self.USER_SCOPES = Settings().get('tools.github.user_scopes') or self.DEFAULT_USER_SCOPES
        self.REDIRECT_URL = f"{self.BACKEND_HOST}/v1/tool/auth"

        if any([
            self.GITHUB_CLIENT_ID is None,
            self.GITHUB_CLIENT_SECRET is None
        ]):
            raise ValueError(
                "GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET must be set to use Slack Tool Auth."
            )

    def get_auth_url(self, user_id: str) -> str:
        key = self.insert_tool_auth_cache(user_id, self.TOOL_ID)
        state = {"key": key}

        params = {
            "client_id": self.GITHUB_CLIENT_ID,
            "scope": " ".join(self.USER_SCOPES or []),
            "redirect_uri": self.REDIRECT_URL,
            "state": json.dumps(state),
        }

        return f"{self.AUTH_ENDPOINT}?{urllib.parse.urlencode(params)}"

    def retrieve_auth_token(
        self, request: Request, session: DBSessionDep, user_id: str
    ) -> str:
        if request.query_params.get("error"):
            error = request.query_params.get("error") or "Unknown error"
            logger.error(event=f"[Github Tool] Auth token error: {error}.")
            return error

        body = {
            "code": request.query_params.get("code"),
            "client_id": self.GITHUB_CLIENT_ID,
            "client_secret": self.GITHUB_CLIENT_SECRET,
        }

        url_encoded_body = urllib.parse.urlencode(body)
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }
        response = requests.post(self.TOKEN_ENDPOINT, data=url_encoded_body, headers=headers)

        response_body = response.json()

        if response.status_code != 200:
            logger.error(
                event=f"[Github Tool] Error retrieving auth token: {response_body}"
            )
            return str(response)

        token = response_body.get("access_token", None)
        token_type = response_body.get("token_type", None)
        refresh_token = response_body.get("refresh_token", "")
        expires_in = response_body.get("expires_in", 31536000)

        if token is None:
            logger.error(
                event=f"[Github Tool] Error retrieving auth token: {response_body}"
            )
            return str(response)

        tool_auth_crud.create_tool_auth(
            session,
            ToolAuthModel(
                user_id=user_id,
                tool_id=self.TOOL_ID,
                token_type=token_type,
                encrypted_access_token=encrypt(token),
                encrypted_refresh_token=encrypt(refresh_token),
                expires_at=datetime.datetime.now()
                + datetime.timedelta(seconds=expires_in)
            ),
        )

        return ""

    def try_refresh_token(self, session: DBSessionDep, user_id: str, tool_auth: ToolAuth) -> bool:
        body = {
            "client_id": self.GITHUB_CLIENT_ID,
            "client_secret": self.GITHUB_CLIENT_SECRET,
            "refresh_token": tool_auth.refresh_token,
            "grant_type": "refresh_token",
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }

        url_encoded_body = urllib.parse.urlencode(body)
        response = requests.post(self.TOKEN_ENDPOINT, data=url_encoded_body, headers=headers)
        response_body = response.json()

        if response.status_code != 200:
            logger.error(
                event=f"[GITHUB Tool] Error refreshing token: {response_body}"
            )
            return False

        token = response_body.get("access_token", None)
        token_type = response_body.get("token_type", None)
        refresh_token = response_body.get("refresh_token", "")
        expires_in = response_body.get("expires_in", 31536000)

        if token is None:
            logger.error(
                event=f"[GITHUB Tool] Error retrieving auth token: {response_body}"
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
                token_type=token_type,
                encrypted_access_token=encrypt(token),
                encrypted_refresh_token=encrypt(refresh_token),
                expires_at=datetime.datetime.now()
                           + datetime.timedelta(seconds=expires_in),
            ),
        )

        return True
