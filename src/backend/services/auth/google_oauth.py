import logging
import os
from typing import List

from authlib.integrations.starlette_client import OAuth, OAuthError
from sqlalchemy.orm import Session

from backend.database_models.user import User
from backend.services.auth.base import BaseOAuthStrategy


class GoogleOAuthStrategy(BaseOAuthStrategy):
    """
    Google OAuth2.0 strategy.
    """

    NAME = "Google OAuth"
    GOOGLE_DISCOVERY_DOCUMENT_URL = (
        "https://accounts.google.com/.well-known/openid-configuration"
    )
    GOOGLE_DEFAULT_SCOPE = "openid email profile"

    def __init__(self):
        client_id = os.environ.get("GOOGLE_CLIENT_ID")
        client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")

        if any([client_id is None, client_secret is None]):
            raise ValueError(
                "To use Google OAuth, please set the GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables."
            )

        self.config = {
            "GOOGLE_CLIENT_ID": client_id,
            "GOOGLE_CLIENT_SECRET": client_secret,
        }

        try:
            self.oauth = OAuth(self.config)
            self.oauth.register(
                name="google",
                server_metadata_url=self.GOOGLE_DISCOVERY_DOCUMENT_URL,
                client_kwargs={"scope": self.GOOGLE_DEFAULT_SCOPE},
            )
        except Exception as e:
            logging.ERROR(f"Error during initializing of GoogleOAuthStrategy.")
            raise

    @staticmethod
    def get_required_payload() -> List[str]:
        """
        Retrieves the required /login payload for the Auth strategy.

        Returns:
            List[str]: List of required variables.
        """
        return []

    @classmethod
    def login(cls, session: Session, payload: dict[str, str]) -> dict | None:
        """
        Logs user in, checking the if the hashed input password corresponds to the
        one stored in the DB.

        Args:
            session (Session): DB Session
            payload (dict[str, str]): Login payload

        Returns:
            dict | None: Returns the user as dict to set the app session, or None.
        """

        payload_email = payload.get("email", "")
        payload_password = payload.get("password", "")
        user = session.query(User).filter(User.email == payload_email).first()

        if not user:
            return None

        if cls.check_password(payload_password, user.hashed_password):
            return {
                "id": user.id,
                "fullname": user.fullname,
                "email": user.email,
            }

        return None
