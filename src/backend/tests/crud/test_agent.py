import pytest
from sqlalchemy.exc import IntegrityError

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
    )

    agent = agent_crud.create_agent(session, agent_data)
    assert agent.user_id == user.id
    assert agent.version == 1
    assert agent.name == "test"
    assert agent.description == "test"
    assert agent.preamble == "test"
    assert agent.temperature == 0.5

    agent = agent_crud.get_agent_by_id(session, agent.id)
    assert agent.user_id == user.id
    assert agent.version == 1
    assert agent.name == "test"
    assert agent.description == "test"
    assert agent.preamble == "test"
    assert agent.temperature == 0.5


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

    agent = agent_crud.get_agent_by_id(session, agent.id)
    assert agent.user_id == user.id
    assert agent.version == 1
    assert agent.name == "test"
    assert agent.description == ""
    assert agent.preamble == ""
    assert agent.temperature == 0.3


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
    )

    with pytest.raises(IntegrityError):
        _ = agent_crud.create_agent(session, agent_data)


def test_get_agent_by_id(session, user):
    _ = get_factory("Agent", session).create(id="1", name="test_agent", user=user)
    agent = agent_crud.get_agent_by_id(session, "1")
    assert agent.id == "1"
    assert agent.name == "test_agent"


def test_get_agent_by_name(session, user):
    _ = get_factory("Agent", session).create(id="1", name="test_agent", user=user)
    agent = agent_crud.get_agent_by_name(session, "test_agent")
    assert agent.id == "1"
    assert agent.name == "test_agent"


def test_fail_get_nonexistant_agent(session, user):
    agent = agent_crud.get_agent_by_id(session, "123")
    assert agent is None


def test_list_agents(session, user):
    # Delete default agent
    session.query(Agent).delete()
    length = 3
    for i in range(length):
        _ = get_factory("Agent", session).create(
            id=i, name=f"test_agent_{i}", user=user
        )

    agents = agent_crud.get_agents(session)
    assert len(agents) == length


def test_list_agents_empty(session, user):
    # Delete default agent
    session.query(Agent).delete()
    agents = agent_crud.get_agents(session)
    assert len(agents) == 0


def test_list_conversations_with_pagination(session, user):
    for i in range(10):
        get_factory("Agent", session).create(name=f"Agent {i}", user=user)

    agents = agent_crud.get_agents(session, offset=5, limit=5)
    assert len(agents) == 5


def test_update_agent(session, user):
    agent = get_factory("Agent", session).create(
        name="test_agent",
        description="This is a test agent",
        version=1,
        preamble="test",
        temperature=0.5,
        user=user,
    )

    new_agent_data = UpdateAgentRequest(
        name="new_test_agent",
        description="This is a new test agent",
        version=2,
        preamble="new_test",
        temperature=0.6,
    )

    agent = agent_crud.update_agent(session, agent, new_agent_data)
    assert agent.name == new_agent_data.name
    assert agent.description == new_agent_data.description
    assert agent.version == new_agent_data.version
    assert agent.preamble == new_agent_data.preamble
    assert agent.temperature == new_agent_data.temperature


def test_delete_agent(session, user):
    agent = get_factory("Agent", session).create(user=user)

    agent_crud.delete_agent(session, agent.id)

    agent = agent_crud.get_agent_by_id(session, agent.id)
    assert agent is None


def test_fail_delete_nonexistent_agent(session, user):
    agent = agent_crud.delete_agent(session, "123")
    assert agent is None


def test_get_association_by_deployment_name(session, user):
    agent = get_factory("Agent", session).create(user=user)
    deployment = get_factory("Deployment", session).create()
    model = get_factory("Model", session).create(deployment_id=deployment.id)
    new_association = get_factory("AgentDeploymentModel", session).create(
        agent=agent, deployment=deployment, model=model
    )
    association = agent_crud.get_association_by_deployment_name(
        session, agent, deployment.name
    )
    assert association.agent_id == agent.id
    assert association.deployment_id == deployment.id
    assert association.model_id == model.id
    assert new_association.deployment.name == deployment.name


