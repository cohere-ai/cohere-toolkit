import os
import sys

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.services.auth import BasicAuthentication, GoogleOAuth, OpenIDConnect

load_dotenv()

SKIP_AUTH = os.getenv("SKIP_AUTH", None)
# Add Auth strategy classes here to enable them
# Ex: [BasicAuthentication]
ENABLED_AUTH_STRATEGIES = []
if "pytest" in sys.modules or SKIP_AUTH == "true":
    ENABLED_AUTH_STRATEGIES = []

# Define the mapping from Auth strategy name to class obj - does not need to be manually modified.
# During runtime, this will create an instance of each enabled strategy class.
# Ex: {"Basic": BasicAuthentication()}
ENABLED_AUTH_STRATEGY_MAPPING = {cls.NAME: cls() for cls in ENABLED_AUTH_STRATEGIES}

# Token to authorize migration requests
MIGRATE_TOKEN = os.environ.get("MIGRATE_TOKEN", None)

security = HTTPBearer()


def verify_migrate_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not MIGRATE_TOKEN or credentials.credentials != MIGRATE_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def is_authentication_enabled() -> bool:
    """
    Check whether any form of authentication was enabled.

    Returns:
        bool: Whether authentication is enabled.
    """
    if ENABLED_AUTH_STRATEGIES:
        return True

    return False


async def get_auth_strategy_endpoints() -> None:
    """
    Fetches the endpoints for each enabled strategy.
    """
    for strategy in ENABLED_AUTH_STRATEGY_MAPPING.values():
        if hasattr(strategy, "get_endpoints"):
            await strategy.get_endpoints()
