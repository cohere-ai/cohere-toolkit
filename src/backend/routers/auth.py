import json
import os
from typing import Union
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from starlette.requests import Request

from backend.config.auth import ENABLED_AUTH_STRATEGY_MAPPING
from backend.config.routers import RouterName
from backend.config.tools import AVAILABLE_TOOLS
from backend.crud import blacklist as blacklist_crud
from backend.database_models import Blacklist
from backend.database_models.database import DBSessionDep
from backend.schemas.auth import JWTResponse, ListAuthStrategy, Login, Logout
from backend.services.auth.jwt import JWTService
from backend.services.auth.request_validators import validate_authorization
from backend.services.auth.utils import (
    get_or_create_user,
    is_enabled_authentication_strategy,
)
from backend.services.logger import get_logger

logger = get_logger()

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
async def login(request: Request, login: Login, session: DBSessionDep):
    """
    Logs user in, performing basic email/password auth.
    Verifies their credentials, retrieves the user and returns a JWT token.

    Args:
        request (Request): current Request object.
        login (Login): Login payload.
        session (DBSessionDep): Database session.

    Returns:
        dict: JWT token on Basic auth success

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

    user = strategy.login(session, payload)
    if not user:
        raise HTTPException(
            status_code=401,
            detail=f"Error performing {strategy_name} authentication with payload: {payload}.",
        )

    token = JWTService().create_and_encode_jwt(user)

    return {"token": token}


@router.post("/{strategy}/auth", response_model=JWTResponse)
async def authorize(
    strategy: str, request: Request, session: DBSessionDep, code: str = None
):
    """
    Callback authorization endpoint used for OAuth providers after authenticating on the provider's login screen.

    Args:
        strategy (str): Current strategy name.
        request (Request): Current Request object.
        session (Session): DB session.

    Returns:
        dict: Containing "token" key, on success.

    Raises:
        HTTPException: If authentication fails, or strategy is invalid.
    """
    if not code:
        raise HTTPException(
            status_code=400,
            detail=f"Error calling /auth with invalid code query parameter.",
        )

    strategy_name = None
    for enabled_strategy_name in ENABLED_AUTH_STRATEGY_MAPPING.keys():
        if enabled_strategy_name.lower() == strategy.lower():
            strategy_name = enabled_strategy_name

    if not strategy_name:
        raise HTTPException(
            status_code=400,
            detail=f"Error calling /auth with invalid strategy name: {strategy_name}.",
        )

    if not is_enabled_authentication_strategy(strategy_name):
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
        raise HTTPException(
            status_code=401, detail=f"Could not get user from auth token: {token}."
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
):
    """
    Logs out the current user, adding the given JWT token to the blacklist.

    Args:
        request (Request): current Request object.

    Returns:
        dict: Empty on success
    """
    if token is not None:
        db_blacklist = Blacklist(token_id=token["jti"])
        blacklist_crud.create_blacklist(session, db_blacklist)

    return {}


# NOTE: Tool Auth is experimental and in development
@router.get("/tool/auth")
async def login(request: Request, session: DBSessionDep):
    """
    Endpoint for Tool Authentication. Note: The flow is different from
    the regular login OAuth flow, the backend initiates it and redirects to the frontend
    after completion.

    If completed, a ToolAuth is stored in the DB containing the access token for the tool.

    Args:
        request (Request): current Request object.
        session (DBSessionDep): Database session.

    Returns:
        RedirectResponse: A redirect pointing to the frontend, contains an error query parameter if
            an unexpected error happens during the authentication.

    Raises:
        HTTPException: If no redirect_uri set.
    """
    redirect_uri = os.getenv("FRONTEND_HOSTNAME")

    if not redirect_uri:
        raise HTTPException(
            status_code=400,
            detail=f"FRONTEND_HOSTNAME environment variable is required for Tool Auth.",
        )

    # TODO: Store user id and tool id in the DB for state key
    state = json.loads(request.query_params.get("state"))
    tool_id = state["tool_id"]

    if tool_id in AVAILABLE_TOOLS:
        tool = AVAILABLE_TOOLS.get(tool_id)
        err = None

        # Tool not found
        if not tool:
            err = f"Tool {tool_id} does not exist or is not available."
            logger.error(err)
            redirect_err = f"{redirect_uri}?error={quote(err)}"
            return RedirectResponse(redirect_err)

        # Tool does not have Auth implemented
        if tool.auth_implementation is None:
            err = f"Tool {tool.name} does not have an auth_implementation required for Tool Auth."
            logger.error(err)
            redirect_err = f"{redirect_uri}?error={quote(err)}"
            return RedirectResponse(redirect_err)

        try:
            tool_auth_service = tool.auth_implementation()
            err = tool_auth_service.retrieve_auth_token(request, session)
        except Exception as e:
            redirect_err = f"{redirect_uri}?error={quote(str(e))}"
            logger.error(e)
            return RedirectResponse(redirect_err)

        if err:
            redirect_err = f"{redirect_uri}?error={quote(err)}"
            logger.error(err)
            return RedirectResponse(redirect_err)

    response = RedirectResponse(redirect_uri)

    return response
