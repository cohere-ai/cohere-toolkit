from backend.config.settings import Settings
from backend.model_deployments.base import BaseDeployment
from backend.services.logger.utils import LoggerFactory

logger = LoggerFactory().get_logger()


ALL_MODEL_DEPLOYMENTS = { d.name(): d for d in BaseDeployment.__subclasses__() }


def get_available_deployments() -> list[type[BaseDeployment]]:
    installed_deployments = list(ALL_MODEL_DEPLOYMENTS.values())

    if Settings().get("feature_flags.use_community_features"):
        try:
            from community.config.deployments import (
                AVAILABLE_MODEL_DEPLOYMENTS as COMMUNITY_DEPLOYMENTS_SETUP,
            )
            installed_deployments.extend(COMMUNITY_DEPLOYMENTS_SETUP.values())
        except ImportError as e:
            logger.warning(
                event="[Deployments] No available community deployments have been configured", ex=e
            )

    enabled_deployment_ids = Settings().get("deployments.enabled_deployments")
    if enabled_deployment_ids:
        return [
            deployment
            for deployment in installed_deployments
            if deployment.id() in enabled_deployment_ids
        ]

    return installed_deployments

AVAILABLE_MODEL_DEPLOYMENTS = get_available_deployments()
