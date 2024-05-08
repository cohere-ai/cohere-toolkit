from typing import List

import bcrypt
from sqlalchemy.orm import Session

from backend.database_models.user import User
from backend.services.auth.base import BaseAuthenticationStrategy


class BasicAuthentication(BaseAuthenticationStrategy):
    """
    Basic email/password auth strategy.

    Attributes:
        NAME (str): The name of the strategy.
        SHOULD_ATTACH_TO_APP (str): Whether the strategy needs to be attached to the FastAPI application.
        SHOULD_AUTH_REDIRECT (str): Whether the strategy requires a redirect to the /auth endpoint after login.
    """

    NAME = "Basic"
    SHOULD_ATTACH_TO_APP = False
    SHOULD_AUTH_REDIRECT = False

    @staticmethod
    def get_required_payload() -> List[str]:
        """
        Retrieves the required /login payload for the Auth strategy.

        Returns:
            List[str]: List of required variables.
        """
        return ["email", "password"]

    @staticmethod
    def hash_and_salt_password(plain_text_password: str) -> str:
        """
        Hashes a given plain-text password with a randomly generated salt.

        Args:
            plain_text_password (str): Password to hash.

        Returns:
            str: Hashed password
        """
        return bcrypt.hashpw(plain_text_password.encode("utf-8"), bcrypt.gensalt())

    @staticmethod
    def check_password(plain_text_password: str, hashed_password: str) -> bool:
        """
        Checks that the input plain text password corresponds to a hashed password.

        Args:
            plain_text_password (str): Password to check.
            hashed_password (str): Password to check against.

        Returns:
            bool: Whether the plain-text password matches the given hashed password.
        """
        return bcrypt.checkpw(plain_text_password.encode("utf-8"), hashed_password)

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
