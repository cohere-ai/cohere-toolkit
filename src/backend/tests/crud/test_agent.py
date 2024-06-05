from datetime import datetime

import pytest

from backend.crud import agent as agent_crud
from backend.database_models.agent import Agent,Deployment, Model
from backend.tests.factories import get_factory
from backend.schemas.agent import UpdateAgent

from sqlalchemy.exc import IntegrityError


def test_create_agent(session, user):
    agent_data = Agent(
        user_id=user.id,
        version=1,
        name="test",
        description="test",
        preamble="test",
        temperature=0.5,
        model=Model.COMMAND_R_PLUS,
        deployment=Deployment.COHERE_PLATFORM,
    )

    agent = agent_crud.create_agent(session, agent_data)
    assert agent.user_id == user.id
    assert agent.version == 1
    assert agent.name == "test"
    assert agent.description == "test"
    assert agent.preamble == "test"
    assert agent.temperature == 0.5
    assert agent.model == Model.COMMAND_R_PLUS
    assert agent.deployment == Deployment.COHERE_PLATFORM

    agent = agent_crud.get_agent(session, agent.id)
    assert agent.user_id == user.id
    assert agent.version == 1
    assert agent.name == "test"
    assert agent.description == "test"
    assert agent.preamble == "test"
    assert agent.temperature == 0.5
    assert agent.model == Model.COMMAND_R_PLUS
    assert agent.deployment == Deployment.COHERE_PLATFORM

def test_create_agent_duplicate_name_version(session, user):
    _ = get_factory("Agent", session).create(id="1", user_id=user.id, name="test_agent", version=1)

    agent_data = Agent(
        user_id=user.id,
        version=1,
        name="test_agent",
        description="test",
        preamble="test",
        temperature=0.5,
        model=Model.COMMAND_R_PLUS,
        deployment=Deployment.COHERE_PLATFORM,
    )
    
    with pytest.raises(IntegrityError):
        _ = agent_crud.create_agent(session, agent_data)

def test_get_agent(session, user):
    _ = get_factory("Agent", session).create(id="1", name="test_agent")
    agent = agent_crud.get_agent(session, "1")
    assert agent.name == "test_agent"

def test_fail_get_nonexistant_agent(session, user):
    agent = agent_crud.get_agent(session, "123")
    assert agent is None

def test_list_agents(session, user):
    length = 3
    for i in range(length):
        _ = get_factory("Agent", session).create(id=i, name=f"test_agent_{i}")

    agents = agent_crud.get_agents(session)
    assert len(agents) == length

def test_list_agents_empty(session, user):
    agents = agent_crud.get_agents(session)
    assert len(agents) == 0

def test_list_conversations_with_pagination(session, user):
    for i in range(10):
        get_factory("Agent", session).create(
            name=f"Agent {i}", user_id=user.id
        )

    agents = agent_crud.get_agents(
        session, offset=5, limit=5
    )
    assert len(agents) == 5

    for i, agent in enumerate(agents):
        assert agent.name == f"Agent {i + 5}"

def test_update_agent(session, user):
    agent = get_factory("Agent", session).create(
        name="test_agent",
        description="This is a test agent",
        version=1,
        preamble="test",
        temperature=0.5,
        user_id=user.id,
    )

    new_agent_data = UpdateAgent(
        name="new_test_agent",
        description="This is a new test agent",
        version=2,
        preamble="new_test",
        temperature=0.6,
    )

    agent = agent_crud.update_agent(
        session, agent, new_agent_data
    )
    assert agent.name == new_agent_data.name
    assert agent.description == new_agent_data.description
    assert agent.version == new_agent_data.version
    assert agent.preamble == new_agent_data.preamble
    assert agent.temperature == new_agent_data.temperature

def test_delete_agent(session, user):
    agent = get_factory("Agent", session).create(user_id=user.id)

    agent_crud.delete_agent(session, agent.id)

    agent = agent_crud.get_agent(session, agent.id)
    assert agent is None


def test_fail_delete_nonexistent_agent(session, user):
    agent = agent_crud.delete_agent(session, "123")
    assert agent is None

# TODO @scott-cohere: add test for delete cascades once tools, model, deployment DB changes are done
