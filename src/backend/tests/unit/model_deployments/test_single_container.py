from fastapi.testclient import TestClient

from backend.database_models.user import User
from backend.model_deployments.single_container import SingleContainerDeployment
from backend.tests.unit.model_deployments.mock_deployments import (
    MockSingleContainerDeployment,
)


def test_streamed_chat(
    session_client_chat: TestClient,
    user: User,
    mock_single_container_deployment,
    mock_available_model_deployments,
):
    deployment = mock_single_container_deployment.return_value
    response = session_client_chat.post(
        "/v1/chat-stream",
        headers={
            "User-Id": user.id,
            "Deployment-Name": SingleContainerDeployment.name(),
        },
        json={"message": "Hello", "max_tokens": 10},
    )

    assert response.status_code == 200
    assert type(deployment) is MockSingleContainerDeployment


def test_non_streamed_chat(
    session_client_chat: TestClient, user: User, mock_single_container_deployment
):
    deployment = mock_single_container_deployment.return_value
    response = session_client_chat.post(
        "/v1/chat",
        headers={
            "User-Id": user.id,
            "Deployment-Name": SingleContainerDeployment.name(),
        },
        json={"message": "Hello", "max_tokens": 10},
    )

    assert response.status_code == 200
    assert type(deployment) is MockSingleContainerDeployment
