import os
from distutils.util import strtobool

from fastapi import APIRouter

from backend.config.config import get_feature_flag
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
            get_feature_flag(
                "use_experimental_langchain", "USE_EXPERIMENTAL_LANGCHAIN", False
            )
        ),
        "USE_AGENTS_VIEW": get_feature_flag(
            "use_agents_view", "USE_AGENTS_VIEW", False
        ),
    }
    return experimental_features
