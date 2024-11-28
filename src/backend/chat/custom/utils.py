from typing import Any

from backend.database_models.database import get_session
from backend.exceptions import DeploymentNotFoundError
from backend.model_deployments.base import BaseDeployment
from backend.schemas.context import Context
from backend.services import deployment as deployment_service


def get_deployment(name: str, ctx: Context, **kwargs: Any) -> BaseDeployment:
    """Get the deployment implementation.

    Args:
        deployment (str): Deployment name.

    Returns:
        BaseDeployment: Deployment implementation instance based on the deployment name.
    """
    kwargs["ctx"] = ctx
    try:
        session = next(get_session())
        deployment = deployment_service.get_deployment_by_name(session, name)
    except DeploymentNotFoundError:
        deployment = deployment_service.get_default_deployment(**kwargs)

    return deployment
