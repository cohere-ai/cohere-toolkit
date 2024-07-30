from backend.crud.agent import get_agents
from backend.database_models.database import get_session
from backend.services.sync.agent import sync_agent

# NOTE Variable to limit the number of agents you are syncing at once
# Helpful for first time setups
# LIMIT = None
LIMIT = 1


def main():
    session = next(get_session())
    agents = get_agents(session)
    if LIMIT:
        agents = agents[:LIMIT]
    session.close()

    for agent in agents:
        sync_agent(agent_id=agent.id)


if __name__ == "__main__":
    main()
