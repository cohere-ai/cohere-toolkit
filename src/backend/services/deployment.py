"""
This module handles backend operations related to deployments, which define how to interact
with an LLM.

New deployments are created by subclassing BaseDeployment and implementing required
methods in the model_deployments directory.

Deployments can be configured in two ways: via configuration.yaml or environment variables
using the .env file, or dynamically in the database using the deployment_crud module. This
service abstracts these methods, ensuring higher layers remain unaffected by configuration details.

Each deployment is assumed to use either configuration files or the database, with database
configurations taking precedence.
"""

from backend.config.deployments import AVAILABLE_MODEL_DEPLOYMENTS
from backend.config.settings import Settings
from backend.crud import deployment as deployment_crud
from backend.crud import model as model_crud
from backend.database_models.database import DBSessionDep
from backend.exceptions import DeploymentNotFoundError, NoAvailableDeploymentsError
from backend.model_deployments.base import BaseDeployment
from backend.schemas.deployment import DeploymentDefinition, DeploymentUpdate
from backend.services.env import update_env_file
from backend.services.logger.utils import LoggerFactory

logger = LoggerFactory().get_logger()


def create_db_deployment(session: DBSessionDep, deployment: DeploymentDefinition) -> DeploymentDefinition:
    logger.debug(event="create_db_deployment", deployment=deployment.model_dump())

    db_deployment = deployment_crud.create_deployment_by_config(session, deployment)
    model_crud.create_model_by_config(session, deployment, db_deployment.id, None)

    return DeploymentDefinition.from_db_deployment(db_deployment)


def get_default_deployment_instance(**kwargs) -> BaseDeployment:
    try:
        fallback = next(d for d in AVAILABLE_MODEL_DEPLOYMENTS.values() if d.is_available())
    except StopIteration:
        raise NoAvailableDeploymentsError()

    default_deployment = Settings().get("deployments.default_deployment")
    if default_deployment:
        return next(
            (
                d
                for d in AVAILABLE_MODEL_DEPLOYMENTS.values()
                if d.id() == default_deployment
            ),
            fallback,
        )(**kwargs)

    return fallback(**kwargs)

def get_deployment_instance_by_id(session: DBSessionDep, deployment_id: str, **kwargs) -> BaseDeployment:
    definition = get_deployment_definition(session, deployment_id)
    # TODO: What's the point of fetching by ID if we just fetch by name after?
    return get_deployment_instance_by_name(session, definition.name, **kwargs)

def get_deployment_instance_by_name(session: DBSessionDep, deployment_name: str, **kwargs) -> BaseDeployment:
    definition = get_deployment_definition_by_name(session, deployment_name)

    try:
        deployment_class =  next(d for d in AVAILABLE_MODEL_DEPLOYMENTS.values() if d.__name__ == definition.class_name)
        deployment_instance = deployment_class(
            db_id=definition.id, db_config=definition.config, **kwargs
        )

        return deployment_instance
    except StopIteration:
        raise DeploymentNotFoundError(deployment_id=deployment_name)

def get_deployment_definition(session: DBSessionDep, deployment_id: str) -> DeploymentDefinition:
    db_deployment = deployment_crud.get_deployment(session, deployment_id)
    if db_deployment:
        return DeploymentDefinition.from_db_deployment(db_deployment)

    try:
        deployment = next(d for d in AVAILABLE_MODEL_DEPLOYMENTS.values() if d.id() == deployment_id)
        create_db_deployment(session, deployment.to_deployment_definition())
    except StopIteration:
        raise DeploymentNotFoundError(deployment_id=deployment_id)

    return deployment.to_deployment_definition()

def get_deployment_definition_by_name(session: DBSessionDep, deployment_name: str) -> DeploymentDefinition:
    definitions = get_deployment_definitions(session)
    try:
        definition = next(definition for definition in definitions if definition.name == deployment_name)
    except StopIteration:
        raise DeploymentNotFoundError(deployment_id=deployment_name)

    # Creates deployment in DB if it doesn't exist
    if definition.name not in [d.name for d in deployment_crud.get_deployments(session)]:
        definition = create_db_deployment(session, definition)

    return definition

def get_deployment_definitions(session: DBSessionDep) -> list[DeploymentDefinition]:
    db_deployments = {
        db_deployment.name: DeploymentDefinition.from_db_deployment(db_deployment)
        for db_deployment in deployment_crud.get_deployments(session)
    }

    installed_deployments = [
        deployment.to_deployment_definition()
        for deployment in AVAILABLE_MODEL_DEPLOYMENTS.values()
        if deployment.name() not in db_deployments
    ]

    return [*db_deployments.values(), *installed_deployments]

def update_config(session: DBSessionDep, deployment_id: str, env_vars: dict[str, str]) -> DeploymentDefinition:
    logger.debug(event="update_config", deployment_id=deployment_id, env_vars=env_vars)

    db_deployment = deployment_crud.get_deployment(session, deployment_id)
    if db_deployment:
        new_config = dict(db_deployment.default_deployment_config if db_deployment.default_deployment_config else {})
        new_config.update(env_vars)
        update = DeploymentUpdate(default_deployment_config=new_config)
        updated_db_deployment = deployment_crud.update_deployment(session, db_deployment, update)
        updated_deployment = DeploymentDefinition.from_db_deployment(updated_db_deployment)
    else:
        update_env_file(env_vars)
        updated_deployment = get_deployment_definition(session, deployment_id)

    return updated_deployment