def test_get_association_by_deployment_id(session, user):
    agent = get_factory("Agent", session).create(user=user)
    deployment = get_factory("Deployment", session).create()
    model = get_factory("Model", session).create(deployment_id=deployment.id)
    new_association = get_factory("AgentDeploymentModel", session).create(
        agent=agent,
        deployment=deployment,
        model=model,
        is_default_deployment=True,
        is_default_model=True,
    )
    association = agent_crud.get_association_by_deployment_id(
        session, agent, deployment.id
    )
    assert association.agent_id == agent.id
    assert association.deployment_id == deployment.id
    assert association.model_id == model.id
    assert new_association.deployment.id == deployment.id


def test_get_agents_by_user_id(session, user):
    agent = get_factory("Agent", session).create(user=user)
    deployment = get_factory("Deployment", session).create()
    model = get_factory("Model", session).create(deployment_id=deployment.id)
    new_association = get_factory("AgentDeploymentModel", session).create(
        agent=agent,
        deployment=deployment,
        model=model,
        is_default_deployment=True,
        is_default_model=True,
    )
    agents = agent_crud.get_agents(session, user_id=user.id)
    assert len(agents) == 1
    assert agents[0].user_id == user.id
    assert agents[0].id == agent.id


def test_get_agents_by_organization_id(session):
    organization = get_factory("Organization", session).create()
    user = get_factory("User", session).create()
    user.organizations.append(organization)
    agent = get_factory("Agent", session).create(user=user, organization=organization)
    deployment = get_factory("Deployment", session).create()
    model = get_factory("Model", session).create(deployment_id=deployment.id)
    new_association = get_factory("AgentDeploymentModel", session).create(
        agent=agent,
        deployment=deployment,
        model=model,
        is_default_deployment=True,
        is_default_model=True,
    )
    agents = agent_crud.get_agents(session, organization_id=organization.id)
    assert len(agents) == 1
    assert agents[0].user_id == user.id
    assert agents[0].id == agent.id


def test_get_agent_model_deployment_association(session):
    organization = get_factory("Organization", session).create()
    user = get_factory("User", session).create()
    user.organizations.append(organization)
    agent = get_factory("Agent", session).create(user=user, organization=organization)
    deployment = get_factory("Deployment", session).create()
    model = get_factory("Model", session).create(deployment_id=deployment.id)
    new_association = get_factory("AgentDeploymentModel", session).create(
        agent=agent,
        deployment=deployment,
        model=model,
        is_default_deployment=True,
        is_default_model=True,
    )
    association = agent_crud.get_agent_model_deployment_association(
        session, agent, model.id, deployment.id
    )

    assert association.id == new_association.id


def test_delete_agent_model_deployment_association(session):
    organization = get_factory("Organization", session).create()
    user = get_factory("User", session).create()
    user.organizations.append(organization)
    agent = get_factory("Agent", session).create(user=user, organization=organization)
    deployment = get_factory("Deployment", session).create()
    model = get_factory("Model", session).create(deployment_id=deployment.id)
    new_association = get_factory("AgentDeploymentModel", session).create(
        agent=agent,
        deployment=deployment,
        model=model,
        is_default_deployment=True,
        is_default_model=True,
    )
    agent_crud.delete_agent_model_deployment_association(
        session, agent, model.id, deployment.id
    )

    association = agent_crud.get_agent_model_deployment_association(
        session, agent, model.id, deployment.id
    )

    assert association is None


def test_delete_non_existing_agent_model_deployment_association(session):
    organization = get_factory("Organization", session).create()
    user = get_factory("User", session).create()
    user.organizations.append(organization)
    agent = get_factory("Agent", session).create(user=user, organization=organization)

    agent_crud.delete_agent_model_deployment_association(session, agent, "123", "123")


def test_assign_model_deployment_to_agent(session):
    organization = get_factory("Organization", session).create()
    user = get_factory("User", session).create()
    user.organizations.append(organization)
    agent = get_factory("Agent", session).create(user=user, organization=organization)
    deployment = get_factory("Deployment", session).create()
    model = get_factory("Model", session).create(deployment_id=deployment.id)

    agent_crud.assign_model_deployment_to_agent(session, agent, model.id, deployment.id)

    association = agent_crud.get_agent_model_deployment_association(
        session, agent, model.id, deployment.id
    )

    assert association.agent_id == agent.id
    assert association.deployment_id == deployment.id
    assert association.model_id == model.id
