import os
from distutils.util import strtobool

from fastapi import APIRouter, Depends

from backend.models import get_session

router = APIRouter(
    prefix="/experimental_features",
    dependencies=[Depends(get_session)],
)


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
        )
    }
    return experimental_features
