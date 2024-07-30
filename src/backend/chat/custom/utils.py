from typing import Any

from backend.config.deployments import (
    AVAILABLE_MODEL_DEPLOYMENTS,
    get_default_deployment,
)
from backend.model_deployments.base import BaseDeployment
from backend.schemas.context import Context


def get_deployment(name: str, ctx: Context, **kwargs: Any) -> BaseDeployment:
    """Get the deployment implementation.

    Args:
        deployment (str): Deployment name.

    Returns:
        BaseDeployment: Deployment implementation instance based on the deployment name.

    Raises:
        ValueError: If the deployment is not supported.
    """
    kwargs["ctx"] = ctx
    deployment = AVAILABLE_MODEL_DEPLOYMENTS.get(name)

    # Check provided deployment against config const
    if deployment is not None:
        return deployment.deployment_class(**kwargs, **deployment.kwargs)

    # Fallback to first available deployment
    default = get_default_deployment(**kwargs)
    if default is not None:
        return default

    raise ValueError(
        f"Deployment {name} is not supported, and no available deployments were found."
    )
