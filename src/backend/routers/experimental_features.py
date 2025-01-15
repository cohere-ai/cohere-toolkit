from fastapi import APIRouter, Depends

from backend.config.routers import RouterName
from backend.config.settings import Settings
from backend.schemas.context import Context
from backend.services.context import get_context

router = APIRouter(
    prefix="/v1/experimental_features",
    tags=[RouterName.EXPERIMENTAL_FEATURES],
)

router.name = RouterName.EXPERIMENTAL_FEATURES


@router.get("/")
def list_experimental_features(ctx: Context = Depends(get_context)) -> dict[str, bool]:
    """
    List all experimental features and if they are enabled
    """
    experimental_features = {
        "USE_AGENTS_VIEW": Settings().get('feature_flags.use_agents_view'),
        "USE_TEXT_TO_SPEECH_SYNTHESIS": bool(Settings().get('google_cloud.api_key')),
    }
    return experimental_features
