import os
from typing import Any, Generator
from unittest.mock import patch

import pytest
from alembic.command import upgrade
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.config.deployments import AVAILABLE_MODEL_DEPLOYMENTS, ModelDeploymentName
from backend.database_models import get_session
from backend.database_models.agent import Agent
from backend.database_models.deployment import Deployment
from backend.database_models.model import Model
from backend.main import app, create_app
from backend.schemas.deployment import Deployment as DeploymentSchema
from backend.schemas.organization import Organization
from backend.schemas.user import User
from backend.tests.factories import get_factory

DATABASE_URL = os.environ["DATABASE_URL"]


@pytest.fixture
def client():
    yield TestClient(app)


@pytest.fixture(scope="function")
def engine() -> Generator[Any, None, None]:
    """
    Yields a SQLAlchemy engine which is disposed of after the test session
    """
    engine = create_engine(DATABASE_URL, echo=True)

    yield engine

    engine.dispose()


@pytest.fixture(scope="function")
def session(engine: Any) -> Generator[Session, None, None]:
    """
    Yields a SQLAlchemy session within a transaction
    that is rolled back after every function
    """
    connection = engine.connect()
    # Begin the nested transaction
    transaction = connection.begin()
    # Use connection within the started transaction
    session = Session(bind=connection)
    # Run Alembic migrations
    alembic_cfg = Config("src/backend/alembic.ini")
    upgrade(alembic_cfg, "head")

    yield session

    session.close()
    # Roll back the transaction
    transaction.rollback()
    # Close connection so it returns to the connection pool
    connection.close()


@pytest.fixture(scope="function")
def session_client(session: Session) -> Generator[TestClient, None, None]:
    """
    Fixture to inject the session into the API client
    """

    def override_get_session() -> Generator[Session, Any, None]:
        yield session

    app = create_app()

    app.dependency_overrides[get_session] = override_get_session

    print("Session at fixture " + str(session))

    with TestClient(app) as client:
        yield client

    app.dependency_overrides = {}


@pytest.fixture(scope="session")
def engine_chat() -> Generator[Any, None, None]:
    """
    Yields a SQLAlchemy engine which is disposed of after the test session
    """
    engine = create_engine(DATABASE_URL, echo=True)

    yield engine

    engine.dispose()


@pytest.fixture(scope="session")
def session_chat(engine_chat: Any) -> Generator[Session, None, None]:
    """
    Yields a SQLAlchemy session within a transaction
    that is rolled back after every session

    We need to use the fixture in the session scope because the chat
    endpoint is asynchronous and needs to be open for the entire session
    """
    connection = engine_chat.connect()
    # Begin the nested transaction
    transaction = connection.begin()
    # Use connection within the started transaction
    session = Session(bind=connection)
    # Run Alembic migrations
    alembic_cfg = Config("src/backend/alembic.ini")
    upgrade(alembic_cfg, "head")

    yield session

    session.close()
    # Roll back the transaction
    transaction.rollback()
    # Close connection so it returns to the connection pool
    connection.close()


@pytest.fixture(scope="session")
def session_client_chat(session_chat: Session) -> Generator[TestClient, None, None]:
    """
    Fixture to inject the session into the API client

    We need to use the fixture in the session scope because the chat
    router uses a WebSocket connection that needs to be open for the
    entire session
    """

    def override_get_session() -> Generator[Session, Any, None]:
        yield session_chat

    app = create_app()
    app.dependency_overrides[get_session] = override_get_session

    print("Session at fixture " + str(session_chat))

    with TestClient(app) as client:
        yield client

    app.dependency_overrides = {}


@pytest.fixture
def user(session: Session) -> User:
    return get_factory("User", session).create()


@pytest.fixture
def organization(session: Session) -> Organization:
    return get_factory("Organization", session).create()


@pytest.fixture
def deployment(session: Session) -> Deployment:
    return get_factory("Deployment", session).create(
        deployment_class_name="CohereDeployment"
    )


@pytest.fixture
def model(session: Session) -> Model:
    return get_factory("Model", session).create()


@pytest.fixture
def agent(session: Session) -> Agent:
    return get_factory("Agent", session).create()


@pytest.fixture
def mock_available_model_deployments(request):
    from backend.tests.model_deployments.mock_deployments import (
        MockAzureDeployment,
        MockBedrockDeployment,
        MockCohereDeployment,
        MockSageMakerDeployment,
    )

    is_available_values = getattr(request, "param", {})
    MOCKED_DEPLOYMENTS = {
        ModelDeploymentName.CoherePlatform: DeploymentSchema(
            id="cohere_platform",
            name=ModelDeploymentName.CoherePlatform,
            models=MockCohereDeployment.list_models(),
            is_available=is_available_values.get(
                ModelDeploymentName.CoherePlatform, True
            ),
            deployment_class=MockCohereDeployment,
            env_vars=["COHERE_VAR_1", "COHERE_VAR_2"],
        ),
        ModelDeploymentName.SageMaker: DeploymentSchema(
            id="sagemaker",
            name=ModelDeploymentName.SageMaker,
            models=MockSageMakerDeployment.list_models(),
            is_available=is_available_values.get(ModelDeploymentName.SageMaker, True),
            deployment_class=MockSageMakerDeployment,
            env_vars=["SAGEMAKER_VAR_1", "SAGEMAKER_VAR_2"],
        ),
        ModelDeploymentName.Azure: DeploymentSchema(
            id="azure",
            name=ModelDeploymentName.Azure,
            models=MockAzureDeployment.list_models(),
            is_available=is_available_values.get(ModelDeploymentName.Azure, True),
            deployment_class=MockAzureDeployment,
            env_vars=["SAGEMAKER_VAR_1", "SAGEMAKER_VAR_2"],
        ),
        ModelDeploymentName.Bedrock: DeploymentSchema(
            id="bedrock",
            name=ModelDeploymentName.Bedrock,
            models=MockBedrockDeployment.list_models(),
            is_available=is_available_values.get(ModelDeploymentName.Bedrock, True),
            deployment_class=MockBedrockDeployment,
            env_vars=["BEDROCK_VAR_1", "BEDROCK_VAR_2"],
        ),
    }

    with patch.dict(AVAILABLE_MODEL_DEPLOYMENTS, MOCKED_DEPLOYMENTS) as mock:
        yield mock
