import pytest
from fastapi.testclient import TestClient

from backend.database_models.user import User
from backend.model_deployments.sagemaker import SageMakerDeployment
from backend.tests.unit.model_deployments.mock_deployments import (
    MockSageMakerDeployment,
)


def test_streamed_chat(
    session_client_chat: TestClient,
    user: User,
    mock_sagemaker_deployment,
    mock_available_model_deployments,
):
    deployment = mock_sagemaker_deployment.return_value
    response = session_client_chat.post(
        "/v1/chat-stream",
        headers={"User-Id": user.id, "Deployment-Name": SageMakerDeployment.name()},
        json={"message": "Hello", "max_tokens": 10},
    )

    assert response.status_code == 200
    assert type(deployment) is MockSageMakerDeployment


@pytest.mark.skip("Non-streamed chat is not supported for SageMaker yet")
def test_non_streamed_chat(
    session_client_chat: TestClient, user: User, mock_sagemaker_deployment
):
    mock_sagemaker_deployment.return_value
    response = session_client_chat.post(
        "/v1/chat",
        headers={"User-Id": user.id, "Deployment-Name": SageMakerDeployment.name()},
        json={"message": "Hello", "max_tokens": 10},
    )

    assert response.status_code == 200
