from unittest.mock import patch

import pytest
from sqlalchemy.orm import Session

from backend.models.user import User
from backend.tests.factories import get_factory
from backend.tests.model_deployments.mock_deployments.mock_cohere_platform import (
    MockCohereDeployment,
)
from backend.tests.model_deployments.mock_deployments.mock_sagemaker import (
    MockSageMakerDeployment,
)


@pytest.fixture()
def user(session_chat: Session) -> User:
    return get_factory("User", session_chat).create()


@pytest.fixture()
def mock_cohere_deployment():
    with patch("backend.chat.custom.custom.get_deployment") as mock:
        mock.return_value = MockCohereDeployment()
        yield mock


@pytest.fixture()
def mock_sagemaker_deployment():
    with patch("backend.chat.custom.custom.get_deployment") as mock:
        mock.return_value = MockSageMakerDeployment()
        yield mock
