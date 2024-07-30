from fastapi import Request
from sqlalchemy.orm import Session

from backend.config.auth import ENABLED_AUTH_STRATEGY_MAPPING, is_authentication_enabled
from backend.crud import user as user_crud
from backend.database_models import User


def is_enabled_authentication_strategy(strategy_name: str) -> bool:
    """
    Check whether a given authentication strategy is enabled in config/auth.py

    Args:
        strategy_name (str): Name the of auth strategy.

    Returns:
        bool: Whether that strategy is currently enabled
    """
    # Check the strategy is valid and enabled
    if strategy_name not in ENABLED_AUTH_STRATEGY_MAPPING.keys():
        return False

    return True


def get_or_create_user(session: Session, token_user: dict[str, str]) -> dict:
    """
    Gets or creates a user when authenticating them.

    Args:
        session (Session): DB session
        token_user (dict): Dictionary of user


    Returns:
        User: User object
    """
    email = token_user.get("email")
    fullname = token_user.get("name")

    user = session.query(User).filter(User.email == email).first()

    # Create User if DNE
    if not user:
        db_user = User(fullname=fullname, email=email)
        user = user_crud.create_user(session, db_user)

    return {
        "id": user.id,
        "fullname": user.fullname,
        "email": user.email,
    }


def get_header_user_id(request: Request) -> str:
    """
    Retrieves the user_id from request headers, will work whether authentication is enabled or not.

    (Auth disabled): retrieves the User-Id header value
    (Auth enabled): retrieves the Authorization header, and decodes the value

    Args:
        request (Request): current Request


    Returns:
        str: User ID
    """
    # Import here to avoid circular imports
    from backend.services.auth.jwt import JWTService

    # Check if Auth enabled
    if is_authentication_enabled():
        # Validation already performed, so just retrieve value
        authorization = request.headers.get("Authorization")
        _, token = authorization.split(" ")
        decoded = JWTService().decode_jwt(token)

        return decoded["context"]["id"]
    # Auth disabled
    else:
        user_id = request.headers.get("User-Id", "")
        return user_id


def has_header_user_id(request: Request) -> bool:
    """
    Check whether we can get the user_id from the request headers.

    Args:
        request (Request): current Request

    Returns:
        bool: Whether the user_id is present in the headers
    """

    if is_authentication_enabled():
        authorization = request.headers.get("Authorization")
        return authorization is not None
    else:
        user_id = request.headers.get("User-Id")
        return user_id is not None
