import logging

from authlib.integrations.requests_client import OAuth2Session
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

    def __init__(self):
        try:
            settings = OIDCSettings()
            # TODO: switch out to proper oidc strategy name
            self.REDIRECT_URI = f"{settings.frontend_hostname}/auth/complete"
            self.WELL_KNOWN_ENDPOINT = settings.oidc_well_known_endpoint
            self.client = OAuth2Session(
                client_id=settings.oidc_client_id,
                client_secret=settings.oidc_client_secret,
            )
        except Exception as e:
            logging.error(f"Error during initializing of OpenIDConnect class: {str(e)}")
            raise

    async def authorize(self, request: Request) -> dict | None:
        """
        Authenticates the current user using their OIDC account.

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
        user_info = self.client.get(self.USERINFO_ENDPOINT)

        return user_info.json()
