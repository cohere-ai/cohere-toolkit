import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.expression import false

from backend.config.tools import Tool
from backend.crud import agent as agent_crud
from backend.database_models.agent import Agent
from backend.schemas.agent import AgentVisibility, UpdateAgentDB
from backend.tests.unit.factories import get_factory


def test_create_agent(session, user):
    deployment = get_factory("Deployment", session).create()
    model = get_factory("Model", session).create(deployment_id=deployment.id)
    agent_data = Agent(
        user_id=user.id,
        version=1,
        name="test",
        description="test",
        preamble="test",
        temperature=0.5,
        model_id=model.id,
        deployment_id=deployment.id,
        tools=[Tool.Wiki_Retriever_LangChain.value.ID, Tool.Search_File.value.ID],
        is_private=True,
    )

    agent = agent_crud.create_agent(session, agent_data)
    assert agent.user_id == user.id
    assert agent.version == 1
    assert agent.name == "test"
    assert agent.description == "test"
    assert agent.preamble == "test"
    assert agent.temperature == 0.5
    assert agent.tools == [Tool.Wiki_Retriever_LangChain.value.ID, Tool.Search_File.value.ID]
    assert agent.is_private
    assert agent.deployment == deployment.name
    assert agent.model == model.name

    agent = agent_crud.get_agent_by_id(session, agent.id, user.id)
    assert agent.user_id == user.id
    assert agent.version == 1
    assert agent.name == "test"
    assert agent.description == "test"
    assert agent.preamble == "test"
    assert agent.temperature == 0.5
    assert agent.tools == [Tool.Wiki_Retriever_LangChain.value.ID, Tool.Search_File.value.ID]
    assert agent.is_private
    assert agent.deployment == deployment.name
    assert agent.model == model.name


def test_create_agent_empty_non_required_fields(session, user):
    agent_data = Agent(
        user_id=user.id,
        name="test",
    )

    agent = agent_crud.create_agent(session, agent_data)
    assert agent.user_id == user.id
    assert agent.version == 1
    assert agent.name == "test"
    assert agent.description == ""
    assert agent.preamble == ""
    assert agent.temperature == 0.3
    assert agent.tools == []
    assert agent.is_private == false()
    agent = agent_crud.get_agent_by_id(session, agent.id, user.id)
    assert agent.user_id == user.id
    assert agent.version == 1
    assert agent.name == "test"
    assert agent.description == ""
    assert agent.preamble == ""
    assert agent.temperature == 0.3
    assert agent.tools == []


def test_create_agent_missing_name(session, user):
    agent_data = Agent(
        user_id=user.id,
    )

    with pytest.raises(IntegrityError):
        _ = agent_crud.create_agent(session, agent_data)


def test_create_agent_duplicate_name_version(session, user):
    _ = get_factory("Agent", session).create(
        id="1", user=user, name="test_agent", version=1
    )

    agent_data = Agent(
        user_id=user.id,
        version=1,
        name="test_agent",
        description="test",
        preamble="test",
        temperature=0.5,
        tools=[Tool.Wiki_Retriever_LangChain.value.ID, Tool.Search_File.value.ID],
    )

    with pytest.raises(IntegrityError):
        _ = agent_crud.create_agent(session, agent_data)


def test_get_agent_by_id(session, user):
    _ = get_factory("Agent", session).create(id="1", name="test_agent", user=user)
    agent = agent_crud.get_agent_by_id(session, "1", user.id)
    assert agent.id == "1"
    assert agent.name == "test_agent"


def test_get_agent_by_name(session, user):
    _ = get_factory("Agent", session).create(id="1", name="test_agent", user=user)
    agent = agent_crud.get_agent_by_name(session, "test_agent", user.id)
    assert agent.id == "1"
    assert agent.name == "test_agent"


def test_fail_get_nonexistant_agent(session, user):
    agent = agent_crud.get_agent_by_id(session, "123", user.id)
    assert agent is None


def test_get_private_agent_by_another_user(session, user):
    user2 = get_factory("User", session).create()
    agent = get_factory("Agent", session).create(
        id="1", name="test_agent", user_id=user.id, is_private=True
    )
    agent = agent_crud.get_agent_by_id(session, agent.id, user2.id)
    assert agent is None


def test_list_public_agents(session, user):
    # Delete default agent
    session.query(Agent).delete()
    length = 3
    for i in range(length):
        _ = get_factory("Agent", session).create(
            id=i, name=f"test_agent_{i}", user=user, is_private=False
        )

    public_agents = agent_crud.get_agents(
        session, user_id=user.id, visibility=AgentVisibility.PUBLIC
    )
    assert len(public_agents) == length

    private_agents = agent_crud.get_agents(
        session, user_id=user.id, visibility=AgentVisibility.PRIVATE
    )
    assert len(private_agents) == 0


