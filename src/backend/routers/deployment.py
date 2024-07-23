from fastapi import APIRouter, Depends, HTTPException, Response

from backend.config.deployments import AVAILABLE_MODEL_DEPLOYMENTS
from backend.config.routers import RouterName
from backend.schemas.deployment import Deployment, UpdateDeploymentEnv
from backend.services.env import update_env_file
from backend.services.logger import get_logger, send_log_message
from backend.services.request_validators import validate_env_vars

logger = get_logger()

router = APIRouter(
    prefix="/v1/deployments",
)
router.name = RouterName.DEPLOYMENT


@router.get("", response_model=list[Deployment])
def list_deployments(all: bool = False) -> list[Deployment]:
    """
    List all available deployments and their models.

    Returns:
        list[Deployment]: List of available deployment options.
    """
    send_log_message(
        logger,
        f"[Deployment] List deployment request"
        "debug",
    )
    available_deployments = [
        deployment
        for _, deployment in AVAILABLE_MODEL_DEPLOYMENTS.items()
        if all or deployment.is_available
    ]

    # No available deployments
    if not available_deployments:
        send_log_message(
            logger,
            f"[Deployment] No deployments available to list."
            "warning",
        )
        raise HTTPException(
            status_code=404,
            detail=(
                "No available deployments found. Please ensure that the required environment variables are set up correctly."
                " Refer to the README.md for detailed instructions.",
            ),
        )

    return available_deployments


@router.post("/{name}/set_env_vars", response_class=Response)
async def set_env_vars(
    name: str, env_vars: UpdateDeploymentEnv, valid_env_vars=Depends(validate_env_vars)
):
    """
    Set environment variables for the deployment.

    Returns:
        str: Empty string.
    """
    send_log_message(
        logger,
        f"[Deployment] Set environment variables request"
        "debug",
    )
    update_env_file(env_vars.env_vars)
