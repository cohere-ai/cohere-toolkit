from backend.database_models.database import DBSessionDep
from backend.schemas.agent import Agent


def get_deployment_model_from_agent(agent: Agent, session: DBSessionDep):
    from backend.crud import deployment as deployment_crud

    model_db = None
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
