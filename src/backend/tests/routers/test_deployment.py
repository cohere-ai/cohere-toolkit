import re
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.config.deployments import AVAILABLE_MODEL_DEPLOYMENTS, ModelDeploymentName
from backend.database_models import Deployment


def test_create_deployment(session_client: TestClient) -> None:
    request_json = {
        "name": "TestDeployment",
        "default_deployment_config": {"COHERE_API_KEY": "test-api-key"},
        "deployment_class_name": "CohereDeployment",
        "description": "Test deployment",
        "is_community": False,
    }
    response = session_client.post(
        "/v1/deployments", json=request_json, headers={"User-Id": "1"}
    )
    assert response.status_code == 200
    deployment = response.json()
    assert deployment["name"] == request_json["name"]
    assert deployment["env_vars"] == ["COHERE_API_KEY"]
    assert deployment["is_available"]


def test_create_deployment_unique(session_client: TestClient) -> None:
    request_json = {
        "name": ModelDeploymentName.CoherePlatform,
        "default_deployment_config": {"COHERE_API_KEY": "test-api-key"},
        "deployment_class_name": "CohereDeployment",
    }

    response = session_client.post(
        "/v1/deployments", json=request_json, headers={"User-Id": "user-id"}
    )
    assert response.status_code == 400
    assert (
        f"Deployment {ModelDeploymentName.CoherePlatform} already exists."
        in response.json()["detail"]
    )


def test_create_deployment_invalid_deployment_class(session_client: TestClient) -> None:
    request_json = {
        "name": "TestDeployment1",
        "default_deployment_config": {"COHERE_API_KEY": "   "},
        "deployment_class_name": "InvalidDeployment",
        "description": "Test deployment",
        "is_community": False,
    }
    response = session_client.post(
        "/v1/deployments", json=request_json, headers={"User-Id": "1"}
    )
    assert response.status_code == 404
    assert (
        "Deployment class name InvalidDeployment not found."
        in response.json()["detail"]
    )


def test_list_deployments(session_client: TestClient, session: Session) -> None:
    response = session_client.get("/v1/deployments")
    assert response.status_code == 200
    deployments = response.json()
    db_deployments = session.query(Deployment).all()
    available_deployments = [
        deployment for deployment in db_deployments if deployment.is_available
    ]
    if len(available_deployments) == 0:
        available_deployments = [
            deployment
            for _, deployment in AVAILABLE_MODEL_DEPLOYMENTS.items()
            if deployment.is_available
        ]
    assert len(deployments) == len(available_deployments)
    for deployment in deployments:
        assert "name" in deployment
        assert "models" in deployment
        assert "env_vars" in deployment


def test_list_deployments_has_all_option(
    session_client: TestClient, session: Session
) -> None:
    response = session_client.get("/v1/deployments?all=1")
    assert response.status_code == 200
    deployments = response.json()
    db_deployments = session.query(Deployment).all()
    if len(db_deployments) == 0:
        db_deployments = [
            deployment for _, deployment in AVAILABLE_MODEL_DEPLOYMENTS.items()
        ]
    assert len(deployments) == len(db_deployments)


def test_list_deployments_no_available_models_404(
    session_client: TestClient, session: Session
) -> None:
    session.query(Deployment).delete()
    AVAILABLE_MODEL_DEPLOYMENTS.clear()
    response = session_client.get("/v1/deployments")
    assert response.status_code == 404
    assert response.json() == {
        "detail": [
            (
                "No available deployments found. Please ensure that the required environment variables are set up correctly. "
                "Refer to the README.md for detailed instructions."
            )
        ]
    }


def test_list_deployments_no_available_db_models_with_all_option(
    session_client: TestClient, session: Session, mock_available_model_deployments: Mock
) -> None:
    session.query(Deployment).delete()
    response = session_client.get("/v1/deployments?all=1")
    assert response.status_code == 200
    assert len(response.json()) == len(list(AVAILABLE_MODEL_DEPLOYMENTS))


def test_update_deployment(session_client: TestClient, session: Session) -> None:
    deployment = session.query(Deployment).first()
    request_json = {
        "name": "UpdatedDeployment",
        "default_deployment_config": {"COHERE_API_KEY": "test-api-key"},
        "deployment_class_name": "CohereDeployment",
        "description": "Updated deployment",
        "is_community": False,
    }
    response = session_client.put("/v1/deployments/" + deployment.id, json=request_json)
    assert response.status_code == 200
    updated_deployment = response.json()
    assert updated_deployment["name"] == request_json["name"]
    assert updated_deployment["env_vars"] == ["COHERE_API_KEY"]
    assert updated_deployment["is_available"]
    assert updated_deployment["description"] == request_json["description"]
    assert updated_deployment["is_community"] == request_json["is_community"]


def test_delete_deployment(session_client: TestClient, session: Session) -> None:
    deployment = session.query(Deployment).first()
    response = session_client.delete("/v1/deployments/" + deployment.id)
    deleted = session.query(Deployment).filter(Deployment.id == deployment.id).first()
    assert response.status_code == 200
    assert deleted is None
    assert response.json() == {}


def test_set_env_vars(
    client: TestClient, mock_available_model_deployments: Mock
) -> None:
    with patch("backend.services.env.set_key") as mock_set_key:
        response = client.post(
            "/v1/deployments/Cohere+Platform/set_env_vars",
            json={
                "env_vars": {
                    "COHERE_VAR_1": "TestCohereValue",
                },
            },
        )
    assert response.status_code == 200

    class EnvPathMatcher:
        def __eq__(self, other):
            return bool(re.match(r".*/?\.env$", other))

    mock_set_key.assert_called_with(
        EnvPathMatcher(),
        "COHERE_VAR_1",
        "TestCohereValue",
    )


def test_set_env_vars_with_invalid_deployment_name(
    client: TestClient, mock_available_model_deployments: Mock
):
    response = client.post("/v1/deployments/unknown/set_env_vars", json={})
    assert response.status_code == 404


def test_set_env_vars_with_var_for_other_deployment(
    client: TestClient, mock_available_model_deployments: Mock
) -> None:
    response = client.post(
        "/v1/deployments/Cohere+Platform/set_env_vars",
        json={
            "env_vars": {
                "SAGEMAKER_VAR_1": "TestSageMakerValue",
            },
        },
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Environment variables not valid for deployment: SAGEMAKER_VAR_1"
    }


def test_set_env_vars_with_invalid_var(
    client: TestClient, mock_available_model_deployments: Mock
) -> None:
    response = client.post(
        "/v1/deployments/Cohere+Platform/set_env_vars",
        json={
            "env_vars": {
                "API_KEY": "12345",
            },
        },
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Environment variables not valid for deployment: API_KEY"
    }
