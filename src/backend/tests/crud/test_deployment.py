import pytest
from pydantic import ValidationError

from backend.crud import deployment as deployment_crud
from backend.database_models import AgentDeploymentModel, Model
from backend.database_models.deployment import Deployment
from backend.schemas.deployment import DeploymentCreate, DeploymentUpdate
from backend.tests.factories import get_factory


def test_create_deployment(session, deployment):
    deployment_data = DeploymentCreate(
        name="Test Deployment",
        deployment_class_name="CohereDeployment",
        description="Test Description",
        is_community=False,
        default_deployment_config={},
    )

    deployment = deployment_crud.create_deployment(session, deployment_data)
    assert deployment.name == deployment_data.name
    assert deployment.deployment_class_name == deployment_data.deployment_class_name
    assert deployment.description == deployment_data.description
    assert deployment.is_community == deployment_data.is_community
    assert (
        deployment.default_deployment_config
        == deployment_data.default_deployment_config
    )

    deployment = deployment_crud.get_deployment(session, deployment.id)
    assert deployment.name == deployment_data.name


def test_create_deployment_invalid_class_name(session):
    with pytest.raises(ValueError) as e:
        deployment_data = DeploymentCreate(
            name="Test Deployment",
            deployment_class_name="SomeClassName",
            description="Test Description",
            is_community=False,
            default_deployment_config={},
        )
        deployment_crud.create_deployment(session, deployment_data)

    assert "Deployment class not found" in str(e.value)


def test_get_deployment(session):
    deployment = get_factory("Deployment", session).create(name="Test Deployment")
    retrieved_deployment = deployment_crud.get_deployment(session, deployment.id)
    assert retrieved_deployment.id == deployment.id
    assert retrieved_deployment.name == deployment.name


def test_fail_get_nonexistent_deployment(session):
    deployment = deployment_crud.get_deployment(session, "123")
    assert deployment is None


def test_list_deployments(session):
    # Delete default deployments
    session.query(Deployment).delete()
    _ = get_factory("Deployment", session).create(name="Test Deployment")

    deployments = deployment_crud.get_deployments(session)
    assert len(deployments) == 1
    assert deployments[0].name == "Test Deployment"


def test_list_deployments_empty(session):
    # Delete default deployments
    session.query(Deployment).delete()
    deployments = deployment_crud.get_deployments(session)
    assert len(deployments) == 0


def test_list_deployments_with_pagination(session):
    # Delete default deployments
    session.query(Deployment).delete()
    for i in range(10):
        _ = get_factory("Deployment", session).create(name=f"Test Deployment {i}")

    deployments = deployment_crud.get_deployments(session, offset=5, limit=5)
    assert len(deployments) == 5


def test_get_available_deployments(session, user):
    session.query(Deployment).delete()
    deployment = get_factory("Deployment", session).create()
    another_deployment = get_factory("Deployment", session).create(
        default_deployment_config={}
    )
    agent = get_factory("Agent", session).create(user=user)
    model = get_factory("Model", session).create(deployment=deployment)
    another_model = get_factory("Model", session).create(deployment=another_deployment)
    agent_deployment_model = get_factory("AgentDeploymentModel", session).create(
        agent=agent, deployment=deployment, model=model
    )
    agent_deployment_model_empty_config = get_factory(
        "AgentDeploymentModel", session
    ).create(
        agent=agent,
        deployment=another_deployment,
        model=another_model,
        deployment_config={},
    )

    deployments = deployment_crud.get_available_deployments(session)

    assert len(deployments) == 1
    assert deployments[0].id == deployment.id


def test_get_available_deployments_empty(session, user):
    session.query(Deployment).delete()
    deployments = deployment_crud.get_available_deployments(session)

    assert len(deployments) == 0


def test_get_available_deployments_by_agent_id(session, user):
    session.query(Deployment).delete()
    deployment = get_factory("Deployment", session).create()
    another_deployment = get_factory("Deployment", session).create(
        default_deployment_config={}
    )
    agent = get_factory("Agent", session).create(user=user)
    model = get_factory("Model", session).create(deployment_id=deployment.id)
    another_model = get_factory("Model", session).create(
        deployment_id=another_deployment.id
    )
    agent_deployment_model = get_factory("AgentDeploymentModel", session).create(
        agent=agent, deployment=deployment, model=model
    )
    agent_deployment_model_empty_config = get_factory(
        "AgentDeploymentModel", session
    ).create(
        agent=agent, deployment=deployment, model=another_model, deployment_config={}
    )

    deployments = deployment_crud.get_available_deployments_by_agent_id(
        session, agent.id
    )

    assert len(deployments) == 1
    assert deployments[0].id == deployment.id


def test_get_deployments_by_agent_id(session, user):
    session.query(Deployment).delete()
    deployment = get_factory("Deployment", session).create()
    agent = get_factory("Agent", session).create(user=user)
    model = get_factory("Model", session).create(deployment_id=deployment.id)
    agent_deployment_model = get_factory("AgentDeploymentModel", session).create(
        agent=agent, deployment=deployment, model=model
    )

    deployments = deployment_crud.get_deployments_by_agent_id(session, agent.id)

    assert len(deployments) == 1
    assert deployments[0].id == deployment.id


def test_update_deployment(session, deployment):
    new_deployment_data = DeploymentUpdate(
        name="NewName",
        description="New Description",
        deployment_class_name="AzureDeployment",
    )

    updated_deployment = deployment_crud.update_deployment(
        session, deployment, new_deployment_data
    )

    assert updated_deployment.name == new_deployment_data.name
    assert updated_deployment.description == new_deployment_data.description
    assert (
        updated_deployment.deployment_class_name
        == new_deployment_data.deployment_class_name
    )
    assert updated_deployment.id == deployment.id


def test_update_deployment_partial(session, deployment):

    new_deployment_data = DeploymentUpdate(name="Cohere")

    updated_deployment = deployment_crud.update_deployment(
        session, deployment, new_deployment_data
    )

    assert updated_deployment.name == new_deployment_data.name
    assert updated_deployment.id == deployment.id


def test_do_not_update_deployment(session, deployment):
    new_deployment_data = DeploymentUpdate(name="Test Deployment")

    updated_deployment = deployment_crud.update_deployment(
        session, deployment, new_deployment_data
    )
    assert updated_deployment.name == deployment.name


def test_delete_deployment(session):
    deployment = get_factory("Deployment", session).create()

    deployment_crud.delete_deployment(session, deployment.id)

    deployment = deployment_crud.get_deployment(session, deployment.id)
    assert deployment is None


def test_delete_nonexistent_deployment(session):
    deployment_crud.delete_deployment(session, "123")  # no error
    deployment = deployment_crud.get_deployment(session, "123")
    assert deployment is None
