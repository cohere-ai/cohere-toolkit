from fastapi import APIRouter, Depends

from backend.config.routers import RouterName
from backend.config.settings import Settings
from backend.schemas.context import Context
from backend.services.context import get_context

router = APIRouter(
    prefix="/v1/experimental_features",
)

router.name = RouterName.EXPERIMENTAL_FEATURES


@router.get("/")
def list_experimental_features(ctx: Context = Depends(get_context)):
    """
    List all experimental features and if they are enabled

    Args:
        ctx (Context): Context object.
    Returns:
        Dict[str, bool]: Experimental feature and their isEnabled state
    """

    experimental_features = {
        "USE_EXPERIMENTAL_LANGCHAIN": Settings().feature_flags.use_experimental_langchain,
        "USE_AGENTS_VIEW": Settings().feature_flags.use_agents_view,
    }
    return experimental_features
