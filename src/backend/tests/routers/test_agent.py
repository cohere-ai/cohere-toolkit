from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.config.deployments import ModelDeploymentName
from backend.config.tools import ToolName
from backend.crud import agent as agent_crud
from backend.database_models.agent import Agent
from backend.database_models.agent_tool_metadata import AgentToolMetadata
from backend.schemas.metrics import MetricsData, MetricsMessageType
from backend.services.metrics import report_metrics
from backend.tests.factories import get_factory


async def test_create_agent_mertic(
    session_client: TestClient, session: Session
) -> None:
    user = get_factory("User", session).create(fullname="John Doe")
    request_json = {
        "name": "test agent",
        "version": 1,
        "description": "test description",
        "preamble": "test preamble",
        "temperature": 0.5,
        "model": "command-r-plus",
        "deployment": ModelDeploymentName.CoherePlatform,
        "tools": [ToolName.Calculator, ToolName.Search_File, ToolName.Read_File],
    }

    with patch(
        "backend.services.metrics.report_metrics",
        return_value=None,
    ) as mock_metrics:
        response = session_client.post(
            "/v1/agents", json=request_json, headers={"User-Id": user.id}
        )
        assert response.status_code == 200
        m_args: MetricsData = mock_metrics.await_args.args[0].signal
        assert m_args.user_id == user.id
        assert m_args.message_type == MetricsMessageType.ASSISTANT_CREATED
        assert m_args.assistant.name == request_json["name"]
        assert m_args.user.fullname == user.fullname


