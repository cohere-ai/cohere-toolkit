from backend.database_models.database import DBSessionDep
from backend.model_deployments.cohere_platform import CohereDeployment
from backend.schemas.agent import Agent


def get_deployment_model_from_agent(agent: Agent, session: DBSessionDep):
    from backend.crud import deployment as deployment_crud

    model_db = None
    deployment_db = None
    if agent.deployment:
        deployment_db = deployment_crud.get_deployment_by_name(session, agent.deployment)
        if not deployment_db:
            deployment_db = deployment_crud.get_deployment(session, agent.deployment)
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
