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
from backend.tools.slack.constants import SLACK_TOOL_ID
from backend.tools.utils.mixins import ToolAuthenticationCacheMixin

logger = LoggerFactory().get_logger()


class SlackAuth(BaseToolAuthentication, ToolAuthenticationCacheMixin):
    TOOL_ID = SLACK_TOOL_ID
    AUTH_ENDPOINT = "https://slack.com/oauth/v2/authorize"
    TOKEN_ENDPOINT = "https://slack.com/api/oauth.v2.access"
    EXCHANGE_ENDPOINT = "https://slack.com/api/oauth.v2.exchange"
    DEFAULT_BOT_SCOPES = ['search:read.public']
    DEFAULT_USER_SCOPES = ['search:read']

    def __init__(self):
        super().__init__()

        self.SLACK_CLIENT_ID = Settings().get('tools.slack.client_id')
        self.SLACK_CLIENT_SECRET = Settings().get('tools.slack.client_secret')
        self.USER_SCOPES = Settings().get('tools.slack.user_scopes') or self.DEFAULT_USER_SCOPES
        self.REDIRECT_URL = f"{self.BACKEND_HOST}/v1/tool/auth"

        if any([
            self.SLACK_CLIENT_ID is None,
            self.SLACK_CLIENT_SECRET is None
        ]):
            raise ValueError(
                "SLACK_CLIENT_ID and SLACK_CLIENT_SECRET must be set to use Slack Tool Auth."
            )

    def get_auth_url(self, user_id: str) -> str:
        key = self.insert_tool_auth_cache(user_id, self.TOOL_ID)
        state = {"key": key}

        params = {
            "client_id": self.SLACK_CLIENT_ID,
            "user_scope": " ".join(self.USER_SCOPES or []),
            "redirect_uri": self.REDIRECT_URL,
            "state": json.dumps(state),
        }

        return f"{self.AUTH_ENDPOINT}?{urllib.parse.urlencode(params)}"

    def retrieve_auth_token(
        self, request: Request, session: DBSessionDep, user_id: str
    ) -> str:
        if request.query_params.get("error"):
            error = request.query_params.get("error") or "Unknown error"
            logger.error(event=f"[Slack Tool] Auth token error: {error}.")
            return error

        body = {
            "code": request.query_params.get("code"),
            "client_id": self.SLACK_CLIENT_ID,
            "client_secret": self.SLACK_CLIENT_SECRET,
        }

        url_encoded_body = urllib.parse.urlencode(body)
        headers = {
            "Content-Type": 'application/x-www-form-urlencoded',
        }
        response = requests.post(self.TOKEN_ENDPOINT, data=url_encoded_body, headers=headers)

        response_body = response.json()

        if response.status_code != 200 or response_body.get("ok") is False:
            logger.error(
                event=f"[Slack Tool] Error retrieving auth token: {response_body}"
            )
            return str(response)

        token_data = response_body.get("authed_user", None)

        if token_data is None:
            logger.error(
                event=f"[Slack Tool] Error retrieving auth token: {response_body}"
            )
            return str(response)

        tool_auth_crud.create_tool_auth(
            session,
            ToolAuthModel(
                user_id=user_id,
                tool_id=self.TOOL_ID,
                token_type=token_data.get("token_type"),
                encrypted_access_token=encrypt(token_data.get("access_token")),
                encrypted_refresh_token=encrypt(token_data.get("refresh_token")),
                expires_at=datetime.datetime.now()
                + datetime.timedelta(seconds=token_data.get("expires_in")),
            ),
        )

        return ""

    def try_refresh_token(self, session: DBSessionDep, user_id: str, tool_auth: ToolAuth) -> bool:
        body = {
            "client_id": self.SLACK_CLIENT_ID,
            "client_secret": self.SLACK_CLIENT_SECRET,
            "refresh_token": tool_auth.refresh_token,
            "grant_type": "refresh_token",
        }
        headers = {
            "Content-Type": 'application/x-www-form-urlencoded',
        }
        url_encoded_body = urllib.parse.urlencode(body)

        response = requests.post(self.TOKEN_ENDPOINT, data=url_encoded_body, headers=headers)
        response_body = response.json()

        if response.status_code != 200 or response_body.get("ok") is False:
            logger.error(
                event=f"[Slack Tool] Error refreshing token: {response_body}"
            )
            return False

        token_data = response_body.get("authed_user", None)
        if token_data is None:
            logger.error(
                event=f"[Slack Tool] Error retrieving auth token: {response_body}"
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
                token_type=token_data.get("token_type"),
                encrypted_access_token=encrypt(token_data.get("access_token")),
                encrypted_refresh_token=encrypt(token_data.get("refresh_token")),
                expires_at=datetime.datetime.now()
                           + datetime.timedelta(seconds=token_data.get("expires_in")),
            ),
        )

        return True
