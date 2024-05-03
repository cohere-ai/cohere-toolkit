from fastapi import APIRouter, Depends, HTTPException
from starlette.requests import Request

from backend.config.auth import ENABLED_AUTH_STRATEGIES
from backend.models import get_session
from backend.models.database import DBSessionDep
from backend.schemas.auth import Login

# Define the mapping from Auth strategy name to class obj
# Ex: {"Basic": BasicAuthentication}
ENABLED_AUTH_STRATEGY_MAPPING = {cls.NAME: cls for cls in ENABLED_AUTH_STRATEGIES}

router = APIRouter(dependencies=[Depends(get_session)])


@router.get("/session")
def get_session(request: Request):
    """
    Retrievers the current session user.

    Args:
        request (Request): current Request object.

    Returns:
        session: current user session ({} if no active session)
    """
    return request.session


@router.post("/login")
async def login(request: Request, login: Login, session: DBSessionDep):
    """
    Logs user in, verifying their credentials and either setting the user session,
    or redirecting to /auth endpoint.

    Args:
        request (Request): current Request object.
        login (Login): Login payload.
        session (DBSessionDep): Database session.

    Returns:
        dict: On success.

    Raises:
        HTTPException: If the strategy or payload are invalid, or if the login fails.
    """
    strategy_name = login.strategy
    payload = login.payload

    # Check the strategy is valid and enabled
    if strategy_name not in ENABLED_AUTH_STRATEGY_MAPPING.keys():
        raise HTTPException(
            status_code=404, detail=f"Invalid Authentication strategy: {strategy_name}."
        )

    # Check that the payload required is given
    strategy = ENABLED_AUTH_STRATEGY_MAPPING[strategy_name]
    strategy_payload = strategy.get_required_payload()
    if not set(strategy_payload).issubset(payload):
        missing_keys = [key for key in strategy_payload if key not in payload.keys()]
        raise HTTPException(
            status_code=404,
            detail=f"Missing the following keys in the payload: {missing_keys}.",
        )

    # Do login
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
async def auth(request: Request):
    # TODO: Implement for OAuth strategies
    return {}


@router.get("/logout")
async def logout(request: Request):
    """
    Logs out the current user session.

    Args:
        request (Request): current Request object.

    Returns:
        dict: On success.
    """
    request.session.pop("user", None)

    return {}
