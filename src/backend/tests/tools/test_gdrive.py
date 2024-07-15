import os

import pytest

from backend.config.deployments import ModelDeploymentName
from backend.config.tools import ToolName
from backend.crud import agent as agent_crud
from backend.database_models.agent import Agent
from backend.tools import GoogleDrive


@pytest.mark.asyncio
async def test_gdrive(session, user) -> None:
    agent = create_test_gdrive_agent(session, user)
    sa_info = construct_service_account_info()

    gdrive = GoogleDrive()
    result = await gdrive.call(
        {"query": "toolkit"},
        **{
            "agent_id": agent.id,
            "service_account_info": sa_info,
            "session": session,
        }
    )
    print(result)


def construct_service_account_info():
    static_properties = {
        "type": "service_account",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "universe_domain": "googleapis.com",
    }
    # Pre-validated env vars
    final_results = {
        **static_properties,
        "project_id": os.getenv("GCP_PROJECT_ID"),
        "private_key_id": os.getenv("GCP_PRIVATE_KEY_ID"),
        "private_key": os.getenv("GCP_PRIVATE_KEY"),
        "client_id": os.getenv("GCP_CLIENT_ID"),
        "client_email": os.getenv("GCP_CLIENT_EMAIL"),
        "client_x509_cert_url": os.getenv("GCP_CLIENT_CERT_URL"),
    }
    return final_results


def create_test_gdrive_agent(session, user):
    agent_data = Agent(
        user_id=user.id,
        version=1,
        name="test",
        description="test",
        preamble="test",
        temperature=0.5,
        tools=[ToolName.Google_Drive],
        model="command-r-plus",
        deployment=ModelDeploymentName.CoherePlatform,
    )
    agent = agent_crud.create_agent(session, agent_data)
    return agent
