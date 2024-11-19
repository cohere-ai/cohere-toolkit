from fastapi.testclient import TestClient

from backend.database_models.user import User
from backend.model_deployments.azure import AzureDeployment
from backend.tests.unit.model_deployments.mock_deployments import MockAzureDeployment


def test_streamed_chat(
    session_client_chat: TestClient,
    user: User,
    mock_azure_deployment,
    mock_available_model_deployments,
):
    deployment = mock_azure_deployment.return_value
    response = session_client_chat.post(
        "/v1/chat-stream",
        headers={
            "User-Id": user.id,
            "Deployment-Name": AzureDeployment.name(),
        },
        json={"message": "Hello", "max_tokens": 10},
    )

    assert response.status_code == 200
    assert type(deployment) is MockAzureDeployment


def test_non_streamed_chat(
    session_client_chat: TestClient,
    user: User,
    mock_azure_deployment,
):
    deployment = mock_azure_deployment.return_value
    response = session_client_chat.post(
        "/v1/chat",
        headers={
            "User-Id": user.id,
            "Deployment-Name": AzureDeployment.name(),
        },
        json={"message": "Hello", "max_tokens": 10},
    )

    assert response.status_code == 200
    assert type(deployment) is MockAzureDeployment
