import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.config.deployments import AVAILABLE_MODEL_DEPLOYMENTS, ModelDeploymentName
from backend.database_models import Model
from backend.tests.factories import get_factory


def test_create_model(session_client: TestClient, session: Session, deployment) -> None:
    request_json = {
        "name": "sagemaker-command-created",
        "cohere_name": "command",
        "description": "New model",
        "deployment_id": deployment.id,
    }

    response = session_client.post(
        "/v1/models", json=request_json, headers={"User-Id": "1"}
    )

    assert response.status_code == 200
    response_json = response.json()

    assert response_json["id"] is not None
    assert (
        "deployment_id" in response_json
        and response_json["deployment_id"] == deployment.id
    )
    assert request_json["name"] == response_json["name"]


def test_create_model_non_existing_deployment(
    session_client: TestClient, session: Session
) -> None:
    request_json = {
        "name": "sagemaker-command-created",
        "cohere_name": "command",
        "description": "New model",
        "deployment_id": "non-existing-deployment",
    }

    response = session_client.post(
        "/v1/models", json=request_json, headers={"User-Id": "1"}
    )
    response_json = response.json()

    assert response.status_code == 400
    assert (
        f"Deployment {request_json['deployment_id']} not found"
        in response_json["detail"]
    )


def test_update_model(session_client: TestClient, session: Session, deployment) -> None:
    request_json = {
        "name": "sagemaker-command-updated",
        "cohere_name": "command",
        "description": "Updated model",
    }
    model = get_factory("Model", session).create(deployment=deployment)
    response = session_client.put(
        f"/v1/models/{model.id}", json=request_json, headers={"User-Id": "1"}
    )

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["id"] == model.id
    assert request_json["name"] == response_json["name"]
    assert request_json["description"] == response_json["description"]
    assert model.deployment_id == response_json["deployment_id"]


def test_get_model(session_client: TestClient, session: Session, deployment) -> None:
    # Delete all models
    session.query(Model).delete()
    model = get_factory("Model", session).create(deployment=deployment)

    response = session_client.get(f"/v1/models/{model.id}")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["id"] == model.id
    assert response_json["name"] == model.name
    assert response_json["deployment_id"] == model.deployment_id


def test_get_model_non_existing(session_client: TestClient, session: Session) -> None:
    response = session_client.get(f"/v1/models/non-existing-id")
    assert response.status_code == 404
    response_json = response.json()
    assert "Model not found" in response_json["detail"]


def test_list_models(session_client: TestClient, session: Session, deployment) -> None:
    # Delete all models
    session.query(Model).delete()
    for _ in range(5):
        get_factory("Model", session).create(deployment=deployment)

    response = session_client.get("/v1/models")
    assert response.status_code == 200
    models = response.json()
    assert len(models) == 5


def test_list_models_empty(session_client: TestClient, session: Session) -> None:
    session.query(Model).delete()
    response = session_client.get("/v1/models")
    assert response.status_code == 200
    models = response.json()
    assert len(models) == 0


def test_list_models_with_pagination(
    session_client: TestClient, session: Session, deployment
) -> None:
    # Delete all models
    session.query(Model).delete()
    for i in range(10):
        get_factory("Model", session).create(
            name=f"Test Model {i}", deployment=deployment
        )

    response = session_client.get("/v1/models?offset=5&limit=5")
    assert response.status_code == 200
    models = response.json()
    assert len(models) == 5

    for i, model in enumerate(models):
        assert model["name"] == f"Test Model {i + 5}"


def test_delete_model(session_client: TestClient, session: Session, deployment) -> None:
    model = get_factory("Model", session).create(deployment=deployment)
    response = session_client.delete(f"/v1/models/{model.id}")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == {}
    response = session_client.get(f"/v1/models/{model.id}")
    assert response.status_code == 404
