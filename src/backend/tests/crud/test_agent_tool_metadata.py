from datetime import datetime

import pytest
from sqlalchemy.exc import IntegrityError

from backend.config.tools import ToolName
from backend.crud import agent_tool_metadata as agent_tool_metadata_crud
from backend.database_models.agent_tool_metadata import AgentToolMetadata
from backend.schemas.agent import UpdateAgentToolMetadata
from backend.tests.factories import get_factory


def test_create_agent_tool_metadata(session, user):
    agent = get_factory("Agent", session).create(
        id="1", name="test_agent", tools=[ToolName.Google_Drive]
    )

    agent_tool_metadata_data = AgentToolMetadata(
        user_id=user.id,
        agent_id=agent.id,
        tool_name=ToolName.Google_Drive,
        artifacts=[{"file": "file_id"}],
    )
    agent_tool_metadata = agent_tool_metadata_crud.create_agent_tool_metadata(
        session, agent_tool_metadata_data
    )
    assert agent_tool_metadata.user_id == user.id
    assert agent_tool_metadata.agent_id == agent.id
    assert agent_tool_metadata.tool_name == ToolName.Google_Drive
    assert agent_tool_metadata.artifacts == [{"file": "file_id"}]

    agent_tool_metadata = agent_tool_metadata_crud.get_agent_tool_metadata_by_id(
        session, agent_tool_metadata.id
    )
    assert agent_tool_metadata.user_id == user.id
    assert agent_tool_metadata.agent_id == agent.id
    assert agent_tool_metadata.tool_name == ToolName.Google_Drive
    assert agent_tool_metadata.artifacts == [{"file": "file_id"}]


def test_create_agent_missing_agent_id(session, user):
    agent_tool_metadata_data = AgentToolMetadata(
        user_id=user.id,
        tool_name=ToolName.Google_Drive,
        artifacts=[{"file": "file_id"}],
    )
    with pytest.raises(IntegrityError):
        _ = agent_tool_metadata_crud.create_agent_tool_metadata(
            session, agent_tool_metadata_data
        )


def test_create_agent_missing_tool_name(session, user):
    agent = get_factory("Agent", session).create(
        id="1", name="test_agent", tools=[ToolName.Google_Drive]
    )

    agent_tool_metadata_data = AgentToolMetadata(
        user_id=user.id,
        agent_id=agent.id,
        artifacts=[{"file": "file_id"}],
    )
    with pytest.raises(IntegrityError):
        _ = agent_tool_metadata_crud.create_agent_tool_metadata(
            session, agent_tool_metadata_data
        )


def test_create_agent_missing_user_id(session, user):
    agent = get_factory("Agent", session).create(
        id="1", name="test_agent", tools=[ToolName.Google_Drive]
    )

    agent_tool_metadata_data = AgentToolMetadata(
        agent_id=agent.id,
        tool_name=ToolName.Google_Drive,
        artifacts=[{"file": "file_id"}],
    )
    with pytest.raises(IntegrityError):
        _ = agent_tool_metadata_crud.create_agent_tool_metadata(
            session, agent_tool_metadata_data
        )


def test_update_agent_tool_metadata(session, user):
    agent = get_factory("Agent", session).create(user_id=user.id)
    original_agent_tool_metadata = get_factory("AgentToolMetadata", session).create(
        user_id=user.id,
        agent_id=agent.id,
        tool_name=ToolName.Google_Drive,
        artifacts=[{"file": "file_id"}],
    )

    new_agent_tool_metadata_data = UpdateAgentToolMetadata(
        artifacts=[{"file": "new_file_id"}],
    )

    agent_tool_metadata = agent_tool_metadata_crud.update_agent_tool_metadata(
        session, original_agent_tool_metadata, new_agent_tool_metadata_data
    )
    assert agent_tool_metadata.user_id == original_agent_tool_metadata.user_id
    assert agent_tool_metadata.agent_id == original_agent_tool_metadata.agent_id
    assert agent_tool_metadata.tool_name == original_agent_tool_metadata.tool_name
    assert agent_tool_metadata.artifacts == new_agent_tool_metadata_data.artifacts


def test_get_agent_tool_metadata_by_id(session, user):
    agent = get_factory("Agent", session).create(user_id=user.id)
    agent_tool_metadata = get_factory("AgentToolMetadata", session).create(
        user_id=user.id,
        agent_id=agent.id,
        tool_name=ToolName.Google_Drive,
        artifacts=[{"file_ids": ["file2", "file2"]}],
    )
    agent_tool_metadata = agent_tool_metadata_crud.get_agent_tool_metadata_by_id(
        session, agent_tool_metadata.id
    )
    assert agent_tool_metadata.user_id == user.id
    assert agent_tool_metadata.agent_id == agent.id
    assert agent_tool_metadata.tool_name == ToolName.Google_Drive
    assert agent_tool_metadata.artifacts == [{"file_ids": ["file2", "file2"]}]


def test_get_all_agent_tool_metadata_by_agent_id(session, user):
    agent1 = get_factory("Agent", session).create(user_id=user.id)
    agent2 = get_factory("Agent", session).create(user_id=user.id)

    # Add a random entry to test
    _ = get_factory("AgentToolMetadata", session).create(
        user_id=user.id,
        agent_id=agent1.id,
        tool_name=ToolName.Google_Drive,
        artifacts=[{"file_ids": ["file2", "file2"]}],
    )

    _ = get_factory("AgentToolMetadata", session).create(
        user_id=user.id,
        agent_id=agent1.id,
        tool_name=ToolName.Wiki_Retriever_LangChain,
        artifacts=[],
    )

    _ = get_factory("AgentToolMetadata", session).create(
        user_id=user.id,
        agent_id=agent2.id,
        tool_name=ToolName.Google_Drive,
        artifacts=[{"file_ids": ["file2", "file2"]}],
    )

    all_agent_tool_metadata = (
        agent_tool_metadata_crud.get_all_agent_tool_metadata_by_agent_id(
            session, agent_id=agent1.id
        )
    )
    assert len(all_agent_tool_metadata) == 2


def test_delete_agent_tool_metadata_by_id(session, user):
    agent = get_factory("Agent", session).create(user_id=user.id)
    agent_tool_metadata = get_factory("AgentToolMetadata", session).create(
        user_id=user.id,
        agent_id=agent.id,
        tool_name=ToolName.Google_Drive,
        artifacts=[{"file_ids": ["file2", "file2"]}],
    )

    agent_tool_metadata_crud.delete_agent_tool_metadata_by_id(
        session, agent_tool_metadata.id
    )

    agent_tool_metadata = agent_tool_metadata_crud.get_agent_tool_metadata_by_id(
        session, agent_tool_metadata.id
    )
    assert agent_tool_metadata is None
