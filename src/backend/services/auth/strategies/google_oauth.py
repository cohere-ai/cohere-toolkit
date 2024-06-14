import logging
from typing import List

from authlib.integrations.requests_client import OAuth2Session
from starlette.requests import Request

from backend.services.auth.strategies.base import BaseOAuthStrategy
from backend.services.auth.strategies.settings import Settings


class GoogleOauthSettings(Settings):
    google_client_id: str
    google_client_secret: str
    frontend_hostname: str


class GoogleOAuth(BaseOAuthStrategy):
    """
    Google OAuth2.0 strategy.
    """

    NAME = "Google"
    TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
    USER_INFO_ENDPOINT = "https://openidconnect.googleapis.com/v1/userinfo"

    def __init__(self):
        try:
            settings = GoogleOauthSettings()
            self.redirect_uri = f"{settings.frontend_hostname}/auth/complete"
            self.client = OAuth2Session(
                client_id=settings.google_client_id,
                client_secret=settings.google_client_secret,
            )
        except Exception as e:
            logging.error(f"Error during initializing of GoogleOAuth class: {str(e)}")
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
            redirect_uri=self.redirect_uri,
        )
        user_info = self.client.get(self.USER_INFO_ENDPOINT)

        return user_info.json()
