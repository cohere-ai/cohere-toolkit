import datetime
import json
import os
import urllib.parse

import requests
from fastapi import Request

from backend.crud import tool_auth as tool_auth_crud
from backend.database_models.database import DBSessionDep
from backend.database_models.tool_auth import ToolAuth
from backend.schemas.tool_auth import UpdateToolAuth
from backend.services.logger import get_logger
from backend.tools.base import BaseToolAuthentication
from backend.tools.google_drive.tool import GoogleDrive

from .constants import SCOPES

logger = get_logger()


class GoogleDriveAuth(BaseToolAuthentication):
    @classmethod
    def get_auth_url(cls, user_id: str) -> str:
        if not os.getenv("GOOGLE_DRIVE_CLIENT_ID"):
            raise ValueError("GOOGLE_DRIVE_CLIENT_ID not set")
        redirect_url = os.getenv(
            "NEXT_PUBLIC_API_HOSTNAME"
        ) + "/v1/tool/auth?redirect_url={}/new?p=t".format(
            os.getenv("FRONTEND_HOSTNAME")
        )
        base_url = "https://accounts.google.com/o/oauth2/v2/auth?"

        # TODO:Create token and insert to redis
        state = {"user_id": user_id, "tool_id": GoogleDrive.NAME}
        params = {
            "response_type": "code",
            "client_id": os.getenv("GOOGLE_DRIVE_CLIENT_ID"),
            "scope": " ".join(SCOPES),
            "redirect_uri": redirect_url,
            "prompt": "select_account consent",
            "state": json.dumps(state),
            "access_type": "offline",
            "include_granted_scopes": "true",
        }
        return base_url + urllib.parse.urlencode(params)

    @classmethod
    def is_auth_required(cls, session: DBSessionDep, user_id: str) -> bool:
        auth = tool_auth_crud.get_tool_auth(session, GoogleDrive.NAME, user_id)
        if auth is None:
            return True
        if auth.expires_at < datetime.datetime.now():
            if cls.try_refresh_token(session, user_id, auth):
                return False  # Refreshed token successfully
            tool_auth_crud.delete_tool_auth(session, GoogleDrive.NAME, user_id)
            return True
        return False

    def try_refresh_token(
        session: DBSessionDep, user_id: str, tool_auth: ToolAuth
    ) -> bool:
        if not os.getenv("GOOGLE_DRIVE_CLIENT_ID") or not os.getenv(
            "GOOGLE_DRIVE_CLIENT_SECRET"
        ):
            raise ValueError(
                "GOOGLE_DRIVE_CLIENT_ID or GOOGLE_DRIVE_CLIENT_SECRET not set"
            )
        url = "https://oauth2.googleapis.com/token"
        body = {
            "client_id": os.getenv("GOOGLE_DRIVE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_DRIVE_CLIENT_SECRET"),
            "refresh_token": tool_auth.encrypted_refresh_token.decode(),
            "grant_type": "refresh_token",
        }
        res = requests.post(url, json=body)
        res_body = res.json()
        if res.status_code != 200:
            logger.error(f"Error in google drive auth: {res_body}")
            return False
        tool_auth_crud.update_tool_auth(
            session,
            tool_auth,
            UpdateToolAuth(
                user_id=user_id,
                tool_id=GoogleDrive.NAME,
                token_type=res_body["token_type"],
                encrypted_access_token=str.encode(
                    res_body["access_token"]
                ),  # TODO: Better storage of token
                encrypted_refresh_token=tool_auth.encrypted_refresh_token,
                expires_at=datetime.datetime.now()
                + datetime.timedelta(seconds=res_body["expires_in"]),
            ),
        )
        return True

    @classmethod
    def process_auth_token(cls, request: Request, session: DBSessionDep) -> str:
        if not os.getenv("GOOGLE_DRIVE_CLIENT_ID") or not os.getenv(
            "GOOGLE_DRIVE_CLIENT_SECRET" or not os.getenv("NEXT_PUBLIC_API_HOSTNAME")
        ):
            raise ValueError(
                "GOOGLE_DRIVE_CLIENT_ID or GOOGLE_DRIVE_CLIENT_SECRET not set"
            )
        if request.query_params.get("error"):
            err = request.query_params.get("error")
            logger.error(f"Error in google drive auth: {err}")
            return err
        state = json.loads(request.query_params.get("state"))
        redirect_url = os.getenv(
            "NEXT_PUBLIC_API_HOSTNAME"
        ) + "/v1/tool/auth?redirect_url={}/new?p=t".format(
            os.getenv("FRONTEND_HOSTNAME")
        )
        url = "https://oauth2.googleapis.com/token"
        body = {
            "code": request.query_params.get("code"),
            "client_id": os.getenv("GOOGLE_DRIVE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_DRIVE_CLIENT_SECRET"),
            "redirect_uri": redirect_url,
            "grant_type": "authorization_code",
        }
        res = requests.post(url, json=body)
        res_body = res.json()
        if res.status_code != 200:
            logger.error(f"Error in google drive auth: {res_body}")
            return res_body

        try:
            tool_auth_crud.get_tool_auth(
                db=session, tool_id=GoogleDrive.NAME, user_id=state["user_id"]
            )
            tool_auth_crud.delete_tool_auth(
                db=session, user_id=state["user_id"], tool_id=GoogleDrive.NAME
            )
        except Exception as _e:
            pass

        tool_auth_crud.create_tool_auth(
            session,
            ToolAuth(
                user_id=state["user_id"],
                tool_id=GoogleDrive.NAME,
                token_type=res_body["token_type"],
                encrypted_access_token=str.encode(
                    res_body["access_token"]
                ),  # TODO: Better storage of token
                encrypted_refresh_token=str.encode(
                    res_body["refresh_token"]
                ),  # TODO: Better storage of token
                expires_at=datetime.datetime.now()
                + datetime.timedelta(seconds=res_body["expires_in"]),
            ),
        )

    @classmethod
    def get_token(cls, session: DBSessionDep, user_id: str) -> str:
        tool_auth = tool_auth_crud.get_tool_auth(session, GoogleDrive.NAME, user_id)
        return tool_auth.encrypted_access_token.decode() if tool_auth else None
