from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.database_models.agent import Agent, Deployment, Model
from backend.tests.factories import get_factory


def test_create_agent(session_client: TestClient, session: Session) -> None:
    request_json = {
        "name": "test agent",
        "version": 1,
        "description": "test description",
        "preamble": "test preamble",
        "temperature": 0.5,
        "model": Model.COMMAND_R,
        "deployment": Deployment.COHERE_PLATFORM,
    }

    response = session_client.post(
        "/v1/agents", json=request_json, headers={"User-Id": "123"}
    )
    assert response.status_code == 200
    response_agent = response.json()

    assert response_agent["name"] == request_json["name"]
    assert response_agent["version"] == request_json["version"]
    assert response_agent["description"] == request_json["description"]
    assert response_agent["preamble"] == request_json["preamble"]
    assert response_agent["temperature"] == request_json["temperature"]
    assert response_agent["model"] == request_json["model"]
    assert response_agent["deployment"] == request_json["deployment"]

    agent = session.get(Agent, response_agent["id"])
    assert agent is not None
    assert agent.name == request_json["name"]
    assert agent.version == request_json["version"]
    assert agent.description == request_json["description"]
    assert agent.preamble == request_json["preamble"]
    assert agent.temperature == request_json["temperature"]
    assert agent.model == request_json["model"]
    assert agent.deployment == request_json["deployment"]


def test_create_agent_missing_name(
    session_client: TestClient, session: Session
) -> None:
    request_json = {
        "description": "test description",
        "preamble": "test preamble",
        "temperature": 0.5,
        "model": Model.COMMAND_R,
        "deployment": Deployment.COHERE_PLATFORM,
    }
    response = session_client.post(
        "/v1/agents", json=request_json, headers={"User-Id": "123"}
    )
    assert response.status_code == 400


def test_create_agent_missing_model(
    session_client: TestClient, session: Session
) -> None:
    request_json = {
        "name": "test agent",
        "description": "test description",
        "preamble": "test preamble",
        "temperature": 0.5,
        "deployment": Deployment.COHERE_PLATFORM,
    }
    response = session_client.post(
        "/v1/agents", json=request_json, headers={"User-Id": "123"}
    )
    assert response.status_code == 400


def test_create_agent_missing_deployment(
    session_client: TestClient, session: Session
) -> None:
    request_json = {
        "name": "test agent",
        "description": "test description",
        "preamble": "test preamble",
        "temperature": 0.5,
        "model": Model.COMMAND_R,
    }
    response = session_client.post(
        "/v1/agents", json=request_json, headers={"User-Id": "123"}
    )
    assert response.status_code == 400


def test_create_agent_missing_non_required_fields(
    session_client: TestClient, session: Session
) -> None:
    request_json = {
        "name": "test agent",
        "model": Model.COMMAND_R,
        "deployment": Deployment.COHERE_PLATFORM,
    }

    print(request_json)

    response = session_client.post(
        "/v1/agents", json=request_json, headers={"User-Id": "123"}
    )
    assert response.status_code == 200
    response_agent = response.json()

    assert response_agent["name"] == request_json["name"]
    assert response_agent["version"] == 1
    assert response_agent["description"] == ""
    assert response_agent["preamble"] == ""
    assert response_agent["temperature"] == 0.3
    assert response_agent["model"] == request_json["model"]
    assert response_agent["deployment"] == request_json["deployment"]

    agent = session.get(Agent, response_agent["id"])
    assert agent is not None
    assert agent.name == request_json["name"]
    assert agent.version == 1
    assert agent.description == ""
    assert agent.preamble == ""
    assert agent.temperature == 0.3
    assert agent.model == request_json["model"]
    assert agent.deployment == request_json["deployment"]


def test_list_agents(session_client: TestClient, session: Session) -> None:
    for _ in range(3):
        _ = get_factory("Agent", session).create()

    response = session_client.get("/v1/agents", headers={"User-Id": "123"})
    assert response.status_code == 200
    response_agents = response.json()
    assert len(response_agents) == 3
