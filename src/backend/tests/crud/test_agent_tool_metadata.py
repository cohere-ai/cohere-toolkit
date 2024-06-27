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
        artifact_id="folder_id",
    )
    agent_tool_metadata = agent_tool_metadata_crud.create_agent_tool_metadata(
        session, agent_tool_metadata_data
    )
    assert agent_tool_metadata.user_id == user.id
    assert agent_tool_metadata.agent_id == agent.id
    assert agent_tool_metadata.tool_name == ToolName.Google_Drive
    assert agent_tool_metadata.artifact_id == "folder_id"

    agent_tool_metadata = (
        agent_tool_metadata_crud.get_agent_tool_metadata_by_agent_id_and_tool_name(
            session, agent.id, ToolName.Google_Drive
        )
    )
    assert agent_tool_metadata.user_id == user.id
    assert agent_tool_metadata.agent_id == agent.id
    assert agent_tool_metadata.tool_name == ToolName.Google_Drive
    assert agent_tool_metadata.artifact_id == "folder_id"


def test_create_agent_missing_agent_id(session, user):
    agent_tool_metadata_data = AgentToolMetadata(
        user_id=user.id,
        tool_name=ToolName.Google_Drive,
        artifact_id="folder_id",
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
        artifact_id="folder_id",
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
        artifact_id="folder_id",
    )
    with pytest.raises(IntegrityError):
        _ = agent_tool_metadata_crud.create_agent_tool_metadata(
            session, agent_tool_metadata_data
        )


def test_get_agent_tool_metadata_by_agent_id_and_tool_name(session, user):
    agent = get_factory("Agent", session).create(
        id="1", name="test_agent", tools=[ToolName.Google_Drive]
    )
    _ = get_factory("AgentToolMetadata", session).create(
        user_id=user.id,
        agent_id=agent.id,
        tool_name=ToolName.Google_Drive,
        artifact_id="folder_id",
    )

    agent_tool_metadata = (
        agent_tool_metadata_crud.get_agent_tool_metadata_by_agent_id_and_tool_name(
            session, agent.id, ToolName.Google_Drive
        )
    )
    assert agent_tool_metadata.user_id == user.id
    assert agent_tool_metadata.agent_id == agent.id
    assert agent_tool_metadata.tool_name == ToolName.Google_Drive
    assert agent_tool_metadata.artifact_id == "folder_id"


def test_update_agent_tool_metadata(session, user):
    agent = get_factory("Agent", session).create(
        id="1", name="test_agent", tools=[ToolName.Google_Drive]
    )
    original_agent_tool_metadata = get_factory("AgentToolMetadata", session).create(
        user_id=user.id,
        agent_id=agent.id,
        tool_name=ToolName.Google_Drive,
        artifact_id="folder_id",
    )

    new_agent_tool_metadata_data = UpdateAgentToolMetadata(
        tool_name=ToolName.Google_Drive,
        artifact_id="new_folder_id",
    )

    agent_tool_metadata = agent_tool_metadata_crud.update_agent_tool_metadata(
        session, original_agent_tool_metadata, new_agent_tool_metadata_data
    )
    assert agent_tool_metadata.user_id == original_agent_tool_metadata.user_id
    assert agent_tool_metadata.agent_id == original_agent_tool_metadata.agent_id
    assert agent_tool_metadata.tool_name == new_agent_tool_metadata_data.tool_name
    assert agent_tool_metadata.artifact_id == new_agent_tool_metadata_data.artifact_id
