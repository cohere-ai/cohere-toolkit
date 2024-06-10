import logging
from typing import List

from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request

from backend.services.auth.strategies.base import BaseOAuthStrategy
from backend.services.auth.strategies.settings import Settings


class OIDCSettings(Settings):
    oidc_client_id: str
    oidc_client_secret: str
    oidc_config_endpoint: str


class OpenIDConnect(BaseOAuthStrategy):
    """
    OpenID Connect strategy.
    """

    NAME = "OIDC"
    REDIRECT_METHOD_NAME = "oidc_authenticate"

    def __init__(self):
        try:
            settings = OIDCSettings()
            self.oauth = OAuth()
            self.oauth.register(
                name="auth0",
                client_id=settings.oidc_client_id,
                client_secret=settings.oidc_client_secret,
                server_metadata_url=settings.oidc_config_endpoint,
                client_kwargs={"scope": "openid email profile"},
            )
        except Exception as e:
            logging.error(f"Error during initializing of OpenIDConnect class: {str(e)}")
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
        Redirects to the /auth endpoint for user to sign onto their SSO account.

        Args:
            request (Request): Current request.
            redirect_uri (str): Redirect URI.

        Returns:
            Redirect to SSO.
        """
        return await self.oauth.auth0.authorize_redirect(request, redirect_uri)

    async def authenticate(self, request: Request) -> dict | None:
        """
        Authenticates the current user using their SSO account.

        Args:
            request (Request): Current request.

        Returns:
            Access token.
        """
        return await self.oauth.google.authorize_access_token(request)
