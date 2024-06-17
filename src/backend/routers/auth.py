from typing import Union

from authlib.integrations.starlette_client import OAuthError
from fastapi import APIRouter, HTTPException
from starlette.requests import Request

from backend.config.auth import ENABLED_AUTH_STRATEGY_MAPPING
from backend.config.routers import RouterName
from backend.database_models.database import DBSessionDep
from backend.schemas.auth import JWTResponse, ListAuthStrategy, Login, Logout
from backend.services.auth import GoogleOAuth, OpenIDConnect
from backend.services.auth.jwt import JWTService
from backend.services.auth.utils import (
    get_or_create_user,
    is_enabled_authentication_strategy,
)

router = APIRouter(prefix="/v1")
router.name = RouterName.AUTH


@router.get("/auth_strategies", response_model=list[ListAuthStrategy])
def get_strategies() -> list[ListAuthStrategy]:
    """
    Retrieves the currently enabled list of Authentication strategies.


    Returns:
        List[dict]: List of dictionaries containing the enabled auth strategy names.
    """
    strategies = []
    for key in ENABLED_AUTH_STRATEGY_MAPPING.keys():
        strategies.append({"strategy": key})

    return strategies


@router.post("/login", response_model=Union[JWTResponse, None])
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
        # Fetch endpoint with method name
        redirect_uri = request.url_for(strategy.REDIRECT_METHOD_NAME)
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


@router.get("/google/auth", response_model=JWTResponse)
async def google_authenticate(request: Request, session: DBSessionDep):
    """
    Callback authentication endpoint used for Google OAuth after redirecting to
    the service's login screen.

    Args:
        request (Request): current Request object.

    Returns:
        RedirectResponse: On success.

    Raises:
        HTTPException: If authentication fails, or strategy is invalid.
    """
    strategy_name = GoogleOAuth.NAME

    return await authenticate(request, session, strategy_name)


@router.get("/oidc/auth", response_model=JWTResponse)
async def oidc_authenticate(request: Request, session: DBSessionDep):
    """
    Callback authentication endpoint used for OIDC after redirecting to
    the service's login screen.

    Args:
        request (Request): current Request object.

    Returns:
        RedirectResponse: On success.

    Raises:
        HTTPException: If authentication fails, or strategy is invalid.
    """
    strategy_name = OpenIDConnect.NAME

    return await authenticate(request, session, strategy_name)


@router.get("/logout", response_model=Logout)
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


async def authenticate(
    request: Request, session: DBSessionDep, strategy_name: str
) -> JWTResponse:
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