def test_create_agent(session_client: TestClient, session: Session, user) -> None:
    request_json = {
        "name": "test agent",
        "version": 1,
        "description": "test description",
        "preamble": "test preamble",
        "temperature": 0.5,
        "model": "command-r-plus",
        "deployment": ModelDeploymentName.CoherePlatform,
        "tools": [ToolName.Calculator, ToolName.Search_File, ToolName.Read_File],
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
    session_client: TestClient, session: Session, user
) -> None:
    request_json = {
        "name": "test agent",
        "version": 1,
        "description": "test description",
        "preamble": "test preamble",
        "temperature": 0.5,
        "model": "command-r-plus",
        "deployment": ModelDeploymentName.CoherePlatform,
        "tools": [ToolName.Google_Drive, ToolName.Search_File],
        "tools_metadata": [
            {
                "tool_name": ToolName.Google_Drive,
                "artifacts": [
                    {
                        "name": "/folder",
                        "ids": "folder1",
                        "type": "folder_ids",
                    }
                ],
            },
            {
                "tool_name": ToolName.Search_File,
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
    assert tool_metadata[0].tool_name == ToolName.Google_Drive
    assert tool_metadata[0].artifacts == [
        {"name": "/folder", "ids": "folder1", "type": "folder_ids"},
    ]
    assert tool_metadata[1].tool_name == ToolName.Search_File
    assert tool_metadata[1].artifacts == [
        {"name": "file.txt", "ids": "file1", "type": "file_ids"}
    ]


def test_create_agent_missing_name(
    session_client: TestClient, session: Session, user
) -> None:
    request_json = {
        "description": "test description",
        "preamble": "test preamble",
        "temperature": 0.5,
        "model": "command-r-plus",
        "deployment": ModelDeploymentName.CoherePlatform,
    }
    response = session_client.post(
        "/v1/agents", json=request_json, headers={"User-Id": user.id}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Name, model, and deployment are required."}


def test_create_agent_missing_model(
    session_client: TestClient, session: Session, user
) -> None:
    request_json = {
        "name": "test agent",
        "description": "test description",
        "preamble": "test preamble",
        "temperature": 0.5,
        "deployment": ModelDeploymentName.CoherePlatform,
    }
    response = session_client.post(
        "/v1/agents", json=request_json, headers={"User-Id": user.id}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Name, model, and deployment are required."}


def test_create_agent_missing_deployment(
    session_client: TestClient, session: Session, user
) -> None:
    request_json = {
        "name": "test agent",
        "description": "test description",
        "preamble": "test preamble",
        "temperature": 0.5,
        "model": "command-r-plus",
    }
    response = session_client.post(
        "/v1/agents", json=request_json, headers={"User-Id": user.id}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Name, model, and deployment are required."}


def test_create_agent_missing_user_id_header(
    session_client: TestClient, session: Session, user
) -> None:
    request_json = {
        "name": "test agent",
        "model": "command-r-plus",
        "deployment": ModelDeploymentName.CoherePlatform,
    }
    response = session_client.post("/v1/agents", json=request_json)
    assert response.status_code == 401


def test_create_agent_missing_non_required_fields(
    session_client: TestClient, session: Session, user
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


def test_create_agent_invalid_deployment(
    session_client: TestClient, session: Session, user
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
        "/v1/agents", json=request_json, headers={"User-Id": user.id}
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Deployment not a real deployment not found or is not available in the Database."
    }


def test_create_agent_invalid_tool(
    session_client: TestClient, session: Session, user
) -> None:
    request_json = {
        "name": "test agent",
        "model": "command-r-plus",
        "deployment": ModelDeploymentName.CoherePlatform,
        "tools": [ToolName.Calculator, "not a real tool"],
    }

    response = session_client.post(
        "/v1/agents", json=request_json, headers={"User-Id": user.id}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Tool not a real tool not found."}


def test_create_existing_agent(
    session_client: TestClient, session: Session, user
) -> None:
    agent = get_factory("Agent", session).create(name="test agent")
    request_json = {
        "name": agent.name,
    }

    response = session_client.post(
        "/v1/agents", json=request_json, headers={"User-Id": user.id}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Agent test agent already exists."}


def test_list_agents_empty(session_client: TestClient, session: Session) -> None:
    # Delete default agent
    session.query(Agent).delete()
    response = session_client.get("/v1/agents", headers={"User-Id": "123"})
    assert response.status_code == 200
    response_agents = response.json()
    assert len(response_agents) == 0


def test_list_agents(session_client: TestClient, session: Session, user) -> None:
    session.query(Agent).delete()
    for _ in range(3):
        _ = get_factory("Agent", session).create(user=user)

    response = session_client.get("/v1/agents", headers={"User-Id": user.id})
    assert response.status_code == 200
    response_agents = response.json()
    assert len(response_agents) == 3


def test_list_private_agents(
    session_client: TestClient, session: Session, user
) -> None:
    for _ in range(3):
        _ = get_factory("Agent", session).create(user=user, is_private=True)

    user2 = get_factory("User", session).create(id="456")
    for _ in range(2):
        _ = get_factory("Agent", session).create(user=user2, is_private=True)

    response = session_client.get(
        "/v1/agents?visibility=private", headers={"User-Id": user.id}
    )

    assert response.status_code == 200
    response_agents = response.json()

    # Only the agents created by user should be returned
    assert len(response_agents) == 3


def test_list_public_agents(session_client: TestClient, session: Session, user) -> None:
    for _ in range(3):
        _ = get_factory("Agent", session).create(user=user, is_private=True)

    user2 = get_factory("User", session).create(id="456")
    for _ in range(2):
        _ = get_factory("Agent", session).create(user=user2, is_private=False)

    response = session_client.get(
        "/v1/agents?visibility=public", headers={"User-Id": user.id}
    )

    assert response.status_code == 200
    response_agents = response.json()

    # Only the agents created by user should be returned
    assert len(response_agents) == 2


def list_public_and_private_agents(
    session_client: TestClient, session: Session, user
) -> None:
    for _ in range(3):
        _ = get_factory("Agent", session).create(user=user, is_private=True)

    user2 = get_factory("User", session).create(id="456")
    for _ in range(2):
        _ = get_factory("Agent", session).create(user=user2, is_private=False)

    response = session_client.get(
        "/v1/agents?visibility=all", headers={"User-Id": user.id}
    )

    assert response.status_code == 200
    response_agents = response.json()

    # Only the agents created by user should be returned
    assert len(response_agents) == 5


def test_list_agent_deployments(
    session_client: TestClient, session: Session, user
) -> None:
    agent = get_factory("Agent", session).create(user=user)
    for i in range(3):
        deployment = get_factory("Deployment", session).create(
            name=f"test deployment {i}"
        )
        model = get_factory("Model", session).create(
            deployment=deployment, name=f"test r+ ({i})", cohere_name="command-r-plus"
        )
        agent_crud.assign_model_deployment_to_agent(
            session,
            agent,
            model.id,
            deployment.id,
            deployment_config=deployment.default_deployment_config,
        )
        model1 = get_factory("Model", session).create(
            deployment=deployment, name=f"test r ({i})", cohere_name="command-r"
        )
        agent_crud.assign_model_deployment_to_agent(
            session,
            agent,
            model1.id,
            deployment.id,
            deployment_config=deployment.default_deployment_config,
        )

    response = session_client.get(
        f"/v1/agents/{agent.id}/deployments", headers={"User-Id": user.id}
    )
    assert response.status_code == 200
    response_deployments = response.json()
    assert len(response_deployments) == 3


def test_list_agents_with_pagination(
    session_client: TestClient, session: Session, user
) -> None:
    for _ in range(5):
        _ = get_factory("Agent", session).create(user=user)

    response = session_client.get(
        "/v1/agents?limit=3&offset=2", headers={"User-Id": user.id}
    )
    assert response.status_code == 200
    response_agents = response.json()
    assert len(response_agents) == 3

    response = session_client.get(
        "/v1/agents?limit=2&offset=4", headers={"User-Id": user.id}
    )
    assert response.status_code == 200
    response_agents = response.json()
    assert len(response_agents) == 1


@pytest.mark.asyncio
async def test_get_agent_mertic(
    session_client: TestClient, session: Session, user
) -> None:
    agent = get_factory("Agent", session).create(name="test agent", user_id=user.id)
    agent_tool_metadata = get_factory("AgentToolMetadata", session).create(
        user_id=user.id,
        agent_id=agent.id,
        tool_name=ToolName.Google_Drive,
        artifacts=[
            {
                "name": "/folder1",
                "ids": "folder1",
                "type": "folder_id",
            },
            {
                "name": "file1.txt",
                "ids": "file1",
                "type": "file_id",
            },
        ],
    )

    with patch(
        "backend.services.metrics.report_metrics",
        return_value=None,
    ) as mock_metrics:
        response = session_client.get(
            f"/v1/agents/{agent.id}", headers={"User-Id": user.id}
        )
        assert response.status_code == 200
        m_args: MetricsData = mock_metrics.await_args.args[0].signal
        assert m_args.message_type == MetricsMessageType.ASSISTANT_ACCESSED
        assert m_args.assistant.name == agent.name


@pytest.mark.asyncio
async def test_get_default_agent_mertic(
    session_client: TestClient, session: Session, user
) -> None:

    with patch(
        "backend.services.metrics.report_metrics",
        return_value=None,
    ) as mock_metrics:
        response = session_client.get(
            f"/v1/default_agent", headers={"User-Id": user.id}
        )
        assert response.status_code == 200
        m_args: MetricsData = mock_metrics.await_args.args[0].signal
        assert m_args.message_type == MetricsMessageType.ASSISTANT_ACCESSED
        assert m_args.assistant.name == "Default Agent"


def test_get_agent(session_client: TestClient, session: Session, user) -> None:
    agent = get_factory("Agent", session).create(name="test agent", user_id=user.id)
    agent_tool_metadata = get_factory("AgentToolMetadata", session).create(
        user_id=user.id,
        agent_id=agent.id,
        tool_name=ToolName.Google_Drive,
        artifacts=[
            {
                "name": "/folder1",
                "ids": "folder1",
                "type": "folder_id",
            },
            {
                "name": "file1.txt",
                "ids": "file1",
                "type": "file_id",
            },
        ],
    )

    response = session_client.get(
        f"/v1/agents/{agent.id}", headers={"User-Id": user.id}
    )
    assert response.status_code == 200
    response_agent = response.json()
    assert response_agent["name"] == agent.name
    assert response_agent["tools_metadata"][0]["tool_name"] == ToolName.Google_Drive
    assert (
        response_agent["tools_metadata"][0]["artifacts"]
        == agent_tool_metadata.artifacts
    )


def test_get_nonexistent_agent(
    session_client: TestClient, session: Session, user
) -> None:
    response = session_client.get("/v1/agents/456", headers={"User-Id": user.id})
    assert response.status_code == 404
    assert response.json() == {"detail": "Agent with ID 456 not found."}


def test_get_public_agent(session_client: TestClient, session: Session, user) -> None:
    user2 = get_factory("User", session).create(id="456")
    agent = get_factory("Agent", session).create(
        name="test agent", user_id=user2.id, is_private=False
    )

    response = session_client.get(
        f"/v1/agents/{agent.id}", headers={"User-Id": user.id}
    )

    assert response.status_code == 200
    response_agent = response.json()
    assert response_agent["name"] == agent.name


def test_get_private_agent(session_client: TestClient, session: Session, user) -> None:
    agent = get_factory("Agent", session).create(
        name="test agent", user=user, is_private=True
    )

    response = session_client.get(
        f"/v1/agents/{agent.id}", headers={"User-Id": user.id}
    )

    assert response.status_code == 200
    response_agent = response.json()
    assert response_agent["name"] == agent.name


def test_get_private_agent_by_another_user(
    session_client: TestClient, session: Session, user
) -> None:
    user2 = get_factory("User", session).create(id="456")
    agent = get_factory("Agent", session).create(
        name="test agent", user_id=user2.id, is_private=True
    )

    response = session_client.get(
        f"/v1/agents/{agent.id}", headers={"User-Id": user.id}
    )

    assert response.status_code == 404
    assert response.json() == {"detail": f"Agent with ID {agent.id} not found."}


def test_update_agent(session_client: TestClient, session: Session, user) -> None:
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


def test_partial_update_agent(session_client: TestClient, session: Session) -> None:
    user = get_factory("User", session).create(id="123")
    agent = get_factory("Agent", session).create(
        name="test agent",
        version=1,
        description="test description",
        preamble="test preamble",
        temperature=0.5,
        tools=[ToolName.Calculator],
        user=user,
    )

    request_json = {
        "name": "updated name",
        "tools": [ToolName.Search_File, ToolName.Read_File],
    }

    response = session_client.put(
        f"/v1/agents/{agent.id}",
        json=request_json,
        headers={"User-Id": user.id},
    )
    assert response.status_code == 200
    updated_agent = response.json()
    assert updated_agent["name"] == "updated name"
    assert updated_agent["version"] == 1
    assert updated_agent["description"] == "test description"
    assert updated_agent["preamble"] == "test preamble"
    assert updated_agent["temperature"] == 0.5
    assert updated_agent["tools"] == [ToolName.Search_File, ToolName.Read_File]


def test_update_agent_with_tool_metadata(
    session_client: TestClient, session: Session
) -> None:
    user = get_factory("User", session).create(id="123")
    agent = get_factory("Agent", session).create(
        name="test agent",
        version=1,
        description="test description",
        preamble="test preamble",
        temperature=0.5,
        user=user,
    )
    agent_tool_metadata = get_factory("AgentToolMetadata", session).create(
        user_id=user.id,
        agent_id=agent.id,
        tool_name=ToolName.Google_Drive,
        artifacts=[
            {
                "url": "test",
                "name": "test",
                "type": "folder",
            },
        ],
    )

    request_json = {
        "tools_metadata": [
            {
                "user_id": user.id,
                "organization_id": None,
                "id": agent_tool_metadata.id,
                "tool_name": "google_drive",
                "artifacts": [
                    {
                        "url": "test",
                        "name": "test",
                        "type": "folder",
                    }
                ],
            }
        ],
    }

    response = session_client.put(
        f"/v1/agents/{agent.id}",
        json=request_json,
        headers={"User-Id": user.id},
    )

    assert response.status_code == 200
    updated_agent = response.json()

    tool_metadata = (
        session.query(AgentToolMetadata)
        .filter(AgentToolMetadata.agent_id == agent.id)
        .all()
    )
    assert len(tool_metadata) == 1
    assert tool_metadata[0].tool_name == "google_drive"
    assert tool_metadata[0].artifacts == [
        {"url": "test", "name": "test", "type": "folder"}
    ]


def test_update_agent_with_tool_metadata_and_new_tool_metadata(
    session_client: TestClient, session: Session
) -> None:
    user = get_factory("User", session).create(id="123")
    agent = get_factory("Agent", session).create(
        name="test agent",
        version=1,
        description="test description",
        preamble="test preamble",
        temperature=0.5,
        user=user,
    )
    agent_tool_metadata = get_factory("AgentToolMetadata", session).create(
        user_id=user.id,
        agent_id=agent.id,
        tool_name=ToolName.Google_Drive,
        artifacts=[
            {
                "url": "test",
                "name": "test",
                "type": "folder",
            },
        ],
    )

    request_json = {
        "tools_metadata": [
            {
                "user_id": user.id,
                "organization_id": None,
                "id": agent_tool_metadata.id,
                "tool_name": "google_drive",
                "artifacts": [
                    {
                        "url": "test",
                        "name": "test",
                        "type": "folder",
                    }
                ],
            },
            {
                "tool_name": "search_file",
                "artifacts": [
                    {
                        "url": "test",
                        "name": "test",
                        "type": "file",
                    }
                ],
            },
        ],
    }

    response = session_client.put(
        f"/v1/agents/{agent.id}",
        json=request_json,
        headers={"User-Id": user.id},
    )

    assert response.status_code == 200

    tool_metadata = (
        session.query(AgentToolMetadata)
        .filter(AgentToolMetadata.agent_id == agent.id)
        .all()
    )
    assert len(tool_metadata) == 2
    drive_tool = None
    search_tool = None
    for tool in tool_metadata:
        if tool.tool_name == "google_drive":
            drive_tool = tool
        if tool.tool_name == "search_file":
            search_tool = tool
    assert drive_tool.tool_name == "google_drive"
    assert drive_tool.artifacts == [{"url": "test", "name": "test", "type": "folder"}]
    assert search_tool.tool_name == "search_file"
    assert search_tool.artifacts == [{"url": "test", "name": "test", "type": "file"}]


def test_update_agent_remove_existing_tool_metadata(
    session_client: TestClient, session: Session
) -> None:
    user = get_factory("User", session).create(id="123")
    agent = get_factory("Agent", session).create(
        name="test agent",
        version=1,
        description="test description",
        preamble="test preamble",
        temperature=0.5,
        user=user,
    )
    agent_tool_metadata = get_factory("AgentToolMetadata", session).create(
        user_id=user.id,
        agent_id=agent.id,
        tool_name=ToolName.Google_Drive,
        artifacts=[
            {
                "url": "test",
                "name": "test",
                "type": "folder",
            },
        ],
    )

    request_json = {
        "tools_metadata": [],
    }

    response = session_client.put(
        f"/v1/agents/{agent.id}",
        json=request_json,
        headers={"User-Id": user.id},
    )

    assert response.status_code == 200
    updated_agent = response.json()

    tool_metadata = (
        session.query(AgentToolMetadata)
        .filter(AgentToolMetadata.agent_id == agent.id)
        .all()
    )
    assert len(tool_metadata) == 0


def test_update_nonexistent_agent(
    session_client: TestClient, session: Session, user
) -> None:
    request_json = {
        "name": "updated name",
    }
    response = session_client.put(
        "/v1/agents/456", json=request_json, headers={"User-Id": user.id}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Agent with ID 456 not found."}


def test_update_agent_wrong_user(
    session_client: TestClient, session: Session, user
) -> None:
    agent = get_factory("Agent", session).create(user=user)
    request_json = {
        "name": "updated name",
    }

    response = session_client.put(
        f"/v1/agents/{agent.id}", json=request_json, headers={"User-Id": "user-id"}
    )
    assert response.status_code == 401
    assert response.json() == {
        "detail": f"Agent with ID {agent.id} does not belong to user."
    }


def test_update_agent_invalid_model(
    session_client: TestClient, session: Session, user
) -> None:
    agent = get_factory("Agent", session).create(
        name="test agent",
        version=1,
        description="test description",
        preamble="test preamble",
        temperature=0.5,
        user=user,
    )

    request_json = {
        "model": "not a real model",
        "deployment": ModelDeploymentName.CoherePlatform,
    }

    response = session_client.put(
        f"/v1/agents/{agent.id}", json=request_json, headers={"User-Id": user.id}
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Model not a real model not found for deployment Cohere Platform."
    }


def test_update_agent_invalid_deployment(
    session_client: TestClient, session: Session, user
) -> None:
    agent = get_factory("Agent", session).create(
        name="test agent",
        version=1,
        description="test description",
        preamble="test preamble",
        temperature=0.5,
        user=user,
    )

    request_json = {
        "model": "command-r",
        "deployment": "not a real deployment",
    }

    response = session_client.put(
        f"/v1/agents/{agent.id}", json=request_json, headers={"User-Id": user.id}
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Deployment not a real deployment not found or is not available in the Database."
    }


def test_update_agent_invalid_tool(
    session_client: TestClient, session: Session, user
) -> None:
    agent = get_factory("Agent", session).create(
        name="test agent",
        version=1,
        description="test description",
        preamble="test preamble",
        temperature=0.5,
        user=user,
    )

    request_json = {
        "model": "not a real model",
        "deployment": "not a real deployment",
        "tools": [ToolName.Calculator, "not a real tool"],
    }

    response = session_client.put(
        f"/v1/agents/{agent.id}", json=request_json, headers={"User-Id": user.id}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Tool not a real tool not found."}


def test_update_private_agent(
    session_client: TestClient, session: Session, user
) -> None:
    agent = get_factory("Agent", session).create(
        name="test agent",
        version=1,
        description="test description",
        preamble="test preamble",
        temperature=0.5,
        is_private=True,
        user=user,
    )

    request_json = {
        "name": "updated name",
    }

    response = session_client.put(
        f"/v1/agents/{agent.id}", json=request_json, headers={"User-Id": user.id}
    )
    assert response.status_code == 200
    updated_agent = response.json()
    assert updated_agent["name"] == "updated name"
    assert updated_agent["is_private"] == True


def test_update_public_agent(
    session_client: TestClient, session: Session, user
) -> None:
    agent = get_factory("Agent", session).create(
        name="test agent",
        version=1,
        description="test description",
        preamble="test preamble",
        temperature=0.5,
        is_private=False,
        user=user,
    )

    request_json = {
        "name": "updated name",
    }

    response = session_client.put(
        f"/v1/agents/{agent.id}", json=request_json, headers={"User-Id": user.id}
    )
    assert response.status_code == 200
    updated_agent = response.json()
    assert updated_agent["name"] == "updated name"
    assert updated_agent["is_private"] == False


def test_delete_agent_metric(
    session_client: TestClient, session: Session, user
) -> None:
    agent = get_factory("Agent", session).create(user=user)
    with patch(
        "backend.services.metrics.report_metrics",
        return_value=None,
    ) as mock_metrics:
        response = session_client.delete(
            f"/v1/agents/{agent.id}", headers={"User-Id": user.id}
        )
        assert response.status_code == 200
        m_args: MetricsData = mock_metrics.await_args.args[0].signal
        assert m_args.message_type == MetricsMessageType.ASSISTANT_DELETED
        assert m_args.assistant_id == agent.id


def test_delete_agent(session_client: TestClient, session: Session, user) -> None:
    agent = get_factory("Agent", session).create(user=user)
    response = session_client.delete(
        f"/v1/agents/{agent.id}", headers={"User-Id": user.id}
    )
    assert response.status_code == 200
    assert response.json() == {}

    agent = session.get(Agent, agent.id)
    assert agent is None


def test_fail_delete_nonexistent_agent(
    session_client: TestClient, session: Session, user
) -> None:
    response = session_client.delete("/v1/agents/456", headers={"User-Id": user.id})
    assert response.status_code == 404
    assert response.json() == {"detail": "Agent with ID 456 not found."}


# Test create agent tool metadata
def test_create_agent_tool_metadata(
    session_client: TestClient, session: Session, user
) -> None:
    agent = get_factory("Agent", session).create(user=user)
    request_json = {
        "tool_name": ToolName.Google_Drive,
        "artifacts": [
            {
                "name": "/folder1",
                "ids": "folder1",
                "type": "folder_id",
            },
            {
                "name": "file1.txt",
                "ids": "file1",
                "type": "file_id",
            },
        ],
    }

    response = session_client.post(
        f"/v1/agents/{agent.id}/tool-metadata",
        json=request_json,
        headers={"User-Id": user.id},
    )
    assert response.status_code == 200
    response_agent_tool_metadata = response.json()

    assert response_agent_tool_metadata["tool_name"] == request_json["tool_name"]
    assert response_agent_tool_metadata["artifacts"] == request_json["artifacts"]

    agent_tool_metadata = session.get(
        AgentToolMetadata, response_agent_tool_metadata["id"]
    )
    assert agent_tool_metadata.tool_name == ToolName.Google_Drive
    assert agent_tool_metadata.artifacts == [
        {
            "name": "/folder1",
            "ids": "folder1",
            "type": "folder_id",
        },
        {
            "name": "file1.txt",
            "ids": "file1",
            "type": "file_id",
        },
    ]


def test_update_agent_tool_metadata(
    session_client: TestClient, session: Session, user
) -> None:
    agent = get_factory("Agent", session).create(user=user)
    agent_tool_metadata = get_factory("AgentToolMetadata", session).create(
        user_id=user.id,
        agent_id=agent.id,
        tool_name=ToolName.Google_Drive,
        artifacts=[
            {
                "name": "/folder1",
                "ids": "folder1",
                "type": "folder_id",
            },
            {
                "name": "file1.txt",
                "ids": "file1",
                "type": "file_id",
            },
        ],
    )

    request_json = {
        "artifacts": [
            {
                "name": "/folder2",
                "ids": "folder2",
                "type": "folder_id",
            },
            {
                "name": "file2.txt",
                "ids": "file2",
                "type": "file_id",
            },
        ],
    }

    response = session_client.put(
        f"/v1/agents/{agent.id}/tool-metadata/{agent_tool_metadata.id}",
        json=request_json,
        headers={"User-Id": user.id},
    )

    assert response.status_code == 200
    response_agent_tool_metadata = response.json()
    assert response_agent_tool_metadata["id"] == agent_tool_metadata.id

    assert response_agent_tool_metadata["artifacts"] == [
        {
            "name": "/folder2",
            "ids": "folder2",
            "type": "folder_id",
        },
        {
            "name": "file2.txt",
            "ids": "file2",
            "type": "file_id",
        },
    ]


def test_get_agent_tool_metadata(
    session_client: TestClient, session: Session, user
) -> None:
    agent = get_factory("Agent", session).create(user=user)
    agent_tool_metadata_1 = get_factory("AgentToolMetadata", session).create(
        user_id=user.id,
        agent_id=agent.id,
        tool_name=ToolName.Google_Drive,
        artifacts=[
            {"name": "/folder", "ids": ["folder1", "folder2"], "type": "folder_ids"}
        ],
    )
    agent_tool_metadata_2 = get_factory("AgentToolMetadata", session).create(
        user_id=user.id,
        agent_id=agent.id,
        tool_name=ToolName.Search_File,
        artifacts=[{"name": "file.txt", "ids": ["file1", "file2"], "type": "file_ids"}],
    )

    response = session_client.get(
        f"/v1/agents/{agent.id}/tool-metadata", headers={"User-Id": user.id}
    )
    assert response.status_code == 200
    response_agent_tool_metadata = response.json()
    assert response_agent_tool_metadata[0]["id"] == agent_tool_metadata_1.id
    assert (
        response_agent_tool_metadata[0]["artifacts"] == agent_tool_metadata_1.artifacts
    )
    assert response_agent_tool_metadata[1]["id"] == agent_tool_metadata_2.id
    assert (
        response_agent_tool_metadata[1]["artifacts"] == agent_tool_metadata_2.artifacts
    )


def test_delete_agent_tool_metadata(
    session_client: TestClient, session: Session, user
) -> None:
    agent = get_factory("Agent", session).create(user=user)
    agent_tool_metadata = get_factory("AgentToolMetadata", session).create(
        user_id=user.id,
        agent_id=agent.id,
        tool_name=ToolName.Google_Drive,
        artifacts=[
            {
                "name": "/folder1",
                "ids": "folder1",
                "type": "folder_id",
            },
            {
                "name": "file1.txt",
                "ids": "file1",
                "type": "file_id",
            },
        ],
    )

    response = session_client.delete(
        f"/v1/agents/{agent.id}/tool-metadata/{agent_tool_metadata.id}",
        headers={"User-Id": user.id},
    )
    assert response.status_code == 200
    assert response.json() == {}

    agent_tool_metadata = session.get(AgentToolMetadata, agent_tool_metadata.id)
    assert agent_tool_metadata is None


def test_fail_delete_nonexistent_agent_tool_metadata(
    session_client: TestClient, session: Session, user
) -> None:
    agent = get_factory("Agent", session).create(user=user, id="456")
    response = session_client.delete(
        "/v1/agents/456/tool-metadata/789", headers={"User-Id": user.id}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Agent tool metadata with ID 789 not found."}
