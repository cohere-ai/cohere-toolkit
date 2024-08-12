import pytest
from sqlalchemy.exc import IntegrityError

from backend.config.tools import ToolName
from backend.crud import agent_tool_metadata as agent_tool_metadata_crud
from backend.database_models.agent_tool_metadata import AgentToolMetadata
from backend.schemas.agent import UpdateAgentToolMetadataRequest
from backend.tests.factories import get_factory

mock_artifact_1 = {
    "id": "1T",
    "url": "hellotesturl.com/document1",
    "name": "document-test1",
    "type": "document",
}
mock_artifact_2 = {
    "id": "2T",
    "url": "hellotesturl.com/document2",
    "name": "document-test2",
    "type": "document",
}


def test_create_agent_tool_metadata(session, user):
    agent = get_factory("Agent", session).create(
        id="1", name="test_agent", tools=[ToolName.Google_Drive], user=user
    )

    agent_tool_metadata_data = AgentToolMetadata(
        user_id=user.id,
        agent_id=agent.id,
        tool_name=ToolName.Google_Drive,
        artifacts=[mock_artifact_1],
    )
    agent_tool_metadata = agent_tool_metadata_crud.create_agent_tool_metadata(
        session, agent_tool_metadata_data
    )
    assert agent_tool_metadata.user_id == user.id
    assert agent_tool_metadata.agent_id == agent.id
    assert agent_tool_metadata.tool_name == ToolName.Google_Drive
    assert agent_tool_metadata.artifacts == [mock_artifact_1]
    assert agent_tool_metadata.artifacts[0]["type"] == "document"

    agent_tool_metadata = agent_tool_metadata_crud.get_agent_tool_metadata_by_id(
        session, agent_tool_metadata.id
    )
    assert agent_tool_metadata.user_id == user.id
    assert agent_tool_metadata.agent_id == agent.id
    assert agent_tool_metadata.tool_name == ToolName.Google_Drive
    assert agent_tool_metadata.artifacts == [mock_artifact_1]
    assert agent_tool_metadata.artifacts[0]["type"] == "document"


def test_create_agent_missing_agent_id(session, user):
    agent_tool_metadata_data = AgentToolMetadata(
        user_id=user.id,
        tool_name=ToolName.Google_Drive,
        artifacts=[mock_artifact_1],
    )
    with pytest.raises(IntegrityError):
        _ = agent_tool_metadata_crud.create_agent_tool_metadata(
            session, agent_tool_metadata_data
        )


def test_create_agent_missing_tool_name(session, user):
    agent = get_factory("Agent", session).create(
        id="1", name="test_agent", tools=[ToolName.Google_Drive], user=user
    )

    agent_tool_metadata_data = AgentToolMetadata(
        user_id=user.id,
        agent_id=agent.id,
        artifacts=[mock_artifact_1],
    )
    with pytest.raises(IntegrityError):
        _ = agent_tool_metadata_crud.create_agent_tool_metadata(
            session, agent_tool_metadata_data
        )


def test_create_agent_missing_user_id(session, user):
    agent = get_factory("Agent", session).create(
        id="1", name="test_agent", tools=[ToolName.Google_Drive], user=user
    )

    agent_tool_metadata_data = AgentToolMetadata(
        agent_id=agent.id,
        tool_name=ToolName.Google_Drive,
        artifacts=[mock_artifact_1],
        user_id="123",
    )
    with pytest.raises(IntegrityError):
        _ = agent_tool_metadata_crud.create_agent_tool_metadata(
            session, agent_tool_metadata_data
        )


def test_update_agent_tool_metadata(session, user):
    agent = get_factory("Agent", session).create(user=user)
    original_agent_tool_metadata = get_factory("AgentToolMetadata", session).create(
        user_id=user.id,
        agent_id=agent.id,
        tool_name=ToolName.Google_Drive,
        artifacts=[mock_artifact_1],
    )

    new_agent_tool_metadata_data = UpdateAgentToolMetadataRequest(
        artifacts=[mock_artifact_1],
    )

    agent_tool_metadata = agent_tool_metadata_crud.update_agent_tool_metadata(
        session, original_agent_tool_metadata, new_agent_tool_metadata_data
    )
    assert agent_tool_metadata.user_id == original_agent_tool_metadata.user_id
    assert agent_tool_metadata.agent_id == original_agent_tool_metadata.agent_id
    assert agent_tool_metadata.tool_name == original_agent_tool_metadata.tool_name
    assert agent_tool_metadata.artifacts == new_agent_tool_metadata_data.artifacts


def test_get_agent_tool_metadata_by_id(session, user):
    agent = get_factory("Agent", session).create(user=user)
    agent_tool_metadata = get_factory("AgentToolMetadata", session).create(
        user_id=user.id,
        agent_id=agent.id,
        tool_name=ToolName.Google_Drive,
        artifacts=[mock_artifact_1, mock_artifact_2],
    )
    agent_tool_metadata = agent_tool_metadata_crud.get_agent_tool_metadata_by_id(
        session, agent_tool_metadata.id
    )
    assert agent_tool_metadata.user_id == user.id
    assert agent_tool_metadata.agent_id == agent.id
    assert agent_tool_metadata.tool_name == ToolName.Google_Drive
    assert agent_tool_metadata.artifacts == [mock_artifact_1, mock_artifact_2]


def test_get_all_agent_tool_metadata_by_agent_id(session, user):
    agent1 = get_factory("Agent", session).create(user=user)
    agent2 = get_factory("Agent", session).create(user=user)

    # Add a random entry to test
    _ = get_factory("AgentToolMetadata", session).create(
        user_id=user.id,
        agent_id=agent1.id,
        tool_name=ToolName.Google_Drive,
        artifacts=[mock_artifact_1, mock_artifact_2],
    )

    # Constraint was added preventing multiple entries for the same user + agent + tool so fixing to change the tool used
    i = 0
    for tool in ToolName:
        i += 1
        agent = get_factory("Agent", session).create(user_id=user.id)
        _ = get_factory("AgentToolMetadata", session).create(
            id=f"{i}",
            tool_name=tool.value,
            artifacts=[mock_artifact_1, mock_artifact_2],
            user_id=user.id,
            agent_id=agent2.id,
        )

    all_agent_tool_metadata = (
        agent_tool_metadata_crud.get_all_agent_tool_metadata_by_agent_id(
            session, agent_id=agent2.id
        )
    )
    assert len(all_agent_tool_metadata) == len(ToolName)


def test_delete_agent_tool_metadata_by_id(session, user):
    agent = get_factory("Agent", session).create(user=user)
    agent_tool_metadata = get_factory("AgentToolMetadata", session).create(
        user_id=user.id,
        agent_id=agent.id,
        tool_name=ToolName.Google_Drive,
        artifacts=[mock_artifact_1, mock_artifact_2],
    )

    agent_tool_metadata_crud.delete_agent_tool_metadata_by_id(
        session, agent_tool_metadata.id
    )

    agent_tool_metadata = agent_tool_metadata_crud.get_agent_tool_metadata_by_id(
        session, agent_tool_metadata.id
    )
    assert agent_tool_metadata is None
