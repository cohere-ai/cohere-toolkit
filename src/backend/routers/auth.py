from authlib.integrations.starlette_client import OAuthError
from fastapi import APIRouter, Depends, HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse

from backend.config.auth import ENABLED_AUTH_STRATEGY_MAPPING
from backend.config.routers import RouterName
from backend.database_models import get_session
from backend.database_models.database import DBSessionDep
from backend.schemas.auth import Auth, Login
from backend.services.auth.jwt import JWTService
from backend.services.auth.utils import (
    get_or_create_user,
    is_enabled_authentication_strategy,
)

router = APIRouter(prefix="/v1")
router.name = RouterName.AUTH


@router.get("/auth_strategies")
def get_strategies():
    """
    Retrieves the currently enabled list of Authentication strategies.


    Returns:
        List[dict]: List of dictionaries containing the enabled auth strategy names.
    """
    strategies = []
    for key in ENABLED_AUTH_STRATEGY_MAPPING.keys():
        strategies.append({"strategy": key})

    return strategies


@router.post("/login")
async def login(request: Request, login: Login, session: DBSessionDep):
    """
    Logs user in and either:
    - (Basic email/password authentication) Verifies their credentials, retrieves the user and returns a JWT token.
    - (OAuth) Redirects to the /auth endpoint.

    Args:
        request (Request): current Request object.
        login (Login): Login payload.
        session (DBSessionDep): Database session.

    Returns:
        dict: JWT token on basic auth success
        or
        Redirect: to /auth endpoint

    Raises:
        HTTPException: If the strategy or payload are invalid, or if the login fails.
    """
    strategy_name = login.strategy
    payload = login.payload

    if not is_enabled_authentication_strategy(strategy_name):
        raise HTTPException(
            status_code=422, detail=f"Invalid Authentication strategy: {strategy_name}."
        )

    # Check that the payload required is given
    strategy = ENABLED_AUTH_STRATEGY_MAPPING[strategy_name]
    strategy_payload = strategy.get_required_payload()
    if not set(strategy_payload).issubset(payload.keys()):
        missing_keys = [key for key in strategy_payload if key not in payload.keys()]
        raise HTTPException(
            status_code=422,
            detail=f"Missing the following keys in the payload: {missing_keys}.",
        )

    # Login with redirect to /auth
    if strategy.SHOULD_AUTH_REDIRECT:
        redirect_uri = request.url_for("authenticate")
        return await strategy.login(request, redirect_uri)
    # Login with email/password and set session directly
    else:
        user = strategy.login(session, payload)
        if not user:
            raise HTTPException(
                status_code=401,
                detail=f"Error performing {strategy_name} authentication with payload: {payload}.",
            )

        token = JWTService().create_and_encode_jwt(user)

        return {"token": token}


@router.post("/auth")
async def authenticate(request: Request, auth: Auth, session: DBSessionDep):
    """
    Authentication endpoint used for OAuth strategies. Logs the user in the redirect environment and then
    sets the current session with the user returned from the auth token.

    Args:
        request (Request): current Request object.
        login (Login): Login payload.

    Returns:
        RedirectResponse: On success.

    Raises:
        HTTPException: If authentication fails, or strategy is invalid.
    """
    strategy_name = auth.strategy
    if not is_enabled_authentication_strategy(strategy_name):
        raise HTTPException(
            status_code=404, detail=f"Invalid Authentication strategy: {strategy_name}."
        )

    strategy = ENABLED_AUTH_STRATEGY_MAPPING[strategy_name]

    try:
        token = await strategy.authenticate(request)
    except OAuthError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Could not authenticate, failed with error: {str(e)}",
        )

    token_user = token.get("userinfo")

    if not token_user:
        raise HTTPException(
            status_code=401, detail=f"Could not get user from auth token: {token}."
        )

    # Get or create user, then set session user
    user = get_or_create_user(session, token_user)

    token = JWTService().create_and_encode_jwt(user)

    return {"token": token}


@router.get("/logout")
async def logout(request: Request):
    """
    Logs out the current user.

    Args:
        request (Request): current Request object.

    Returns:
        dict: Empty on success
    """
    # TODO: Design blacklist

    return {}
