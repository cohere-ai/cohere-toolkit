from authlib.integrations.starlette_client import OAuthError
from fastapi import APIRouter, Depends, HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse

from backend.config.auth import ENABLED_AUTH_STRATEGY_MAPPING
from backend.database_models import get_session
from backend.database_models.database import DBSessionDep
from backend.schemas.auth import Auth, Login
from backend.services.auth.utils import (
    get_or_create_user,
    is_enabled_authentication_strategy,
)

router = APIRouter(dependencies=[Depends(get_session)])


@router.get("/auth_strategies")
def get_session():
    """
    Retrieves the currently enabled list of Authentication strategies.


    Returns:
        List[str]: List of names for enabled Authentication strategies, can be empty.
    """
    return ENABLED_AUTH_STRATEGY_MAPPING.keys()


@router.get("/session")
def get_session(request: Request):
    """
    Retrievers the current session user.

    Args:
        request (Request): current Request object.

    Returns:
        session: current user session ({} if no active session)

    Raises:
        401 HTTPException if no user found in session.
    """

    if not request.session:
        raise HTTPException(status_code=401, detail="Not authenticated.")

    return request.session.get("user")


@router.post("/login")
async def login(request: Request, login: Login, session: DBSessionDep):
    """
    Logs user in and EITHER:
    - Verifies their credentials and sets the current session
    - Redirects to the /auth endpoint.

    Args:
        request (Request): current Request object.
        login (Login): Login payload.
        session (DBSessionDep): Database session.

    Returns:
        RedirectResponse: On success

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

        # Set session user
        request.session["user"] = user

    return {}


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
    request.session["user"] = user

    return {}


@router.get("/logout")
async def logout(request: Request):
    """
    Logs out the current user session.

    Args:
        request (Request): current Request object.

    Returns:
        RedirectResponse: On success.
    """
    request.session.pop("user", None)

    return {}
