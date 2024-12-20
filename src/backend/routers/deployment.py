from fastapi import APIRouter, Depends, HTTPException

from backend.config.routers import RouterName
from backend.crud import deployment as deployment_crud
from backend.database_models.database import DBSessionDep
from backend.exceptions import DeploymentNotFoundError
from backend.schemas.context import Context
from backend.schemas.deployment import (
    DeleteDeployment,
    DeploymentCreate,
    DeploymentDefinition,
    DeploymentUpdate,
    UpdateDeploymentEnv,
)
from backend.services import deployment as deployment_service
from backend.services.context import get_context
from backend.services.logger.utils import LoggerFactory
from backend.services.request_validators import (
    validate_create_deployment_request,
    validate_env_vars,
)

logger = LoggerFactory().get_logger()

router = APIRouter(
    prefix="/v1/deployments",
)
router.name = RouterName.DEPLOYMENT


@router.post(
    "",
    response_model=DeploymentDefinition,
    dependencies=[Depends(validate_create_deployment_request)],
)
def create_deployment(
    deployment: DeploymentCreate, session: DBSessionDep
) -> DeploymentDefinition:
    """
    Create a new deployment.

    Args:
        deployment (DeploymentCreate): Deployment data to be created.
        session (DBSessionDep): Database session.

    Returns:
        DeploymentDefinition: Created deployment.
    """
    try:
        created = DeploymentDefinition.from_db_deployment(
            deployment_crud.create_deployment(session, deployment)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return mask_deployment_secrets(created)


@router.put("/{deployment_id}", response_model=DeploymentDefinition)
def update_deployment(
    deployment_id: str, new_deployment: DeploymentUpdate, session: DBSessionDep
) -> DeploymentDefinition:
    """
    Update a deployment.

    Args:
        deployment_id (str): Deployment ID.
        new_deployment (DeploymentUpdate): Deployment data to be updated.
        session (DBSessionDep): Database session.

    Returns:
        Deployment: Updated deployment.

    Raises:
        HTTPException: If deployment not found.
    """
    deployment = deployment_crud.get_deployment(session, deployment_id)
    if not deployment:
        raise DeploymentNotFoundError(deployment_id=deployment_id)

    return mask_deployment_secrets(DeploymentDefinition.from_db_deployment(
        deployment_crud.update_deployment(session, deployment, new_deployment)
    ))


@router.get("/{deployment_id}", response_model=DeploymentDefinition)
def get_deployment(deployment_id: str, session: DBSessionDep) -> DeploymentDefinition:
    """
    Get a deployment by ID.

    Returns:
        Deployment: Deployment with the given ID.
    """
    return mask_deployment_secrets(
        deployment_service.get_deployment_definition(session, deployment_id)
    )


@router.get("", response_model=list[DeploymentDefinition])
def list_deployments(
    session: DBSessionDep, all: bool = False, ctx: Context = Depends(get_context)
) -> list[DeploymentDefinition]:
    """
    List all available deployments and their models.

    Args:
        session (DBSessionDep)
        all (bool): Include all deployments, regardless of availability.
        ctx (Context): Context object.
    Returns:
        list[Deployment]: List of available deployment options.
    """
    logger = ctx.get_logger()

    installed_deployments = deployment_service.get_deployment_definitions(session)
    available_deployments = [
        mask_deployment_secrets(deployment) for deployment in installed_deployments if deployment.is_available or all
    ]

    if not available_deployments:
        logger.warning(
            event="[Deployment] No deployments available to list.",
        )
        raise HTTPException(
            status_code=404,
            detail=(
                "No available deployments found. Please ensure that the required variables in your configuration.yaml "
                "and secrets.yaml are set up correctly. "
                "Refer to the README.md for detailed instructions.",
            ),
        )

    return available_deployments


@router.delete("/{deployment_id}")
async def delete_deployment(
    deployment_id: str, session: DBSessionDep
) -> DeleteDeployment:
    """
    Delete a deployment by ID.

    Args:
        deployment_id (str): Deployment ID.
        session (DBSessionDep): Database session.
        request (Request): Request object.

    Returns:
        DeleteDeployment: Empty response.

    Raises:
        HTTPException: If the deployment with the given ID is not found.
    """
    deployment = deployment_crud.get_deployment(session, deployment_id)

    if not deployment:
        raise DeploymentNotFoundError(deployment_id=deployment_id)

    deployment_crud.delete_deployment(session, deployment_id)

    return DeleteDeployment()


@router.post("/{deployment_id}/update_config")
async def update_config(
    deployment_id: str,
    session: DBSessionDep,
    env_vars: UpdateDeploymentEnv,
    valid_env_vars = Depends(validate_env_vars),
    # ctx: Context = Depends(get_context),
):
    """
    Set environment variables for the deployment.

    Args:
        name (str): Deployment name.
        env_vars (UpdateDeploymentEnv): Environment variables to set.
        valid_env_vars (str): Validated environment variables.
        ctx (Context): Context object.
    Returns:
        str: Empty string.
    """
    return mask_deployment_secrets(
        deployment_service.update_config(session, deployment_id, valid_env_vars)
    )


def mask_deployment_secrets(deployment: DeploymentDefinition) -> DeploymentDefinition:
    deployment.config = {key: "*****" if val else "" for [key, val] in deployment.config.items()}
    return deployment
