import pytest
from sqlalchemy.orm import Session

from backend.crud import deployment as deployment_crud
from backend.database_models.deployment import Deployment
from backend.schemas.deployment import DeploymentCreate, DeploymentUpdate
from backend.schemas.user import User
from backend.tests.unit.factories import get_factory


def test_create_deployment(session: Session, deployment: Deployment) -> None:
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


def test_create_deployment_invalid_class_name(session: Session) -> None:
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


def test_get_deployment(session: Session) -> None:
    deployment = get_factory("Deployment", session).create(name="Test Deployment")
    retrieved_deployment = deployment_crud.get_deployment(session, deployment.id)
    assert retrieved_deployment.id == deployment.id
    assert retrieved_deployment.name == deployment.name


def test_fail_get_nonexistent_deployment(session: Session) -> None:
    deployment = deployment_crud.get_deployment(session, "123")
    assert deployment is None


def test_list_deployments(session: Session) -> None:
    # Delete default deployments
    session.query(Deployment).delete()
    _ = get_factory("Deployment", session).create(name="Test Deployment")

    deployments = deployment_crud.get_deployments(session)
    assert len(deployments) == 1
    assert deployments[0].name == "Test Deployment"


def test_list_deployments_empty(session: Session) -> None:
    # Delete default deployments
    session.query(Deployment).delete()
    deployments = deployment_crud.get_deployments(session)
    assert len(deployments) == 0


def test_list_deployments_with_pagination(session: Session) -> None:
    # Delete default deployments
    session.query(Deployment).delete()
    for i in range(10):
        _ = get_factory("Deployment", session).create(name=f"Test Deployment {i}")

    deployments = deployment_crud.get_deployments(session, offset=5, limit=5)
    assert len(deployments) == 5


def test_get_available_deployments(session: Session, user: User) -> None:
    session.query(Deployment).delete()
    deployment = get_factory("Deployment", session).create()
    _ = get_factory("Deployment", session).create(
        default_deployment_config={}
    )

    deployments = deployment_crud.get_available_deployments(session)

    assert len(deployments) == 1
    assert deployments[0].id == deployment.id


def test_get_available_deployments_empty(session: Session, user: User) -> None:
    session.query(Deployment).delete()
    deployments = deployment_crud.get_available_deployments(session)

    assert len(deployments) == 0


def test_update_deployment(session: Session, deployment: Deployment) -> None:
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


def test_update_deployment_partial(session: Session, deployment: Deployment) -> None:
    new_deployment_data = DeploymentUpdate(name="Cohere")

    updated_deployment = deployment_crud.update_deployment(
        session, deployment, new_deployment_data
    )

    assert updated_deployment.name == new_deployment_data.name
    assert updated_deployment.id == deployment.id


def test_do_not_update_deployment(session: Session, deployment: Deployment) -> None:
    new_deployment_data = DeploymentUpdate(name="Test Deployment")

    updated_deployment = deployment_crud.update_deployment(
        session, deployment, new_deployment_data
    )
    assert updated_deployment.name == deployment.name


def test_delete_deployment(session: Session) -> None:
    deployment = get_factory("Deployment", session).create()

    deployment_crud.delete_deployment(session, deployment.id)

    deployment = deployment_crud.get_deployment(session, deployment.id)
    assert deployment is None


def test_delete_nonexistent_deployment(session: Session) -> None:
    deployment_crud.delete_deployment(session, "123")  # no error
    deployment = deployment_crud.get_deployment(session, "123")
    assert deployment is None
