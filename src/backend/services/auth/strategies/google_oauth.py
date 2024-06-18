import logging
from typing import List

from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request

from backend.services.auth.strategies.base import BaseOAuthStrategy
from backend.services.auth.strategies.settings import Settings


class GoogleOAuthSettings(Settings):
    google_client_id: str
    google_client_secret: str


class GoogleOAuth(BaseOAuthStrategy):
    """
    Google OAuth2.0 strategy.
    """

    NAME = "Google"
    REDIRECT_METHOD_NAME = "google_authenticate"

    def __init__(self):
        try:
            settings = GoogleOAuthSettings()
            self.oauth = OAuth()
            self.oauth.register(
                name="google",
                server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
                client_id=settings.google_client_id,
                client_secret=settings.google_client_secret,
                client_kwargs={"scope": "openid email profile"},
            )
        except Exception as e:
            logging.error(f"Error during initializing of GoogleOAuth class: {str(e)}")
            raise

    @staticmethod
    def get_required_payload() -> List[str]:
        """
        Retrieves the required /login payload for the Auth strategy.

        Returns:
            List[str]: List of required variables.
        """
        return []

    async def login(self, request: Request, redirect_uri: str) -> dict | None:
        """
        Redirects to the /auth endpoint for user to sign onto their Google account.

        Args:
            request (Request): Current request.
            redirect_uri (str): Redirect URI.

        Returns:
            Redirect to Google OAuth.
        """
        return await self.oauth.google.authorize_redirect(request, redirect_uri)

    async def authenticate(self, request: Request) -> dict | None:
        """
        Authenticates the current user using their Google account.

        Args:
            request (Request): Current request.

        Returns:
            Access token.
        """
        return await self.oauth.google.authorize_access_token(request)
