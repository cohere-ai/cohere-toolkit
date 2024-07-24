from unittest.mock import Mock

from backend.config.deployments import (
    AVAILABLE_MODEL_DEPLOYMENTS,
    ModelDeploymentName,
    get_default_deployment,
)
from backend.model_deployments.cohere_platform import CohereDeployment
from backend.tests.model_deployments.mock_deployments.mock_cohere_platform import (
    MockCohereDeployment,
)


def test_get_default_deployment(mock_available_model_deployments: Mock) -> None:
    default_deployment = get_default_deployment()
    assert isinstance(default_deployment, MockCohereDeployment)
