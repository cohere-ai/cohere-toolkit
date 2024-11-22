"""Functions for handling operations with deployments.

This module contains functions for handling backend operations with deployments. A Deployment
represents the information required to interact with an LLM. New deployments are defined
by creating a class that inherits from BaseDeployment and implementing the required methods in
the model_deployments directory.

Deployments can be configured in two different ways: by providing appropriate config values
through the config (which itself should be set in a configuration.yaml file, or through setting
environment variables), or by dynamically defining a deployment in the database through the
deployment_crud module. This service attempts to abstract the differences between these two
styles so that higher layers don't need to know about these differences.

We assume that for each kind of deployment, it will be configured either through the config or
through the database, but not both. If a deployment is configured in the database, it is assumed
to the be the correct definition.
"""

from backend.config.deployments import AVAILABLE_MODEL_DEPLOYMENTS
from backend.config.settings import Settings
from backend.crud import deployment as deployment_crud
from backend.database_models.database import DBSessionDep
from backend.exceptions import DeploymentNotFoundError, NoAvailableDeploymentsError
from backend.model_deployments.base import BaseDeployment
from backend.schemas.deployment import DeploymentDefinition, DeploymentUpdate
from backend.services.env import update_env_file
from backend.services.logger.utils import LoggerFactory

logger = LoggerFactory().get_logger()


def get_default_deployment() -> type[BaseDeployment]:
    try:
        fallback = next(d for d in AVAILABLE_MODEL_DEPLOYMENTS if d.is_available)
    except StopIteration:
        raise NoAvailableDeploymentsError()

    default_deployment = Settings().get("deployments.default_deployment")
    if default_deployment:
        return next(
            (
                d
                for d in AVAILABLE_MODEL_DEPLOYMENTS
                if d.id() == default_deployment
            ),
            fallback,
        )

    return fallback

def get_deployment(session: DBSessionDep, deployment_id: str) -> type[BaseDeployment]:
    definition = get_deployment_definition(session, deployment_id)
    return get_deployment_by_name(definition.name)

def get_deployment_by_name(deployment_name: str) -> type[BaseDeployment]:
    try:
        return next(d for d in AVAILABLE_MODEL_DEPLOYMENTS if d.name() == deployment_name)
    except StopIteration:
        raise DeploymentNotFoundError(deployment_id=deployment_name)

def get_deployment_definition(session: DBSessionDep, deployment_id: str) -> DeploymentDefinition:
    db_deployment = deployment_crud.get_deployment(session, deployment_id)
    if db_deployment:
        return DeploymentDefinition.from_db_deployment(db_deployment)

    try:
        deployment = next(d for d in AVAILABLE_MODEL_DEPLOYMENTS if d.id() == deployment_id)
    except StopIteration:
        raise DeploymentNotFoundError(deployment_id=deployment_id)

    return deployment.to_deployment_definition()

def get_deployment_definition_by_name(session: DBSessionDep, deployment_name: str) -> DeploymentDefinition:
    definitions = get_deployment_definitions(session)
    try:
        return next(definition for definition in definitions if definition.name == deployment_name)
    except StopIteration:
        raise DeploymentNotFoundError(deployment_id=deployment_name)

def get_deployment_definitions(session: DBSessionDep) -> list[DeploymentDefinition]:
    db_deployments = {
        db_deployment.name: DeploymentDefinition.from_db_deployment(db_deployment)
        for db_deployment in deployment_crud.get_deployments(session)
    }

    installed_deployments = [
        deployment.to_deployment_definition()
        for deployment in AVAILABLE_MODEL_DEPLOYMENTS
        if deployment.name() not in db_deployments
    ]

    return [*db_deployments.values(), *installed_deployments]

def update_config(session: DBSessionDep, deployment_id: str, env_vars: dict[str, str]) -> DeploymentDefinition:
    db_deployment = deployment_crud.get_deployment(session, deployment_id)
    if db_deployment:
        update = DeploymentUpdate(default_deployment_config=env_vars)
        updated_db_deployment = deployment_crud.update_deployment(session, db_deployment, update)
        updated_deployment = DeploymentDefinition.from_db_deployment(updated_db_deployment)
    else:
        update_env_file(env_vars)
        updated_deployment = get_deployment_definition(session, deployment_id)

    return updated_deployment
