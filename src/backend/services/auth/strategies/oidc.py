import requests
from authlib.integrations.requests_client import OAuth2Session
from fastapi import HTTPException
from starlette.requests import Request

from backend.config.settings import Settings
from backend.services.auth.strategies.base import BaseOAuthStrategy
from backend.services.logger.utils import LoggerFactory

logger = LoggerFactory().get_logger()


class OpenIDConnect(BaseOAuthStrategy):
    """
    OpenID Connect strategy.
    """

    NAME = "OIDC"
    PKCE_ENABLED = True

    def __init__(self):
        try:
            self.settings = Settings().auth.oidc
            self.REDIRECT_URI = (
                f"{Settings().auth.frontend_hostname}/auth/{self.NAME.lower()}"
            )
            self.WELL_KNOWN_ENDPOINT = self.settings.well_known_endpoint
            self.client = OAuth2Session(
                client_id=self.settings.client_id,
                client_secret=self.settings.client_secret,
            )
        except Exception as e:
            logger.error(
                event=f"[OpenIDConnect] Error initializing OpenIDConnect: {str(e)}"
            )
            raise

    def get_client_id(self):
        return self.settings.client_id

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
            logger.error(
                event=f"Error fetching `token_endpoint` and `userinfo_endpoint` from {endpoints}."
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
