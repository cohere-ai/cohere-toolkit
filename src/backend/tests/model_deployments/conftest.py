from unittest.mock import patch

import pytest
from sqlalchemy.orm import Session

from backend.database_models.user import User
from backend.tests.factories import get_factory
from backend.tests.model_deployments.mock_deployments import (
    MockAzureDeployment,
    MockBedrockDeployment,
    MockCohereDeployment,
    MockSageMakerDeployment,
    MockSingleContainerDeployment,
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
def mock_single_container_deployment():
    with patch("backend.chat.custom.custom.get_deployment") as mock:
        mock.return_value = MockSingleContainerDeployment()
        yield mock


@pytest.fixture()
def mock_sagemaker_deployment():
    with patch("backend.chat.custom.custom.get_deployment") as mock:
        mock.return_value = MockSageMakerDeployment()
        yield mock


@pytest.fixture()
def mock_azure_deployment():
    with patch("backend.chat.custom.custom.get_deployment") as mock:
        mock.return_value = MockAzureDeployment()
        yield mock


@pytest.fixture()
def mock_bedrock_deployment():
    with patch("backend.chat.custom.custom.get_deployment") as mock:
        mock.return_value = MockBedrockDeployment()
        yield mock
