from backend.chat.custom.model_deployments.base import BaseDeployment
from backend.config.deployments import AVAILABLE_MODEL_DEPLOYMENTS, ModelDeploymentName


def get_deployment(deployment_name) -> BaseDeployment:
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
        return deployment.deployment_class()

    cohere_deployment = AVAILABLE_MODEL_DEPLOYMENTS.get(
        ModelDeploymentName.CoherePlatform
    )
    if cohere_deployment is not None and cohere_deployment.is_available:
        return cohere_deployment.deployment_class()
    else:
        raise ValueError(
            f"Deployment {deployment_name} is not supported, and no available deployments were found."
        )
