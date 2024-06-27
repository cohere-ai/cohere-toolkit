import logging

import requests
from authlib.integrations.requests_client import OAuth2Session
from fastapi import HTTPException
from starlette.requests import Request

from backend.services.auth.strategies.base import BaseOAuthStrategy
from backend.services.auth.strategies.settings import Settings


class OIDCSettings(Settings):
    oidc_client_id: str
    oidc_client_secret: str
    oidc_well_known_endpoint: str
    frontend_hostname: str


class OpenIDConnect(BaseOAuthStrategy):
    """
    OpenID Connect strategy.
    """

    NAME = "OIDC"
    PKCE_ENABLED = True

    def __init__(self):
        try:
            self.settings = OIDCSettings()
            self.REDIRECT_URI = (
                f"{self.settings.frontend_hostname}/auth/{self.NAME.lower()}"
            )
            self.WELL_KNOWN_ENDPOINT = self.settings.oidc_well_known_endpoint
            self.client = OAuth2Session(
                client_id=self.settings.oidc_client_id,
                client_secret=self.settings.oidc_client_secret,
            )
        except Exception as e:
            logging.error(f"Error during initializing of OpenIDConnect class: {str(e)}")
            raise

    def get_client_id(self):
        return self.settings.oidc_client_id

    def get_authorization_endpoint(self):
        if hasattr(self, "AUTHORIZATION_ENDPOINT"):
            return self.AUTHORIZATION_ENDPOINT
        return None

    def get_pkce_enabled(self):
        if hasattr(self, "PKCE_ENABLED"):
            return self.PKCE_ENABLED
        return False

    async def get_endpoints(self):
        response = requests.get(self.WELL_KNOWN_ENDPOINT)
        endpoints = response.json()
        try:
            self.TOKEN_ENDPOINT = endpoints["token_endpoint"]
            self.USERINFO_ENDPOINT = endpoints["userinfo_endpoint"]
            self.AUTHORIZATION_ENDPOINT = endpoints["authorization_endpoint"]
        except Exception as e:
            logging.error(
                f"Error fetching `token_endpoint` and `userinfo_endpoint` from {endpoints}."
            )
            raise

    async def authorize(self, request: Request) -> dict | None:
        """
        Authenticates the current user using their OIDC account.

        Args:
            request (Request): Current request.

        Returns:
            Access token.
        """
        params = {
            "url": self.TOKEN_ENDPOINT,
            "authorization_response": str(request.url),
            "redirect_uri": self.REDIRECT_URI,
        }

        if self.PKCE_ENABLED:
            body = await request.json()
            code_verifier = body.get("code_verifier")

            if not code_verifier:
                raise HTTPException(
                    status_code=400,
                    detail="code_verifier not available in request body during PKCE flow.",
                )

            params["code_verifier"] = code_verifier

        token = self.client.fetch_token(**params)

        user_info = self.client.get(self.USERINFO_ENDPOINT)

        return user_info.json()
