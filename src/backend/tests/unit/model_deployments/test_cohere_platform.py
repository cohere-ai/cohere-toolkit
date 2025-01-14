import pytest
from fastapi.testclient import TestClient

from backend.database_models.user import User
from backend.model_deployments.cohere_platform import CohereDeployment
from backend.tests.unit.model_deployments.mock_deployments import MockCohereDeployment

pytest.skip("These tests are already covered by tests in integration/routers/test_chat.py and are breaking other unit tests. They should be converted to smaller-scoped unit tests.", allow_module_level=True)

def test_streamed_chat(
    session_client_chat: TestClient,
    user: User,
    mock_cohere_deployment,
    mock_available_model_deployments,
):
    deployment = mock_cohere_deployment.return_value
    response = session_client_chat.post(
        "/v1/chat-stream",
        headers={
            "User-Id": user.id,
            "Deployment-Name": CohereDeployment.name(),
        },
        json={"message": "Hello", "max_tokens": 10},
    )

    assert response.status_code == 200
    assert type(deployment) is MockCohereDeployment


def test_non_streamed_chat(
    session_client_chat: TestClient,
    user: User,
    mock_cohere_deployment,
):
    deployment = mock_cohere_deployment.return_value
    response = session_client_chat.post(
        "/v1/chat",
        headers={
            "User-Id": user.id,
            "Deployment-Name": CohereDeployment.name(),
        },
        json={"message": "Hello", "max_tokens": 10},
    )

    assert response.status_code == 200
    assert type(deployment) is MockCohereDeployment
