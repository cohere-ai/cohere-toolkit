import os
from distutils.util import strtobool

from fastapi import APIRouter

from backend.config.routers import RouterName

router = APIRouter(
    prefix="/v1/experimental_features",
)

router.name = RouterName.EXPERIMENTAL_FEATURES


@router.get("/")
def list_experimental_features():
    """
    List all experimental features and if they are enabled

    Returns:
        Dict[str, bool]: Experimental feature and their isEnabled state
    """

    experimental_features = {
        "USE_EXPERIMENTAL_LANGCHAIN": bool(
            strtobool(os.getenv("USE_EXPERIMENTAL_LANGCHAIN", "false"))
        ),
        "USE_AGENTS_VIEW": bool(strtobool(os.getenv("USE_AGENTS_VIEW", "false"))),
    }
    return experimental_features
