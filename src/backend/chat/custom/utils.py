from typing import Any

from backend.config.deployments import AVAILABLE_MODEL_DEPLOYMENTS
from backend.model_deployments.base import BaseDeployment


def get_deployment(name, **kwargs: Any) -> BaseDeployment:
    """Get the deployment implementation.

    Args:
        deployment (str): Deployment name.

    Returns:
        BaseDeployment: Deployment implementation instance based on the deployment name.

    Raises:
        ValueError: If the deployment is not supported.
    """
    deployment = AVAILABLE_MODEL_DEPLOYMENTS.get(name)

    # Check provided deployment against config const
    if deployment is not None:
        return deployment.deployment_class(**kwargs, **deployment.kwargs)

    # Fallback to first available deployment
    for deployment in AVAILABLE_MODEL_DEPLOYMENTS.values():
        if deployment.is_available:
            return deployment.deployment_class(**kwargs)

    raise ValueError(
        f"Deployment {name} is not supported, and no available deployments were found."
    )
