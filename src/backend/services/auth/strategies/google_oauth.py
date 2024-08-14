import requests
from authlib.integrations.requests_client import OAuth2Session
from starlette.requests import Request

from backend.config.settings import Settings
from backend.services.auth.strategies.base import BaseOAuthStrategy
from backend.services.logger.utils import LoggerFactory

logger = LoggerFactory().get_logger()


class GoogleOAuth(BaseOAuthStrategy):
    """
    Google OAuth2.0 strategy.
    """

    NAME = "Google"
    WELL_KNOWN_ENDPOINT = "https://accounts.google.com/.well-known/openid-configuration"

    def __init__(self):
        try:
            self.settings = Settings().auth.google_oauth
            self.REDIRECT_URI = (
                f"{Settings().auth.frontend_hostname}/auth/{self.NAME.lower()}"
            )
            self.client = OAuth2Session(
                client_id=self.settings.client_id,
                client_secret=self.settings.client_secret,
            )
        except Exception as e:
            logger.error(
                event=f"[Google OAuth] Error during initializing of GoogleOAuth class: {str(e)}"
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
                event=f"[Google OAuth] Error fetching endpoints: `token_endpoint`, `userinfo_endpoint` or `authorization_endpoint` not found in {endpoints}."
            )
            raise

    async def authorize(self, request: Request) -> dict | None:
        """
        Authenticates the current user using their Google account.

        Args:
            request (Request): Current request.

        Returns:
            Access token.
        """
        token = self.client.fetch_token(
            url=self.TOKEN_ENDPOINT,
            authorization_response=str(request.url),
            redirect_uri=self.REDIRECT_URI,
        )
        user_info = self.client.get(self.USERINFO_ENDPOINT)

        return user_info.json()
