import datetime
import logging
import os
import uuid

import jwt
from fastapi import Depends
from sqlalchemy.orm import Session

from backend.database_models import Blacklist, get_session
from backend.services.logger import get_logger

logger = get_logger()


class JWTService:
    ISSUER = "cohere-toolkit"
    # AUTH_EXPIRY_MONTHS = 3
    # JWT_EXPIRY_HOURS = 72
    # REFRESH_AVAILABILITY_HOURS = 36
    AUTH_EXPIRY_SECONDS = 60 * 2
    JWT_EXPIRY_SECONDS = 30
    REFRESH_AVAILABILITY_SECONDS = 15
    ALGORITHM = "HS256"

    def __init__(self):
        secret_key = os.environ.get("AUTH_SECRET_KEY")

        if not secret_key:
            raise ValueError(
                "AUTH_SECRET_KEY environment variable is missing, and is required to enable authentication."
            )

        self.secret_key = secret_key

    def create_and_encode_jwt(self, user: dict, strategy_name: str, **kwargs) -> str:
        """
        Creates a payload based on user info and creates a JWT token.

        Args:
            user (dict): User data.
            strategy_name (str): Name of the authentication strategy.
            kwargs: Additional payload data. These parameters will override normal payload data.

        Returns:
            str: JWT token.
        """
        now = datetime.datetime.now(datetime.timezone.utc)
        payload = {
            "iss": self.ISSUER,
            "iat": now,
            # "exp": now + datetime.timedelta(hours=self.AUTH_EXPIRY_HOURS),
            "exp": now + datetime.timedelta(seconds=self.JWT_EXPIRY_SECONDS),
            "jti": str(uuid.uuid4()),
            "strategy": strategy_name,
            "context": user,
            **kwargs,
        }

        token = jwt.encode(payload, self.secret_key, self.ALGORITHM)

        return token

    def refresh_jwt(self, token: str) -> str:
        """
        Refreshes a given JWT token. Callers should check if the token is expired before calling this method.

        Args:
            token (str): JWT token.

        Returns:
            str: New JWT token.
        """
        decoded_payload = self.decode_jwt(token)

        if not decoded_payload:
            return None

        # Create new token with same payload
        return self.create_and_encode_jwt(
            decoded_payload["context"],
            decoded_payload["strategy"],
            iat=decoded_payload["iat"],
        )

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
            logger.warning("JWT Token has expired.")
            decoded_payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.ALGORITHM],
                options={"verify_exp": False},
            )
            return decoded_payload
        except jwt.InvalidTokenError:
            logger.warning("JWT Token is invalid.")
            return None

    @staticmethod
    def check_validity(payload: dict, session: Session = Depends(get_session)) -> str:
        """
        Checks a given JWT payload for its validity.

        Args:
            payload (dict): JWT payload.

        Returns:
            str: One of the following strings depending on the validity:
                - "valid": Token is valid.
                - "refreshable": Token is valid and within the refresh availability window.
                - "expired": Token is expired or blacklisted.
                - "invalid": Token is invalid.
        """

        if payload is None or any(
            [
                "context" not in payload,
                "jti" not in payload,
                "exp" not in payload,
                "strategy" not in payload,
                "iat" not in payload,
            ]
        ):
            return "invalid"

        now = datetime.datetime.now(datetime.timezone.utc)

        # Check if token is blacklisted
        blacklist = (
            session.query(Blacklist)
            .filter(Blacklist.token_id == payload["jti"])
            .first()
        )

        if blacklist is not None:
            logger.warning("JWT payload is blacklisted.")
            return "expired"

        # Check if token is expired; either we're past the expiry time or iat is more than 3 months ago
        expiry_datetime = datetime.datetime.fromtimestamp(
            payload["exp"], datetime.timezone.utc
        )
        issued_datetime = datetime.datetime.fromtimestamp(
            payload["iat"], datetime.timezone.utc
        )

        # if now > expiry_datetime or now > (issued_datetime + datetime.timedelta(months=JWTService.AUTH_EXPIRY_MONTHS)):
        if now > expiry_datetime or now > (
            issued_datetime + datetime.timedelta(seconds=JWTService.AUTH_EXPIRY_SECONDS)
        ):
            return "expired"

        # if now > (expiry_datetime - datetime.timedelta(hours=JWTService.REFRESH_AVAILABILITY_HOURS)):
        if now > (
            expiry_datetime
            - datetime.timedelta(seconds=JWTService.REFRESH_AVAILABILITY_SECONDS)
        ):
            return "refreshable"

        return "valid"
