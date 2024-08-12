from fastapi import APIRouter, Depends, HTTPException, Response

from backend.config.deployments import AVAILABLE_MODEL_DEPLOYMENTS
from backend.config.routers import RouterName
from backend.crud import deployment as deployment_crud
from backend.database_models import Deployment
from backend.database_models.database import DBSessionDep
from backend.schemas.context import Context
from backend.schemas.deployment import DeleteDeployment
from backend.schemas.deployment import Deployment as DeploymentSchema
from backend.schemas.deployment import (
    DeploymentCreate,
    DeploymentUpdate,
    UpdateDeploymentEnv,
)
from backend.services.context import get_context
from backend.services.env import update_env_file
from backend.services.request_validators import (
    validate_create_deployment_request,
    validate_env_vars,
)

router = APIRouter(
    prefix="/v1/deployments",
)
router.name = RouterName.DEPLOYMENT


@router.post(
    "",
    response_model=DeploymentSchema,
    dependencies=[Depends(validate_create_deployment_request)],
)
def create_deployment(
    deployment: DeploymentCreate, session: DBSessionDep
) -> DeploymentSchema:
    """
    Create a new deployment.

    Args:
        deployment (DeploymentCreate): Deployment data to be created.
        session (DBSessionDep): Database session.

    Returns:
        DeploymentSchema: Created deployment.
    """
    try:
        return DeploymentSchema.custom_transform(
            deployment_crud.create_deployment(session, deployment)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{deployment_id}", response_model=DeploymentSchema)
def update_deployment(
    deployment_id: str, new_deployment: DeploymentUpdate, session: DBSessionDep
) -> DeploymentSchema:
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
        raise HTTPException(status_code=404, detail="Deployment not found")

    return DeploymentSchema.custom_transform(
        deployment_crud.update_deployment(session, deployment, new_deployment)
    )


@router.get("/{deployment_id}", response_model=DeploymentSchema)
def get_deployment(deployment_id: str, session: DBSessionDep) -> DeploymentSchema:
    """
    Get a deployment by ID.

    Returns:
        Deployment: Deployment with the given ID.
    """
    deployment = deployment_crud.get_deployment(session, deployment_id)
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return DeploymentSchema.custom_transform(deployment)


@router.get("", response_model=list[DeploymentSchema])
def list_deployments(
    session: DBSessionDep, all: bool = False, ctx: Context = Depends(get_context)
) -> list[DeploymentSchema]:
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

    if all:
        available_deployments = [
            DeploymentSchema.custom_transform(_)
            for _ in deployment_crud.get_deployments(session)
        ]

    else:
        available_deployments = [
            DeploymentSchema.custom_transform(_)
            for _ in deployment_crud.get_available_deployments(session)
        ]

    if not available_deployments:
        available_deployments = [
            deployment
            for _, deployment in AVAILABLE_MODEL_DEPLOYMENTS.items()
            if all or deployment.is_available
        ]

    # No available deployments
    if not available_deployments:
        logger.warning(
            event=f"[Deployment] No deployments available to list.",
        )
        raise HTTPException(
            status_code=404,
            detail=(
                "No available deployments found. Please ensure that the required environment variables are set up correctly."
                " Refer to the README.md for detailed instructions.",
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
        raise HTTPException(
            status_code=404, detail=f"Deployment with ID: {deployment_id} not found."
        )

    deployment_crud.delete_deployment(session, deployment_id)

    return DeleteDeployment()


@router.post("/{name}/set_env_vars", response_class=Response)
async def set_env_vars(
    name: str,
    env_vars: UpdateDeploymentEnv,
    valid_env_vars=Depends(validate_env_vars),
    ctx: Context = Depends(get_context),
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
    update_env_file(env_vars.env_vars)
