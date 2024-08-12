import json
from typing import Union
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from starlette.requests import Request

from backend.config.auth import ENABLED_AUTH_STRATEGY_MAPPING
from backend.config.routers import RouterName
from backend.config.settings import Settings
from backend.config.tools import AVAILABLE_TOOLS
from backend.crud import blacklist as blacklist_crud
from backend.database_models import Blacklist
from backend.database_models.database import DBSessionDep
from backend.schemas.auth import JWTResponse, ListAuthStrategy, Login, Logout
from backend.schemas.context import Context
from backend.services.auth.jwt import JWTService
from backend.services.auth.request_validators import validate_authorization
from backend.services.auth.utils import (
    get_or_create_user,
    is_enabled_authentication_strategy,
)
from backend.services.cache import cache_get_dict
from backend.services.context import get_context

router = APIRouter(prefix="/v1")
router.name = RouterName.AUTH


@router.get("/auth_strategies", response_model=list[ListAuthStrategy])
def get_strategies(
    ctx: Context = Depends(get_context),
) -> list[ListAuthStrategy]:
    """
    Retrieves the currently enabled list of Authentication strategies.

    Args:
        ctx (Context): Context object.
    Returns:
        List[dict]: List of dictionaries containing the enabled auth strategy names.
    """
    strategies = []
    for strategy_name, strategy_instance in ENABLED_AUTH_STRATEGY_MAPPING.items():
        strategies.append(
            {
                "strategy": strategy_name,
                "client_id": (
                    strategy_instance.get_client_id()
                    if hasattr(strategy_instance, "get_client_id")
                    else None
                ),
                "authorization_endpoint": (
                    strategy_instance.get_authorization_endpoint()
                    if hasattr(strategy_instance, "get_authorization_endpoint")
                    else None
                ),
                "pkce_enabled": (
                    strategy_instance.get_pkce_enabled()
                    if hasattr(strategy_instance, "get_pkce_enabled")
                    else False
                ),
            }
        )

    return strategies


@router.post("/login", response_model=Union[JWTResponse, None])
async def login(
    login: Login, session: DBSessionDep, ctx: Context = Depends(get_context)
):
    """
    Logs user in, performing basic email/password auth.
    Verifies their credentials, retrieves the user and returns a JWT token.

    Args:
        login (Login): Login payload.
        session (DBSessionDep): Database session.
        ctx (Context): Context object.

    Returns:
        dict: JWT token on Basic auth success

    Raises:
        HTTPException: If the strategy or payload are invalid, or if the login fails.
    """
    logger = ctx.get_logger()
    strategy_name = login.strategy
    payload = login.payload

    if not is_enabled_authentication_strategy(strategy_name):
        logger.error(
            event=f"[Auth] Error logging in: Invalid authentication strategy {strategy_name}",
        )
        raise HTTPException(
            status_code=422, detail=f"Invalid Authentication strategy: {strategy_name}."
        )

    # Check that the payload required is given
    strategy = ENABLED_AUTH_STRATEGY_MAPPING[strategy_name]
    strategy_payload = strategy.get_required_payload()
    if not set(strategy_payload).issubset(payload.keys()):
        missing_keys = [key for key in strategy_payload if key not in payload.keys()]
        logger.error(
            event=f"[Auth] Error logging in: Keys {missing_keys} missing from payload",
        )
        raise HTTPException(
            status_code=422,
            detail=f"Missing the following keys in the payload: {missing_keys}.",
        )

    user = strategy.login(session, payload)
    if not user:
        logger.error(
            event=f"[Auth] Error logging in: Invalid credentials in payload {payload}",
        )
        raise HTTPException(
            status_code=401,
            detail=f"Error performing {strategy_name} authentication with payload: {payload}.",
        )

    token = JWTService().create_and_encode_jwt(user)

    return {"token": token}


