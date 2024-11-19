from unittest.mock import Mock

from backend.services.deployment import (
    get_default_deployment,
)
from backend.tests.unit.model_deployments.mock_deployments.mock_cohere_platform import (
    MockCohereDeployment,
)


def test_get_default_deployment(mock_available_model_deployments: Mock) -> None:
    default_deployment = get_default_deployment()
    assert isinstance(default_deployment, MockCohereDeployment)
