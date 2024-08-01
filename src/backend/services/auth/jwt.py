import datetime
import uuid

import jwt

from backend.config.settings import Settings
from backend.services.logger.utils import LoggerFactory

logger = LoggerFactory().get_logger()


class JWTService:
    ISSUER = "cohere-toolkit"
    EXPIRY_DAYS = 90
    ALGORITHM = "HS256"

    def __init__(self):
        secret_key = Settings().auth.secret_key

        if not secret_key:
            raise ValueError(
                "AUTH_SECRET_KEY environment variable is missing, and is required to enable authentication."
            )

        self.secret_key = secret_key

    def create_and_encode_jwt(self, user: dict) -> str:
        """
        Creates a payload based on user info and creates a JWT token.

        Args:
            user (dict): User data.

        Returns:
            str: JWT token.
        """
        now = datetime.datetime.utcnow()
        payload = {
            "iss": self.ISSUER,
            "iat": now,
            "exp": now + datetime.timedelta(days=self.EXPIRY_DAYS),
            "jti": str(uuid.uuid4()),
            "context": user,
        }

        token = jwt.encode(payload, self.secret_key, self.ALGORITHM)

        return token

    def decode_jwt(self, token: str) -> dict:
        """
        Decodes a given JWT token.

        Args:
            token (str): JWT token.

        Returns:
            dict: Decoded JWT token payload.
        """
        try:
            decoded_payload = jwt.decode(
                token, self.secret_key, algorithms=[self.ALGORITHM]
            )
            return decoded_payload
        except jwt.ExpiredSignatureError:
            logger.warning(event="[Auth] JWT token is expired.")
            return None
        except jwt.InvalidTokenError:
            logger.warning(event="[Auth] JWT token is invalid.")
            return None
