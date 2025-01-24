from typing import Any

from sqlalchemy.orm import Session

from backend.exceptions import DeploymentNotFoundError
from backend.model_deployments.base import BaseDeployment
from backend.schemas.context import Context
from backend.services import deployment as deployment_service


def get_deployment(name: str, session: Session, ctx: Context, **kwargs: Any) -> BaseDeployment:
    """
    Get the deployment implementation instance.

    Args:
        name (str): Deployment name.
        session (Session): SQLAchemy db session for the request.
        ctx (Context): Request context
        **kwargs (Any): Keyword arguments.

    Returns:
        BaseDeployment: Deployment implementation instance based on the deployment name.
    """
    kwargs["ctx"] = ctx
    try:
        deployment = deployment_service.get_deployment_instance_by_name(session, name, **kwargs)
    except (DeploymentNotFoundError, Exception):
        deployment = deployment_service.get_default_deployment_instance(**kwargs)

    return deployment
