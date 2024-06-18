from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.config.deployments import ModelDeploymentName
from backend.config.tools import ToolName
from backend.database_models.agent import Agent
from backend.tests.factories import get_factory


def test_create_agent(session_client: TestClient, session: Session) -> None:
    request_json = {
        "name": "test agent",
        "version": 1,
        "description": "test description",
        "preamble": "test preamble",
        "temperature": 0.5,
        "model": "command-r-plus",
        "deployment": ModelDeploymentName.CoherePlatform,
        "tools": [ToolName.Calculator],
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
    assert response_agent["tools"] == request_json["tools"]

    agent = session.get(Agent, response_agent["id"])
    assert agent is not None
    assert agent.name == request_json["name"]
    assert agent.version == request_json["version"]
    assert agent.description == request_json["description"]
    assert agent.preamble == request_json["preamble"]
    assert agent.temperature == request_json["temperature"]
    assert agent.model == request_json["model"]
    assert agent.deployment == request_json["deployment"]
    assert agent.tools == request_json["tools"]


def test_create_agent_missing_name(
    session_client: TestClient, session: Session
) -> None:
    request_json = {
        "description": "test description",
        "preamble": "test preamble",
        "temperature": 0.5,
        "model": "command-r-plus",
        "deployment": ModelDeploymentName.CoherePlatform,
    }
    response = session_client.post(
        "/v1/agents", json=request_json, headers={"User-Id": "123"}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Name, model, and deployment are required."}


def test_create_agent_missing_model(
    session_client: TestClient, session: Session
) -> None:
    request_json = {
        "name": "test agent",
        "description": "test description",
        "preamble": "test preamble",
        "temperature": 0.5,
        "deployment": ModelDeploymentName.CoherePlatform,
    }
    response = session_client.post(
        "/v1/agents", json=request_json, headers={"User-Id": "123"}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Name, model, and deployment are required."}


def test_create_agent_missing_deployment(
    session_client: TestClient, session: Session
) -> None:
    request_json = {
        "name": "test agent",
        "description": "test description",
        "preamble": "test preamble",
        "temperature": 0.5,
        "model": "command-r-plus",
    }
    response = session_client.post(
        "/v1/agents", json=request_json, headers={"User-Id": "123"}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Name, model, and deployment are required."}


def test_create_agent_missing_user_id_header(
    session_client: TestClient, session: Session
) -> None:
    request_json = {
        "name": "test agent",
        "model": "command-r-plus",
        "deployment": ModelDeploymentName.CoherePlatform,
    }
    response = session_client.post("/v1/agents", json=request_json)
    assert response.status_code == 401


def test_create_agent_missing_non_required_fields(
    session_client: TestClient, session: Session
) -> None:
    request_json = {
        "name": "test agent",
        "model": "command-r-plus",
        "deployment": ModelDeploymentName.CoherePlatform,
    }

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

    agent = session.get(Agent, response_agent["id"])
    assert agent is not None
    assert agent.name == request_json["name"]
    assert agent.version == 1
    assert agent.description == ""
    assert agent.preamble == ""
    assert agent.temperature == 0.3
    assert agent.model == request_json["model"]


def test_create_agent_invalid_deployment(
    session_client: TestClient, session: Session
) -> None:
    request_json = {
        "name": "test agent",
        "version": 1,
        "description": "test description",
        "preamble": "test preamble",
        "temperature": 0.5,
        "model": "command-r-plus",
        "deployment": "not a real deployment",
    }

    response = session_client.post(
        "/v1/agents", json=request_json, headers={"User-Id": "123"}
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Deployment not a real deployment not found or is not available."
    }


def test_create_agent_invalid_tool(
    session_client: TestClient, session: Session
) -> None:
    request_json = {
        "name": "test agent",
        "model": "command-r-plus",
        "deployment": ModelDeploymentName.CoherePlatform,
        "tools": [ToolName.Calculator, "not a real tool"],
    }

    response = session_client.post(
        "/v1/agents", json=request_json, headers={"User-Id": "123"}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Tool not a real tool not found."}


def test_create_existing_agent(session_client: TestClient, session: Session) -> None:
    agent = get_factory("Agent", session).create(name="test agent")
    request_json = {
        "name": agent.name,
    }

    response = session_client.post(
        "/v1/agents", json=request_json, headers={"User-Id": "123"}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Agent test agent already exists."}


def test_list_agents_empty(session_client: TestClient, session: Session) -> None:
    response = session_client.get("/v1/agents", headers={"User-Id": "123"})
    assert response.status_code == 200
    response_agents = response.json()
    assert len(response_agents) == 0


def test_list_agents(session_client: TestClient, session: Session) -> None:
    for _ in range(3):
        _ = get_factory("Agent", session).create()

    response = session_client.get("/v1/agents", headers={"User-Id": "123"})
    assert response.status_code == 200
    response_agents = response.json()
    assert len(response_agents) == 3


def test_list_agents_with_pagination(
    session_client: TestClient, session: Session
) -> None:
    for _ in range(5):
        _ = get_factory("Agent", session).create()

    response = session_client.get(
        "/v1/agents?limit=3&offset=2", headers={"User-Id": "123"}
    )
    assert response.status_code == 200
    response_agents = response.json()
    assert len(response_agents) == 3

    response = session_client.get(
        "/v1/agents?limit=2&offset=4", headers={"User-Id": "123"}
    )
    assert response.status_code == 200
    response_agents = response.json()
    assert len(response_agents) == 1


def test_get_agent(session_client: TestClient, session: Session) -> None:
    agent = get_factory("Agent", session).create(name="test agent")

    response = session_client.get(f"/v1/agents/{agent.id}", headers={"User-Id": "123"})
    assert response.status_code == 200
    response_agent = response.json()
    assert response_agent["name"] == agent.name


def test_get_nonexistent_agent(session_client: TestClient, session: Session) -> None:
    response = session_client.get("/v1/agents/456", headers={"User-Id": "123"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Agent with ID: 456 not found."}


def test_update_agent(session_client: TestClient, session: Session) -> None:
    agent = get_factory("Agent", session).create(
        name="test agent",
        version=1,
        description="test description",
        preamble="test preamble",
        temperature=0.5,
        model="command-r-plus",
        deployment=ModelDeploymentName.CoherePlatform,
    )

    request_json = {
        "name": "updated name",
        "version": 2,
        "description": "updated description",
        "preamble": "updated preamble",
        "temperature": 0.7,
        "model": "command-r",
        "deployment": ModelDeploymentName.CoherePlatform,
    }

    response = session_client.put(
        f"/v1/agents/{agent.id}", json=request_json, headers={"User-Id": "123"}
    )

    assert response.status_code == 200
    updated_agent = response.json()
    assert updated_agent["name"] == "updated name"
    assert updated_agent["version"] == 2
    assert updated_agent["description"] == "updated description"
    assert updated_agent["preamble"] == "updated preamble"
    assert updated_agent["temperature"] == 0.7
    assert updated_agent["model"] == "command-r"
    assert updated_agent["deployment"] == ModelDeploymentName.CoherePlatform


def test_partial_update_agent(session_client: TestClient, session: Session) -> None:
    agent = get_factory("Agent", session).create(
        name="test agent",
        version=1,
        description="test description",
        preamble="test preamble",
        temperature=0.5,
        model="command-r-plus",
        deployment=ModelDeploymentName.CoherePlatform,
        tools=[ToolName.Calculator],
    )

    request_json = {
        "name": "updated name",
        "tools": [ToolName.Search_File, ToolName.Read_File],
    }

    response = session_client.put(
        f"/v1/agents/{agent.id}", json=request_json, headers={"User-Id": "123"}
    )
    assert response.status_code == 200
    updated_agent = response.json()
    assert updated_agent["name"] == "updated name"
    assert updated_agent["version"] == 1
    assert updated_agent["description"] == "test description"
    assert updated_agent["preamble"] == "test preamble"
    assert updated_agent["temperature"] == 0.5
    assert updated_agent["model"] == "command-r-plus"
    assert updated_agent["deployment"] == ModelDeploymentName.CoherePlatform
    assert updated_agent["tools"] == [ToolName.Search_File, ToolName.Read_File]


def test_update_nonexistent_agent(session_client: TestClient, session: Session) -> None:
    request_json = {
        "name": "updated name",
    }
    response = session_client.put(
        "/v1/agents/456", json=request_json, headers={"User-Id": "123"}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Agent with ID: 456 not found."}


def test_update_agent_invalid_model(
    session_client: TestClient, session: Session
) -> None:
    agent = get_factory("Agent", session).create(
        name="test agent",
        version=1,
        description="test description",
        preamble="test preamble",
        temperature=0.5,
        model="command-r-plus",
        deployment=ModelDeploymentName.CoherePlatform,
    )

    request_json = {
        "model": "not a real model",
        "deployment": ModelDeploymentName.CoherePlatform,
    }

    response = session_client.put(
        f"/v1/agents/{agent.id}", json=request_json, headers={"User-Id": "123"}
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Model not a real model not found for deployment Cohere Platform."
    }


def test_update_agent_invalid_deployment(
    session_client: TestClient, session: Session
) -> None:
    agent = get_factory("Agent", session).create(
        name="test agent",
        version=1,
        description="test description",
        preamble="test preamble",
        temperature=0.5,
        model="command-r-plus",
        deployment=ModelDeploymentName.CoherePlatform,
    )

    request_json = {
        "model": "command-r",
        "deployment": "not a real deployment",
    }

    response = session_client.put(
        f"/v1/agents/{agent.id}", json=request_json, headers={"User-Id": "123"}
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Deployment not a real deployment not found or is not available."
    }


def test_update_agent_model_without_deployment(
    session_client: TestClient, session: Session
) -> None:
    agent = get_factory("Agent", session).create(
        name="test agent",
        version=1,
        description="test description",
        preamble="test preamble",
        temperature=0.5,
        model="command-r-plus",
        deployment=ModelDeploymentName.CoherePlatform,
    )

    request_json = {
        "model": "command-r",
    }

    response = session_client.put(
        f"/v1/agents/{agent.id}", json=request_json, headers={"User-Id": "123"}
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": "If updating an agent's model, the deployment must also be provided."
    }


def test_update_agent_deployment_without_model(
    session_client: TestClient, session: Session
) -> None:
    agent = get_factory("Agent", session).create(
        name="test agent",
        version=1,
        description="test description",
        preamble="test preamble",
        temperature=0.5,
        model="command-r-plus",
        deployment=ModelDeploymentName.CoherePlatform,
    )

    request_json = {
        "deployment": ModelDeploymentName.CoherePlatform,
    }

    response = session_client.put(
        f"/v1/agents/{agent.id}", json=request_json, headers={"User-Id": "123"}
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": "If updating an agent's deployment type, the model must also be provided."
    }


def test_update_agent_invalid_tool(
    session_client: TestClient, session: Session
) -> None:
    agent = get_factory("Agent", session).create(
        name="test agent",
        version=1,
        description="test description",
        preamble="test preamble",
        temperature=0.5,
        model="command-r-plus",
        deployment=ModelDeploymentName.CoherePlatform,
    )

    request_json = {
        "model": "not a real model",
        "deployment": "not a real deployment",
        "tools": [ToolName.Calculator, "not a real tool"],
    }

    response = session_client.put(
        f"/v1/agents/{agent.id}", json=request_json, headers={"User-Id": "123"}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Tool not a real tool not found."}


def test_delete_agent(session_client: TestClient, session: Session) -> None:
    agent = get_factory("Agent", session).create()
    response = session_client.delete(
        f"/v1/agents/{agent.id}", headers={"User-Id": "123"}
    )
    assert response.status_code == 200
    assert response.json() == {}

    agent = session.get(Agent, agent.id)
    assert agent is None


def test_fail_delete_nonexistent_agent(
    session_client: TestClient, session: Session
) -> None:
    response = session_client.delete("/v1/agents/456", headers={"User-Id": "123"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Agent with ID: 456 not found."}