def test_list_public_agents_empty(session, user):
    # Delete default agent
    session.query(Agent).delete()
    agents = agent_crud.get_agents(
        session, user_id=user.id, visibility=AgentVisibility.PUBLIC
    )
    assert len(agents) == 0


def test_list_private_agents(session, user):
    length = 3
    for i in range(length):
        _ = get_factory("Agent", session).create(
            id=i, name=f"test_agent_{i}", user=user, is_private=True
        )

    user2 = get_factory("User", session).create()
    for i in range(length, length * 2):
        _ = get_factory("Agent", session).create(
            id=i, name=f"test_agent_{i}", user=user2, is_private=True
        )

    agents = agent_crud.get_agents(session, user.id, visibility=AgentVisibility.PRIVATE)
    assert len(agents) == length

    agents = agent_crud.get_agents(session, user.id, visibility=AgentVisibility.PUBLIC)
    assert len(agents) == 0


def test_list_public_and_private_agents(session, user):
    length = 3
    for i in range(length):
        _ = get_factory("Agent", session).create(
            id=i, name=f"test_agent_{i}", user=user, is_private=True
        )

    for i in range(length, length * 2):
        _ = get_factory("Agent", session).create(
            id=i, name=f"test_agent_{i}", user=user, is_private=False
        )

    agents = agent_crud.get_agents(session, user.id, visibility=AgentVisibility.ALL)
    assert len(agents) == length * 2


def test_list_agents_with_pagination(session, user):
    for i in range(10):
        get_factory("Agent", session).create(name=f"Agent {i}", user=user)

    agents = agent_crud.get_agents(
        session, user.id, offset=5, limit=5, visibility=AgentVisibility.ALL
    )
    assert len(agents) == 5


def test_update_agent(session, user):
    deployment = get_factory("Deployment", session).create()
    model = get_factory("Model", session).create(deployment_id=deployment.id)
    agent = get_factory("Agent", session).create(
        name="test_agent",
        description="This is a test agent",
        version=1,
        preamble="test",
        temperature=0.5,
        user=user,
        deployment_id=deployment.id,
        model_id=model.id,
        tools=[Tool.Wiki_Retriever_LangChain.value.ID, Tool.Search_File.value.ID],
    )

    new_deployment = get_factory("Deployment", session).create()
    new_model = get_factory("Model", session).create(deployment_id=new_deployment.id)
    new_agent_data = UpdateAgentDB(
        name="new_test_agent",
        description="This is a new test agent",
        version=2,
        preamble="new_test",
        temperature=0.6,
        tools=[Tool.Python_Interpreter.value.ID, Tool.Calculator.value.ID],
        model_id=new_model.id,
        deployment_id=new_deployment.id,
    )

    agent = agent_crud.update_agent(session, agent, new_agent_data, user.id)
    assert agent.name == new_agent_data.name
    assert agent.description == new_agent_data.description
    assert agent.version == new_agent_data.version
    assert agent.preamble == new_agent_data.preamble
    assert agent.temperature == new_agent_data.temperature
    assert agent.tools == [Tool.Python_Interpreter.value.ID, Tool.Calculator.value.ID]
    assert agent.model_id == new_model.id
    assert agent.deployment_id == new_deployment.id
    assert agent.model == new_model.name
    assert agent.deployment == new_deployment.name


def test_delete_agent(session, user):
    agent = get_factory("Agent", session).create(user=user)

    agent_crud.delete_agent(session, agent.id, user.id)

    agent = agent_crud.get_agent_by_id(session, agent.id, user.id)
    assert agent is None


def test_fail_delete_nonexistent_agent(session, user):
    status = agent_crud.delete_agent(session, "123", user.id)
    assert status is False


def test_delete_agent_by_another_user(session, user):
    user2 = get_factory("User", session).create()
    agent = get_factory("Agent", session).create(user=user, is_private=True)

    status = agent_crud.delete_agent(session, agent.id, user2.id)
    assert status is False


def test_get_agents_by_user_id(session, user):
    deployment = get_factory("Deployment", session).create()
    model = get_factory("Model", session).create(deployment_id=deployment.id)
    agent = get_factory("Agent", session).create(user=user, deployment_id=deployment.id, model_id=model.id)

    agents = agent_crud.get_agents(session, user_id=user.id)
    assert len(agents) == 1
    assert agents[0].user_id == user.id
    assert agents[0].id == agent.id


def test_get_agents_by_organization_id(session):
    organization = get_factory("Organization", session).create()
    user = get_factory("User", session).create()
    user.organizations.append(organization)
    deployment = get_factory("Deployment", session).create()
    model = get_factory("Model", session).create(deployment_id=deployment.id)
    agent = get_factory("Agent", session).create(user=user, organization=organization, deployment_id=deployment.id,
                                                 model_id=model.id)

    agents = agent_crud.get_agents(session, user.id, organization_id=organization.id)
    assert len(agents) == 1
    assert agents[0].user_id == user.id
    assert agents[0].id == agent.id
