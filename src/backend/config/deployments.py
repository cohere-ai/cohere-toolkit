from enum import StrEnum

from backend.config.settings import Settings
from backend.model_deployments import (
    AzureDeployment,
    BedrockDeployment,
    CohereDeployment,
    SageMakerDeployment,
    SingleContainerDeployment,
)
from backend.model_deployments.azure import AZURE_ENV_VARS
from backend.model_deployments.base import BaseDeployment
from backend.model_deployments.bedrock import BEDROCK_ENV_VARS
from backend.model_deployments.cohere_platform import COHERE_ENV_VARS
from backend.model_deployments.sagemaker import SAGE_MAKER_ENV_VARS
from backend.model_deployments.single_container import SC_ENV_VARS
from backend.schemas.deployment import Deployment
from backend.services.logger.utils import LoggerFactory

logger = LoggerFactory().get_logger()


class ModelDeploymentName(StrEnum):
    CoherePlatform = "Cohere Platform"
    SageMaker = "SageMaker"
    Azure = "Azure"
    Bedrock = "Bedrock"
    SingleContainer = "Single Container"


use_community_features = Settings().feature_flags.use_community_features

# TODO names in the map below should not be the display names but ids
ALL_MODEL_DEPLOYMENTS = {
    ModelDeploymentName.CoherePlatform: Deployment(
        id="cohere_platform",
        name=ModelDeploymentName.CoherePlatform,
        deployment_class=CohereDeployment,
        models=CohereDeployment.list_models(),
        is_available=CohereDeployment.is_available(),
        env_vars=COHERE_ENV_VARS,
    ),
    ModelDeploymentName.SingleContainer: Deployment(
        id="single_container",
        name=ModelDeploymentName.SingleContainer,
        deployment_class=SingleContainerDeployment,
        models=SingleContainerDeployment.list_models(),
        is_available=SingleContainerDeployment.is_available(),
        env_vars=SC_ENV_VARS,
    ),
    ModelDeploymentName.SageMaker: Deployment(
        id="sagemaker",
        name=ModelDeploymentName.SageMaker,
        deployment_class=SageMakerDeployment,
        models=SageMakerDeployment.list_models(),
        is_available=SageMakerDeployment.is_available(),
        env_vars=SAGE_MAKER_ENV_VARS,
    ),
    ModelDeploymentName.Azure: Deployment(
        id="azure",
        name=ModelDeploymentName.Azure,
        deployment_class=AzureDeployment,
        models=AzureDeployment.list_models(),
        is_available=AzureDeployment.is_available(),
        env_vars=AZURE_ENV_VARS,
    ),
    ModelDeploymentName.Bedrock: Deployment(
        id="bedrock",
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
            logger.warning(
                event="[Deployments] No available community deployments have been configured"
            )

    deployments = Settings().deployments.enabled_deployments
    if deployments is not None and len(deployments) > 0:
        return {
            key: value
            for key, value in ALL_MODEL_DEPLOYMENTS.items()
            if value.id in Settings().deployments.enabled_deployments
        }

    return ALL_MODEL_DEPLOYMENTS


def get_default_deployment(**kwargs) -> BaseDeployment:
    # Fallback to the first available deployment
    fallback = None
    for deployment in AVAILABLE_MODEL_DEPLOYMENTS.values():
        if deployment.is_available:
            fallback = deployment.deployment_class(**kwargs)
            break

    default = Settings().deployments.default_deployment
    if default:
        return next(
            (
                v.deployment_class(**kwargs)
                for k, v in AVAILABLE_MODEL_DEPLOYMENTS.items()
                if v.id == default
            ),
            fallback,
        )
    else:
        return fallback


AVAILABLE_MODEL_DEPLOYMENTS = get_available_deployments()
