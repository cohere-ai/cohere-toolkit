from fastapi.testclient import TestClient

from backend.config.deployments import ModelDeploymentName
from backend.database_models.user import User
from backend.schemas.cohere_chat import CohereChatRequest
from backend.tests.model_deployments.mock_deployments import MockBedrockDeployment


def test_streamed_chat(
    session_client_chat: TestClient,
    user: User,
    mock_bedrock_deployment,
    mock_available_model_deployments,
):
    deployment = mock_bedrock_deployment.return_value
    response = session_client_chat.post(
        "/v1/chat-stream",
        headers={
            "User-Id": user.id,
            "Deployment-Name": ModelDeploymentName.Bedrock,
        },
        json={"message": "Hello", "max_tokens": 10},
    )

    assert response.status_code == 200
    assert type(deployment) is MockBedrockDeployment


def test_non_streamed_chat(
    session_client_chat: TestClient,
    user: User,
    mock_bedrock_deployment,
    mock_available_model_deployments,
):
    deployment = mock_bedrock_deployment.return_value
    response = session_client_chat.post(
        "/v1/chat",
        headers={"User-Id": user.id, "Deployment-Name": ModelDeploymentName.Bedrock},
        json={"message": "Hello", "max_tokens": 10},
    )

    assert response.status_code == 200
