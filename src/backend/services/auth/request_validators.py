import datetime

from fastapi import Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from backend.config.auth import get_auth_strategy
from backend.database_models import Blacklist, get_session
from backend.services.auth.jwt import JWTService
from backend.services.auth.utils import get_or_create_user
from backend.services.logger import get_logger

UPDATE_TOKEN_HEADER = "X-Toolkit-Auth-Update"
logger = get_logger()


def validate_authorization(
    request: Request, response: Response, session: Session = Depends(get_session)
) -> dict:
    """
    Validate that the request has the `Authorization` header, used for requests
    that require authentication.

    Args:
        request (Request): The request to validate

    Raises:
        HTTPException: If no `Authorization` header.

    Returns:
        dict: Decoded payload.
    """

    # Check if `Authorization` header is present
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization: Bearer <token> required in request headers.",
        )

    # Check if `Authorization` header is well-formed and contains a `Bearer` token.
    scheme, token = authorization.split(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Authorization: Bearer <token> required in request headers.",
        )

    jwt_payload = JWTService().decode_jwt(token)

    match JWTService.check_validity(jwt_payload, session):
        case "invalid":
            raise HTTPException(status_code=401, detail="Bearer token is invalid.")
        case "expired":
            raise HTTPException(status_code=401, detail="Auth token has expired.")
        case "refreshable":
            try:
                logger.info("JWT is within refresh availability window; refreshing.")
                token = JWTService().refresh_jwt(token)

                if not token:
                    raise HTTPException(
                        status_code=401,
                        detail="Could not refresh token, please re-authenticate.",
                    )

                response.headers[UPDATE_TOKEN_HEADER] = token

                # TODO(AW): Also add the old token to the blacklist

                return JWTService().decode_jwt(token)
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Could not create user and encode JWT token.",
                )

    return jwt_payload
