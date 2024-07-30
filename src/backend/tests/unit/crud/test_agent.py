import pytest
from sqlalchemy.exc import IntegrityError

from backend.config.deployments import ModelDeploymentName
from backend.config.tools import ToolName
from backend.crud import agent as agent_crud
from backend.database_models.agent import Agent
from backend.schemas.agent import UpdateAgentRequest
from backend.tests.factories import get_factory


def test_create_agent(session, user):
    agent_data = Agent(
        user_id=user.id,
        version=1,
        name="test",
        description="test",
        preamble="test",
        temperature=0.5,
        tools=[ToolName.Wiki_Retriever_LangChain, ToolName.Search_File],
        model="command-r-plus",
        deployment=ModelDeploymentName.CoherePlatform,
    )

    agent = agent_crud.create_agent(session, agent_data)
    assert agent.user_id == user.id
    assert agent.version == 1
    assert agent.name == "test"
    assert agent.description == "test"
    assert agent.preamble == "test"
    assert agent.temperature == 0.5
    assert agent.tools == [ToolName.Wiki_Retriever_LangChain, ToolName.Search_File]
    assert agent.model == "command-r-plus"
    assert agent.deployment == ModelDeploymentName.CoherePlatform

    agent = agent_crud.get_agent_by_id(session, agent.id)
    assert agent.user_id == user.id
    assert agent.version == 1
    assert agent.name == "test"
    assert agent.description == "test"
    assert agent.preamble == "test"
    assert agent.temperature == 0.5
    assert agent.tools == [ToolName.Wiki_Retriever_LangChain, ToolName.Search_File]
    assert agent.model == "command-r-plus"
    assert agent.deployment == ModelDeploymentName.CoherePlatform


def test_create_agent_empty_non_required_fields(session, user):
    agent_data = Agent(
        user_id=user.id,
        name="test",
        model="command-r-plus",
        deployment=ModelDeploymentName.CoherePlatform,
    )

    agent = agent_crud.create_agent(session, agent_data)
    assert agent.user_id == user.id
    assert agent.version == 1
    assert agent.name == "test"
    assert agent.description == ""
    assert agent.preamble == ""
    assert agent.temperature == 0.3
    assert agent.tools == []
    assert agent.model == "command-r-plus"
    assert agent.deployment == ModelDeploymentName.CoherePlatform

    agent = agent_crud.get_agent_by_id(session, agent.id)
    assert agent.user_id == user.id
    assert agent.version == 1
    assert agent.name == "test"
    assert agent.description == ""
    assert agent.preamble == ""
    assert agent.temperature == 0.3
    assert agent.tools == []
    assert agent.model == "command-r-plus"
    assert agent.deployment == ModelDeploymentName.CoherePlatform


def test_create_agent_missing_name(session, user):
    agent_data = Agent(
        user_id=user.id,
        model="command-r-plus",
        deployment=ModelDeploymentName.CoherePlatform,
    )

    with pytest.raises(IntegrityError):
        _ = agent_crud.create_agent(session, agent_data)


def test_create_agent_missing_model(session, user):
    agent_data = Agent(
        user_id=user.id,
        name="test",
        deployment=ModelDeploymentName.CoherePlatform,
    )

    with pytest.raises(IntegrityError):
        _ = agent_crud.create_agent(session, agent_data)


def test_create_agent_duplicate_name_version(session, user):
    _ = get_factory("Agent", session).create(
        id="1", user_id=user.id, name="test_agent", version=1
    )

    agent_data = Agent(
        user_id=user.id,
        version=1,
        name="test_agent",
        description="test",
        preamble="test",
        temperature=0.5,
        tools=[ToolName.Wiki_Retriever_LangChain, ToolName.Search_File],
        model="command-r-plus",
        deployment=ModelDeploymentName.CoherePlatform,
    )

    with pytest.raises(IntegrityError):
        _ = agent_crud.create_agent(session, agent_data)


def test_get_agent_by_id(session, user):
    _ = get_factory("Agent", session).create(id="1", name="test_agent", user_id=user.id)
    agent = agent_crud.get_agent_by_id(session, "1")
    assert agent.id == "1"
    assert agent.name == "test_agent"


def test_get_agent_by_name(session, user):
    _ = get_factory("Agent", session).create(id="1", name="test_agent", user_id=user.id)
    agent = agent_crud.get_agent_by_name(session, "test_agent")
    assert agent.id == "1"
    assert agent.name == "test_agent"


def test_fail_get_nonexistant_agent(session, user):
    agent = agent_crud.get_agent_by_id(session, "123")
    assert agent is None


def test_list_agents(session, user):
    length = 3
    for i in range(length):
        _ = get_factory("Agent", session).create(
            id=i, name=f"test_agent_{i}", user_id=user.id
        )

    agents = agent_crud.get_agents(session)
    assert len(agents) == length


def test_list_agents_empty(session, user):
    agents = agent_crud.get_agents(session)
    assert len(agents) == 0


def test_list_conversations_with_pagination(session, user):
    for i in range(10):
        get_factory("Agent", session).create(name=f"Agent {i}", user_id=user.id)

    agents = agent_crud.get_agents(session, offset=5, limit=5)
    assert len(agents) == 5


def test_update_agent(session, user):
    agent = get_factory("Agent", session).create(
        name="test_agent",
        description="This is a test agent",
        version=1,
        preamble="test",
        temperature=0.5,
        user_id=user.id,
        tools=[ToolName.Wiki_Retriever_LangChain, ToolName.Search_File],
    )

    new_agent_data = UpdateAgentRequest(
        name="new_test_agent",
        description="This is a new test agent",
        version=2,
        preamble="new_test",
        temperature=0.6,
        tools=[ToolName.Python_Interpreter, ToolName.Calculator],
    )

    agent = agent_crud.update_agent(session, agent, new_agent_data)
    assert agent.name == new_agent_data.name
    assert agent.description == new_agent_data.description
    assert agent.version == new_agent_data.version
    assert agent.preamble == new_agent_data.preamble
    assert agent.temperature == new_agent_data.temperature
    assert agent.tools == [ToolName.Python_Interpreter, ToolName.Calculator]


def test_delete_agent(session, user):
    agent = get_factory("Agent", session).create(user_id=user.id)

    agent_crud.delete_agent(session, agent.id)

    agent = agent_crud.get_agent_by_id(session, agent.id)
    assert agent is None


def test_fail_delete_nonexistent_agent(session, user):
    agent = agent_crud.delete_agent(session, "123")
    assert agent is None


# TODO @scott-cohere: add test for delete cascades once tools, model, deployment DB changes are done