@router.post("/{strategy}/auth", response_model=JWTResponse)
async def authorize(
    strategy: str,
    request: Request,
    session: DBSessionDep,
    code: str = None,
    ctx: Context = Depends(get_context),
):
    """
    Callback authorization endpoint used for OAuth providers after authenticating on the provider's login screen.

    Args:
        strategy (str): Current strategy name.
        request (Request): Current Request object.
        session (Session): DB session.
        code (str): OAuth code.
        ctx (Context): Context object.

    Returns:
        dict: Containing "token" key, on success.

    Raises:
        HTTPException: If authentication fails, or strategy is invalid.
    """
    logger = ctx.get_logger()

    if not code:
        logger.error(
            event="[Auth] Error authorizing login: No code provided",
        )
        raise HTTPException(
            status_code=400,
            detail=f"Error calling /auth with invalid code query parameter.",
        )

    strategy_name = None
    for enabled_strategy_name in ENABLED_AUTH_STRATEGY_MAPPING.keys():
        if enabled_strategy_name.lower() == strategy.lower():
            strategy_name = enabled_strategy_name

    if not strategy_name:
        logger.error(
            event=f"[Auth] Error authorizing login: Invalid strategy {strategy_name}",
        )
        raise HTTPException(
            status_code=400,
            detail=f"Error calling /auth with invalid strategy name: {strategy_name}.",
        )

    if not is_enabled_authentication_strategy(strategy_name):
        logger.error(
            event=f"[Auth] Error authorizing login: Strategy {strategy_name} not enabled",
        )
        raise HTTPException(
            status_code=404, detail=f"Invalid Authentication strategy: {strategy_name}."
        )

    strategy = ENABLED_AUTH_STRATEGY_MAPPING[strategy_name]

    try:
        userinfo = await strategy.authorize(request)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Could not fetch access token from provider, failed with error: {str(e)}",
        )

    if not userinfo:
        logger.error(
            event="[Auth] Error authorizing login: Invalid token",
        )
        raise HTTPException(
            status_code=401, detail="Could not get user from auth token."
        )

    # Get or create user, then set session user
    user = get_or_create_user(session, userinfo)

    token = JWTService().create_and_encode_jwt(user)

    return {"token": token}


@router.get("/logout", response_model=Logout)
async def logout(
    request: Request,
    session: DBSessionDep,
    token: dict | None = Depends(validate_authorization),
    ctx: Context = Depends(get_context),
):
    """
    Logs out the current user, adding the given JWT token to the blacklist.

    Args:
        request (Request): current Request object.
        session (DBSessionDep): Database session.
        token (dict): JWT token payload.
        ctx (Context): Context object.

    Returns:
        dict: Empty on success
    """
    if token is not None:
        db_blacklist = Blacklist(token_id=token["jti"])
        blacklist_crud.create_blacklist(session, db_blacklist)

    return {}


# NOTE: Tool Auth is experimental and in development
@router.get("/tool/auth")
async def login(
    request: Request, session: DBSessionDep, ctx: Context = Depends(get_context)
):
    """
    Endpoint for Tool Authentication. Note: The flow is different from
    the regular login OAuth flow, the backend initiates it and redirects to the frontend
    after completion.

    If completed, a ToolAuth is stored in the DB containing the access token for the tool.

    Args:
        request (Request): current Request object.
        session (DBSessionDep): Database session.
        ctx (Context): Context object.

    Returns:
        RedirectResponse: A redirect pointing to the frontend, contains an error query parameter if
            an unexpected error happens during the authentication.

    Raises:
        HTTPException: If no redirect_uri set.
    """
    logger = ctx.get_logger()
    redirect_uri = Settings().auth.frontend_hostname

    if not redirect_uri:
        raise HTTPException(
            status_code=400,
            detail=f"FRONTEND_HOSTNAME environment variable is required for Tool Auth.",
        )

    def log_and_redirect_err(error_message: str):
        logger.error(event=error_message)
        redirect_err = f"{redirect_uri}?error={quote(error_message)}"
        return RedirectResponse(redirect_err)

    # Get key from state and retrieve cache
    try:
        state = json.loads(request.query_params.get("state"))
        cache_key = state["key"]
        tool_auth_cache = cache_get_dict(cache_key)
    except Exception as e:
        log_and_redirect_err(str(e))

    user_id = tool_auth_cache.get("user_id")
    tool_id = tool_auth_cache.get("tool_id")

    if not tool_auth_cache:
        err = f"Error retrieving cache for Tool Auth with key: {cache_key}"
        log_and_redirect_err(err)

    if user_id is None or tool_id is None:
        err = f"Tool Auth cache {tool_auth_cache} does not contain user_id or tool_id."
        log_and_redirect_err(err)

    if tool_id in AVAILABLE_TOOLS:
        tool = AVAILABLE_TOOLS.get(tool_id)
        err = None

        # Tool not found
        if not tool:
            err = f"Tool {tool_id} does not exist or is not available."
            log_and_redirect_err(err)

        # Tool does not have Auth implemented
        if tool.auth_implementation is None:
            err = f"Tool {tool.name} does not have an auth_implementation required for Tool Auth."
            log_and_redirect_err(err)

        try:
            tool_auth_service = tool.auth_implementation()
            err = tool_auth_service.retrieve_auth_token(request, session, user_id)
        except Exception as e:
            log_and_redirect_err(str(e))

        if err:
            log_and_redirect_err(err)

    response = RedirectResponse(redirect_uri)

    return response
