import logging
import os
from distutils.util import strtobool
from enum import StrEnum

from backend.chat.custom.model_deployments.azure import AzureDeployment
from backend.chat.custom.model_deployments.cohere_platform import CohereDeployment
from backend.chat.custom.model_deployments.sagemaker import SageMakerDeployment
from backend.schemas.deployment import Deployment


class ModelDeploymentName(StrEnum):
    CoherePlatform = "Cohere Platform"
    SageMaker = "SageMaker"
    Azure = "Azure"


use_community_features = bool(strtobool(os.getenv("USE_COMMUNITY_FEATURES", "false")))


ALL_MODEL_DEPLOYMENTS = {
    ModelDeploymentName.CoherePlatform: Deployment(
        name=ModelDeploymentName.CoherePlatform,
        deployment_class=CohereDeployment,
        models=CohereDeployment.list_models(),
        is_available=CohereDeployment.is_available(),
        env_vars=[
            "COHERE_API_KEY",
        ],
    ),
    ModelDeploymentName.SageMaker: Deployment(
        name=ModelDeploymentName.SageMaker,
        deployment_class=SageMakerDeployment,
        models=SageMakerDeployment.list_models(),
        is_available=SageMakerDeployment.is_available(),
        env_vars=[
            "SAGE_MAKER_REGION_NAME",
            "SAGE_MAKER_ENDPOINT_NAME",
            "SAGE_MAKER_PROFILE_NAME",
        ],
    ),
    ModelDeploymentName.Azure: Deployment(
        name=ModelDeploymentName.Azure,
        deployment_class=AzureDeployment,
        models=AzureDeployment.list_models(),
        is_available=AzureDeployment.is_available(),
        env_vars=[
            "AZURE_API_KEY",
            "AZURE_CHAT_ENDPOINT_URL",
        ],
    ),
}


def get_available_deployments() -> dict[ModelDeploymentName, Deployment]:
    if use_community_features:
        try:
            from community.config.deployments import (
                AVAILABLE_MODEL_DEPLOYMENTS as COMMUNITY_DEPLOYMENTS_SETUP,
            )

            model_deployments = ALL_MODEL_DEPLOYMENTS.copy()
            model_deployments.update(COMMUNITY_DEPLOYMENTS_SETUP)
            return model_deployments
        except ImportError:
            logging.warning(
                "Community deployments are not available. They can still be set up."
            )

    return ALL_MODEL_DEPLOYMENTS


AVAILABLE_MODEL_DEPLOYMENTS = get_available_deployments()
