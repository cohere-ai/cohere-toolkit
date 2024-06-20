import logging

from authlib.integrations.requests_client import OAuth2Session

from backend.services.auth.strategies.base import BaseOAuthStrategy
from backend.services.auth.strategies.settings import Settings


class GoogleOAuthSettings(Settings):
    google_client_id: str
    google_client_secret: str
    frontend_hostname: str


class GoogleOAuth(BaseOAuthStrategy):
    """
    Google OAuth2.0 strategy.
    """

    NAME = "Google"
    WELL_KNOWN_ENDPOINT = "https://accounts.google.com/.well-known/openid-configuration"

    def __init__(self):
        try:
            self.settings = GoogleOAuthSettings()
            self.REDIRECT_URI = f"{self.settings.frontend_hostname}/auth/google"
            self.client = OAuth2Session(
                client_id=self.settings.google_client_id,
                client_secret=self.settings.google_client_secret,
            )
        except Exception as e:
            logging.error(f"Error during initializing of GoogleOAuth class: {str(e)}")
            raise

    def get_client_id(self):
        return self.settings.google_client_id

    def get_authorization_endpoint(self):
        return self.AUTHORIZATION_ENDPOINT

    def get_refresh_token_params(self):
        return {"access_type": "offline", "prompt": "consent"}
