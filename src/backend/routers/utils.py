import backend.services.deployment as deployment_service
from backend.database_models.database import DBSessionDep
from backend.exceptions import DeploymentNotFoundError
from backend.model_deployments.cohere_platform import CohereDeployment
from backend.schemas.agent import Agent
from backend.services.logger.utils import LoggerFactory


def get_deployment_for_agent(session: DBSessionDep, deployment, model) -> tuple[CohereDeployment, str | None]:
    try:
        deployment = deployment_service.get_deployment_instance_by_name(session, deployment)
    except DeploymentNotFoundError:
        deployment = deployment_service.get_default_deployment_instance()

    model = next((m for m in deployment.models() if m.name == model), None)

    return deployment, model

def get_deployment_model_from_agent(agent: Agent, session: DBSessionDep):
    from backend.crud import deployment as deployment_crud
    logger = LoggerFactory().get_logger()
    logger.debug(event="get_deployment_model_from_agent", agent=agent.model_dump())

    model_db = None
    deployment_db = None
    if agent.deployment:
        deployment_db = deployment_crud.get_deployment_by_name(session, agent.deployment)
        if not deployment_db:
            deployment_db = deployment_crud.get_deployment(session, agent.deployment)
        logger.debug(event="deployment models:", deployment_id=deployment_db.id, models=list(d.name for d in deployment_db.models))
        if deployment_db:
            model_db = next(
                (
                    model
                    for model in deployment_db.models
                    if model.name == agent.model or model.id == agent.model
                ),
                None,
            )
    return deployment_db, model_db


def get_default_deployment_model(session: DBSessionDep):
    from backend.crud import deployment as deployment_crud

    deployment_db = deployment_crud.get_deployment_by_name(session, CohereDeployment.name())
    model_db = None
    if deployment_db:
        model_db = next(
            (
                model
                for model in deployment_db.models
                if model.name == 'command-r-plus'
            ),
            None,
        )
    return deployment_db, model_db
