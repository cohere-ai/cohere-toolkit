from backend.crud.agent import get_agents
from backend.database_models.database import get_session
from backend.schemas.agent import Agent
from backend.services.sync.jobs.sync_agent_activity import sync_agent_activity

# NOTE Variable to limit the number of agents you are syncing at once
# Helpful for first time setups
LIMIT = None
# LIMIT = 1


def main():
    session = next(get_session())
    agents = [Agent.model_validate(x) for x in get_agents(session)]
    if LIMIT:
        agents = agents[:LIMIT]
    session.close()

    for agent in agents:
        sync_agent_activity(agent_id=agent.id)


if __name__ == "__main__":
    main()
