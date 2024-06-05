from datetime import datetime

import pytest

from backend.crud import agent as agent_crud
from backend.database_models.agent import Agent,Deployment, Model
from backend.tests.factories import get_factory

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

    agent = agent_crud.get_agent(session, agent.id, user.id)
    assert agent.user_id == user.id
    assert agent.version == 1
    assert agent.name == "test"
    assert agent.description == "test"
    assert agent.preamble == "test"
    assert agent.temperature == 0.5
    assert agent.model == Model.COMMAND_R_PLUS
    assert agent.deployment == Deployment.COHERE_PLATFORM

def test_get_agent(session, user):
    _ = get_factory("Agent", session).create(id="1", user_id=user.id, name="test_agent")
    agent = agent_crud.get_agent(session, "1", user.id)
    assert agent.name == "test_agent"

def test_fail_get_nonexistant_agent(session, user):
    agent = agent_crud.get_agent(session, "123", user_id=user.id)
    assert agent is None
