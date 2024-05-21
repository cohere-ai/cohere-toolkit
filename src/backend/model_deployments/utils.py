import os
from backend.config.deployments import AVAILABLE_MODEL_DEPLOYMENTS
from backend.model_deployments.base import BaseDeployment


def get_deployment(deployment_name, model_config) -> BaseDeployment:
    """Get the deployment implementation.

    Args:
        deployment (str): Deployment name.

    Returns:
        BaseDeployment: Deployment implementation instance based on the deployment name.

    Raises:
        ValueError: If the deployment is not supported.
    """
    deployment = AVAILABLE_MODEL_DEPLOYMENTS.get(deployment_name)

    # Check provided deployment against config const
    if deployment is not None and deployment.is_available:
        return deployment.deployment_class(**deployment.kwargs)

    # Fallback to first available deployment
    for deployment in AVAILABLE_MODEL_DEPLOYMENTS.values():
        if deployment.is_available:
            return deployment.deployment_class(model_config)

    raise ValueError(
        f"Deployment {deployment_name} is not supported, and no available deployments were found."
    )


def get_model_config_var(var_name: str, model_config: dict) -> str:
    """Get the model config variable.

    Args:
        var_name (str): Variable name.
        model_config (dict): Model config.

    Returns:
        str: Model config variable value.

    """
    return (
        model_config[var_name]
        if model_config.get(var_name)
        else os.environ.get(var_name)
    )
