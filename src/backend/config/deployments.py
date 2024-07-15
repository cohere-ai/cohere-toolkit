import logging
import os
from distutils.util import strtobool
from enum import StrEnum

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


ALL_MODEL_DEPLOYMENTS = {
    ModelDeploymentName.CoherePlatform: Deployment(
        name=ModelDeploymentName.CoherePlatform,
        deployment_class=CohereDeployment,
        models=CohereDeployment.list_models(),
        is_available=CohereDeployment.is_available(),
        env_vars=COHERE_ENV_VARS,
    ),
    ModelDeploymentName.SingleContainer: Deployment(
        name=ModelDeploymentName.SingleContainer,
        deployment_class=SingleContainerDeployment,
        models=SingleContainerDeployment.list_models(),
        is_available=SingleContainerDeployment.is_available(),
        env_vars=SC_ENV_VARS,
    ),
    ModelDeploymentName.SageMaker: Deployment(
        name=ModelDeploymentName.SageMaker,
        deployment_class=SageMakerDeployment,
        models=SageMakerDeployment.list_models(),
        is_available=SageMakerDeployment.is_available(),
        env_vars=SAGE_MAKER_ENV_VARS,
    ),
    ModelDeploymentName.Azure: Deployment(
        name=ModelDeploymentName.Azure,
        deployment_class=AzureDeployment,
        models=AzureDeployment.list_models(),
        is_available=AzureDeployment.is_available(),
        env_vars=AZURE_ENV_VARS,
    ),
    ModelDeploymentName.Bedrock: Deployment(
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

    return ALL_MODEL_DEPLOYMENTS


AVAILABLE_MODEL_DEPLOYMENTS = get_available_deployments()
