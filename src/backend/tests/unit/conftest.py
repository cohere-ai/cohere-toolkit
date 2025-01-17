import os
from typing import Any, Generator
from unittest.mock import patch

import fakeredis
import pytest
from alembic.command import upgrade
from alembic.config import Config
from fastapi import FastAPI
from fastapi.testclient import TestClient
from redis import Redis
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from backend.database_models import get_session
from backend.database_models.base import CustomFilterQuery
from backend.database_models.deployment import Deployment
from backend.main import app, create_app
from backend.schemas.organization import Organization
from backend.schemas.user import User
from backend.tests.unit.factories import get_factory

DATABASE_URL = os.environ["DATABASE_URL"]
MASTER_DB_NAME = "postgres"
TEST_DB_PREFIX = "postgres_"
MASTER_DATABASE_FULL_URL = f"{DATABASE_URL}/{MASTER_DB_NAME}"


def create_test_database(test_db_name: str):
    engine = create_engine(
        MASTER_DATABASE_FULL_URL, echo=True, isolation_level="AUTOCOMMIT"
    )

    with engine.connect() as connection:
        connection.execute(text(f"CREATE DATABASE {test_db_name}"))
    engine.dispose()


def drop_test_database_if_exists(test_db_name: str):
    engine = create_engine(
        MASTER_DATABASE_FULL_URL, echo=True, isolation_level="AUTOCOMMIT"
    )

    with engine.connect() as connection:
        connection.execute(text(f"DROP DATABASE IF EXISTS {test_db_name}"))
    engine.dispose()


@pytest.fixture(scope="session")
def fastapi_app() -> Generator[FastAPI, None, None]:
    """Creates a session-scoped FastAPI app object."""
    app = create_app()
    yield app


@pytest.fixture
def client():
    yield TestClient(app)


@pytest.fixture(scope="session")
def engine(worker_id: str) -> Generator[Any, None, None]:
    """
    Yields a SQLAlchemy engine which is disposed of after the test session
    """
    test_db_name = f"{TEST_DB_PREFIX}{worker_id.replace('gw', '')}"
    test_db_url = f"{DATABASE_URL}/{test_db_name}"

    drop_test_database_if_exists(test_db_name)
    create_test_database(test_db_name)
    engine = create_engine(test_db_url, echo=True)

    with engine.begin():
        alembic_cfg = Config("src/backend/alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", test_db_url)
        upgrade(alembic_cfg, "head")

    yield engine

    engine.dispose()
    drop_test_database_if_exists(test_db_name)


@pytest.fixture(scope="function")
def session(engine: Any) -> Generator[Session, None, None]:
    """
    Yields a SQLAlchemy session within a transaction
    that is rolled back after every function
    """
    connection = engine.connect()
    # Begin the transaction
    transaction = connection.begin()
    # Use connection within the started transaction
    session = Session(bind=connection, query_cls=CustomFilterQuery)

    yield session

    session.close()
    # Roll back the transaction
    transaction.rollback()
    # Close connection so it returns to the connection pool
    connection.close()


@pytest.fixture(scope="function")
def session_client(session: Session, fastapi_app: FastAPI) -> Generator[TestClient, None, None]:
    """
    Fixture to inject the session into the API client
    """

    def override_get_session() -> Generator[Session, Any, None]:
        yield session

    fastapi_app.dependency_overrides[get_session] = override_get_session

    print("Session at fixture " + str(session))

    with TestClient(fastapi_app) as client:
        yield client

    fastapi_app.dependency_overrides = {}


@pytest.fixture(scope="session")
def session_chat(engine: Any) -> Generator[Session, None, None]:
    """
    Yields a SQLAlchemy session within a transaction
    that is rolled back after every session

    We need to use the fixture in the session scope because the chat
    endpoint is asynchronous and needs to be open for the entire session
    """
    connection = engine.connect()
    transaction = connection.begin()
    # Use connection within the started transaction
    session = Session(bind=connection, query_cls=CustomFilterQuery)

    yield session

    session.close()
    # Roll back the transaction
    transaction.rollback()
    # Close connection so it returns to the connection pool
    connection.close()


@pytest.fixture(scope="session")
def session_client_chat(session_chat: Session, fastapi_app: FastAPI) -> Generator[TestClient, None, None]:
    """
    Fixture to inject the session into the API client

    We need to use the fixture in the session scope because the chat
    router uses a WebSocket connection that needs to be open for the
    entire session
    """

    def override_get_session() -> Generator[Session, Any, None]:
        yield session_chat

    fastapi_app.dependency_overrides[get_session] = override_get_session

    print("Session at fixture " + str(session_chat))

    with TestClient(fastapi_app) as client:
        yield client

    fastapi_app.dependency_overrides = {}


@pytest.fixture(autouse=True)
def mock_redis_client():
    """
    A pytest fixture that globally replaces `Redis.from_url` with `fakeredis`.
    """
    fake_redis = fakeredis.FakeStrictRedis(decode_responses=True)

    # Patch Redis.from_url to always return the fake Redis instance
    with patch.object(Redis, 'from_url', return_value=fake_redis):
        yield fake_redis


@pytest.fixture
def user(session: Session) -> User:
    return get_factory("User", session).create(id="1")


@pytest.fixture
def organization(session: Session) -> Organization:
    return get_factory("Organization", session).create()

@pytest.fixture
def deployment(session: Session) -> Deployment:
    return get_factory("Deployment", session).create(
        deployment_class_name="CohereDeployment"
    )

@pytest.fixture
def mock_available_model_deployments(request):
    from backend.tests.unit.model_deployments.mock_deployments import (
        MockAzureDeployment,
        MockBedrockDeployment,
        MockCohereDeployment,
        MockSageMakerDeployment,
        MockSingleContainerDeployment,
    )

    MOCKED_DEPLOYMENTS = {
        MockCohereDeployment.name(): MockCohereDeployment,
        MockAzureDeployment.name(): MockAzureDeployment,
        MockSageMakerDeployment.name(): MockSageMakerDeployment,
        MockBedrockDeployment.name(): MockBedrockDeployment,
        MockSingleContainerDeployment.name(): MockSingleContainerDeployment,
    }

    with patch("backend.services.deployment.AVAILABLE_MODEL_DEPLOYMENTS", MOCKED_DEPLOYMENTS) as mock:
        yield mock
