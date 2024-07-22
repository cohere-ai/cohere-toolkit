import logging
import os
from distutils.util import strtobool
from enum import StrEnum

from backend.config.config import Configuration
from backend.model_deployments import (
    AzureDeployment,
    BedrockDeployment,
    CohereDeployment,
    SageMakerDeployment,
    SingleContainerDeployment,
)
from backend.model_deployments.azure import AZURE_ENV_VARS
from backend.model_deployments.bedrock import BEDROCK_ENV_VARS
from backend.model_deployments.cohere_platform import COHERE_ENV_VARS
from backend.model_deployments.sagemaker import SAGE_MAKER_ENV_VARS
from backend.model_deployments.single_container import SC_ENV_VARS
from backend.schemas.deployment import Deployment

class ModelDeploymentName(StrEnum):
    CoherePlatform = "Cohere Platform"
    SageMaker = "SageMaker"
    Azure = "Azure"
    Bedrock = "Bedrock"
    SingleContainer = "Single Container"


use_community_features = bool(strtobool(os.getenv("USE_COMMUNITY_FEATURES", "false")))

# TODO names in the map below should not be the display names but ids 
ALL_MODEL_DEPLOYMENTS = {
    ModelDeploymentName.CoherePlatform: Deployment(
        id = "cohere_platform",
        name=ModelDeploymentName.CoherePlatform,
        deployment_class=CohereDeployment,
        models=CohereDeployment.list_models(),
        is_available=CohereDeployment.is_available(),
        env_vars=COHERE_ENV_VARS,
    ),
    ModelDeploymentName.SingleContainer: Deployment(
        id = "single_container",
        name=ModelDeploymentName.SingleContainer,
        deployment_class=SingleContainerDeployment,
        models=SingleContainerDeployment.list_models(),
        is_available=SingleContainerDeployment.is_available(),
        env_vars=SC_ENV_VARS,
    ),
    ModelDeploymentName.SageMaker: Deployment(
        id = "sagemaker",
        name=ModelDeploymentName.SageMaker,
        deployment_class=SageMakerDeployment,
        models=SageMakerDeployment.list_models(),
        is_available=SageMakerDeployment.is_available(),
        env_vars=SAGE_MAKER_ENV_VARS,
    ),
    ModelDeploymentName.Azure: Deployment(
        id = "azure",
        name=ModelDeploymentName.Azure,
        deployment_class=AzureDeployment,
        models=AzureDeployment.list_models(),
        is_available=AzureDeployment.is_available(),
        env_vars=AZURE_ENV_VARS,
    ),
    ModelDeploymentName.Bedrock: Deployment(
        id = "bedrock",
        name=ModelDeploymentName.Bedrock,
        deployment_class=BedrockDeployment,
        models=BedrockDeployment.list_models(),
        is_available=BedrockDeployment.is_available(),
        env_vars=BEDROCK_ENV_VARS,
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

    if Configuration.deployment_config.get("enabled_deployments"):
        return {
            key: value
            for key, value in ALL_MODEL_DEPLOYMENTS.items()
            if value.id in Configuration.deployment_config.get("enabled_deployments")
        }

    return ALL_MODEL_DEPLOYMENTS

# TODO test
def get_default_deployment(**kwargs) -> ModelDeploymentName:
    # Fallback to the first available deployment
    for deployment in AVAILABLE_MODEL_DEPLOYMENTS.values():
        if deployment.is_available:
            fallback = deployment.deployment_class(**kwargs)
            break

    default = Configuration.deployment_config.get("default_deployment")
    if default:
        return next((k for k, v in AVAILABLE_MODEL_DEPLOYMENTS.items() if v.id == default), fallback)
    else :
        return fallback
    

AVAILABLE_MODEL_DEPLOYMENTS = get_available_deployments()
