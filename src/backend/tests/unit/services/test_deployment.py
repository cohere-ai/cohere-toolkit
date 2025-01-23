from unittest.mock import patch

import pytest

import backend.services.deployment as deployment_service
from backend.config.tools import Tool
from backend.database_models import Deployment
from backend.exceptions import DeploymentNotFoundError, NoAvailableDeploymentsError
from backend.schemas.deployment import DeploymentDefinition
from backend.tests.unit.model_deployments.mock_deployments import (
    MockAzureDeployment,
    MockBedrockDeployment,
    MockCohereDeployment,
    MockSageMakerDeployment,
    MockSingleContainerDeployment,
)


@pytest.fixture
def clear_db_deployments(session):
    session.query(Deployment).delete()
    session.commit()

@pytest.fixture
def db_deployment(session):
    session.query(Deployment).delete()
    mock_cohere_deployment = Deployment(
        name=MockCohereDeployment.name(),
        description="A mock Cohere deployment from the DB",
        deployment_class_name=MockCohereDeployment.__name__,
        is_community=False,
        default_deployment_config={"COHERE_API_KEY": "db-test-api-key"},
        id="db-mock-cohere-platform-id",
    )
    session.add(mock_cohere_deployment)
    session.commit()
    return mock_cohere_deployment

def test_all_tools_have_id() -> None:
    for tool in Tool:
        assert tool.value.ID is not None

def test_get_default_deployment_none_available() -> None:
    with patch("backend.services.deployment.AVAILABLE_MODEL_DEPLOYMENTS", {}):
        with pytest.raises(NoAvailableDeploymentsError):
            deployment_service.get_default_deployment_instance()

def test_get_default_deployment_no_settings(mock_available_model_deployments) -> None:
    assert isinstance(deployment_service.get_default_deployment_instance(), MockCohereDeployment)

def test_get_default_deployment_with_settings(mock_available_model_deployments) -> None:
    with patch("backend.config.settings.Settings.get", return_value="azure") as mock_settings:
        assert isinstance(deployment_service.get_default_deployment_instance(), MockAzureDeployment)
        mock_settings.assert_called_once_with("deployments.default_deployment")

def test_get_deployment(session, mock_available_model_deployments, db_deployment) -> None:
    deployment = deployment_service.get_deployment_instance_by_id(session, db_deployment.id)
    assert isinstance(deployment, MockCohereDeployment)

def test_get_deployment_by_name(session, mock_available_model_deployments, clear_db_deployments) -> None:
    deployment = deployment_service.get_deployment_instance_by_name(session, MockCohereDeployment.name())
    assert isinstance(deployment, MockCohereDeployment)

def test_get_deployment_by_name_wrong_name(session, mock_available_model_deployments) -> None:
    with pytest.raises(DeploymentNotFoundError):
        deployment_service.get_deployment_instance_by_name(session, "wrong-name")

def test_get_deployment_definition(session, mock_available_model_deployments, db_deployment) -> None:
    definition = deployment_service.get_deployment_definition(session, "db-mock-cohere-platform-id")
    assert definition == DeploymentDefinition.from_db_deployment(db_deployment)

def test_get_deployment_definition_wrong_id(session, mock_available_model_deployments) -> None:
    with pytest.raises(DeploymentNotFoundError):
        deployment_service.get_deployment_definition(session, "wrong-id")

def test_get_deployment_definition_no_db_deployments(session, mock_available_model_deployments, clear_db_deployments) -> None:
    definition = deployment_service.get_deployment_definition(session, MockCohereDeployment.id())
    assert definition == MockCohereDeployment.to_deployment_definition()

def test_get_deployment_definition_by_name(session, mock_available_model_deployments, db_deployment) -> None:
    definition = deployment_service.get_deployment_definition_by_name(session, db_deployment.name)
    assert definition == DeploymentDefinition.from_db_deployment(db_deployment)

def test_get_deployment_definition_by_name_no_db_deployments(session, mock_available_model_deployments, clear_db_deployments) -> None:
    definition = deployment_service.get_deployment_definition_by_name(session, MockCohereDeployment.name())
    mock = MockCohereDeployment.to_deployment_definition()
    assert definition.name == mock.name
    assert definition.models == mock.models
    assert definition.class_name == mock.class_name
    assert definition.config == mock.config


def test_get_deployment_definition_by_name_wrong_name(session, mock_available_model_deployments) -> None:
    with pytest.raises(DeploymentNotFoundError):
        deployment_service.get_deployment_definition_by_name(session, "wrong-name")

def test_get_deployment_definitions_no_db_deployments(session, mock_available_model_deployments, clear_db_deployments) -> None:
    definitions = deployment_service.get_deployment_definitions(session)

    assert len(definitions) == 5
    assert all(isinstance(d, DeploymentDefinition) for d in definitions)
    assert all(d.name in [MockAzureDeployment.name(), MockCohereDeployment.name(), MockSageMakerDeployment.name(), MockBedrockDeployment.name(), MockSingleContainerDeployment.name()] for d in definitions)

def test_get_deployment_definitions_with_db_deployments(session, mock_available_model_deployments, db_deployment) -> None:
    mock_cohere_deployment = Deployment(
        name=MockCohereDeployment.name(),
        description="A mock Cohere deployment from the DB",
        deployment_class_name=MockCohereDeployment.__name__,
        is_community=False,
        default_deployment_config={"COHERE_API_KEY": "db-test-api-key"},
        id="db-mock-cohere-platform-id",
    )
    with patch("backend.crud.deployment.get_deployments", return_value=[mock_cohere_deployment]):
        with patch(
            "backend.services.deployment.AVAILABLE_MODEL_DEPLOYMENTS",
            { MockCohereDeployment.name(): MockCohereDeployment, MockAzureDeployment.name(): MockAzureDeployment }
        ):
            definitions = deployment_service.get_deployment_definitions(session)

    assert len(definitions) == 2
    assert all(isinstance(d, DeploymentDefinition) for d in definitions)
    assert all(d.name in [MockAzureDeployment.name(), MockCohereDeployment.name()] for d in definitions)
    assert any(d.id == "db-mock-cohere-platform-id" for d in definitions)

def test_update_config_db(session, db_deployment) -> None:
    deployment_service.update_config(session, db_deployment.id, {"COHERE_API_KEY": "new-db-test-api-key"})
    updated_deployment = session.query(Deployment).get("db-mock-cohere-platform-id")
    assert updated_deployment.default_deployment_config == {"COHERE_API_KEY": "new-db-test-api-key"}

def test_update_config_no_db_deployments(session, mock_available_model_deployments, clear_db_deployments) -> None:
    with patch("backend.services.deployment.update_env_file") as mock_update_env_file:
        with patch("backend.services.deployment.get_deployment_definition", return_value=MockCohereDeployment.to_deployment_definition()):
            deployment_service.update_config(session, "some-deployment-id", {"API_KEY": "new-api-key"})
            mock_update_env_file.assert_called_with({"API_KEY": "new-api-key"})
