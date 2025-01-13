from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.config.deployments import ModelDeploymentName
from backend.config.tools import Tool
from backend.database_models.agent import Agent
from backend.database_models.agent_tool_metadata import AgentToolMetadata
from backend.schemas.user import User
from backend.tests.unit.factories import get_factory


def test_create_agent(session_client: TestClient, session: Session, user: User) -> None:
    request_json = {
        "name": "test agent",
        "version": 1,
        "description": "test description",
        "preamble": "test preamble",
        "temperature": 0.5,
        "model": "command-r-plus",
        "deployment": ModelDeploymentName.CoherePlatform,
        "tools": [Tool.Calculator.value.ID, Tool.Search_File.value.ID, Tool.Read_File.value.ID],
    }

    response = session_client.post(
        "/v1/agents", json=request_json, headers={"User-Id": user.id}
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


def test_create_agent_with_tool_metadata(
    session_client: TestClient, session: Session, user: User,
) -> None:
    request_json = {
        "name": "test agent",
        "version": 1,
        "description": "test description",
        "preamble": "test preamble",
        "temperature": 0.5,
        "model": "command-r-plus",
        "deployment": ModelDeploymentName.CoherePlatform,
        "tools": [Tool.Google_Drive.value.ID, Tool.Search_File.value.ID],
        "tools_metadata": [
            {
                "tool_name": Tool.Google_Drive.value.ID,
                "artifacts": [
                    {
                        "name": "/folder",
                        "ids": "folder1",
                        "type": "folder_ids",
                    }
                ],
            },
            {
                "tool_name": Tool.Search_File.value.ID,
                "artifacts": [
                    {
                        "name": "file.txt",
                        "ids": "file1",
                        "type": "file_ids",
                    }
                ],
            },
        ],
    }

    response = session_client.post(
        "/v1/agents", json=request_json, headers={"User-Id": user.id}
    )
    assert response.status_code == 200
    response_agent = response.json()

    tool_metadata = (
        session.query(AgentToolMetadata)
        .filter(AgentToolMetadata.agent_id == response_agent["id"])
        .all()
    )
    assert len(tool_metadata) == 2
    assert tool_metadata[0].tool_name == Tool.Google_Drive.value.ID
    assert tool_metadata[0].artifacts == [
        {"name": "/folder", "ids": "folder1", "type": "folder_ids"},
    ]
    assert tool_metadata[1].tool_name == Tool.Search_File.value.ID
    assert tool_metadata[1].artifacts == [
        {"name": "file.txt", "ids": "file1", "type": "file_ids"}
    ]


def test_create_agent_missing_non_required_fields(
    session_client: TestClient, session: Session, user: User,
) -> None:
    request_json = {
        "name": "test agent",
        "model": "command-r-plus",
        "deployment": ModelDeploymentName.CoherePlatform,
    }

    response = session_client.post(
        "/v1/agents", json=request_json, headers={"User-Id": user.id}
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


def test_update_agent(session_client: TestClient, session: Session, user: User) -> None:
    agent = get_factory("Agent", session).create(
        name="test agent",
        version=1,
        description="test description",
        preamble="test preamble",
        temperature=0.5,
        user=user,
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
        f"/v1/agents/{agent.id}",
        json=request_json,
        headers={"User-Id": user.id},
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
