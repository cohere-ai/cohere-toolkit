import os

import pytest

from backend.config.deployments import ModelDeploymentName
from backend.config.tools import ToolName
from backend.crud import agent as agent_crud
from backend.database_models.agent import Agent
from backend.tools import GoogleDrive


def calculate_recall_at_k(results, ground_truths, k=5):
    """
    Calculate recall@k for retrieved docs given the ground truth
    """
    if len(results) == 0:
        return 0
    if k > len(results):
        k = len(results)
    num_relevant = 0
    for i in range(k):
        for ground_truth in ground_truths:
            if ground_truth in results[i]:
                num_relevant += 1
                break
    return num_relevant / len(ground_truths)


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
    """
    Create a test agent with Google Drive tool
    """
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


async def query_gdrive(agent, sa_info, session, query):
    """
    Query the Google Drive tool
    """
    gdrive = GoogleDrive()
    result = await gdrive.call(
        {"query": query},
        **{
            "agent_id": agent.id,
            "service_account_info": sa_info,
            "session": session,
        },
    )
    return result


@pytest.mark.asyncio
async def test_gdrive(session, user) -> None:
    """
    Evaluate the retrieval performance of the Google Drive tool + Compass
    """
    agent = create_test_gdrive_agent(session, user)
    sa_info = construct_service_account_info()

    # List of queries and their corresponding expected text snippets in the retrieved documents
    queries = [
        "In Amazon's Q2 2023 10-Q, how does the discussion on employee compensation and benefits in the human resources section relate to the reported financial expenses",
        "For Microsoft's Q2 2023 report, assess the connection between Microsoft's earnings from international markets and the discussion on currency risk in the financial section.",
        "For NVIDIA's Q1 2023 10-Q, what is the relationship between R&D spending and the development of new GPU technologies or services?",
    ]
    golden_texts = [
        [
            "The decrease in AWS operating income in absolute dollars in Q2 2023 and for the six months ended June 30, 2023, compared to the comparable prior year #periods, is primarily due to increased payroll and related expenses and spending on technology infrastructure"
        ],
        [
            "Foreign currency risks related to certain non-U.S. dollar-denominated investments are hedged using foreign exchange forward contracts that are designated as fair value hedging instruments. Foreign currency risks related to certain Euro-denominated debt are hedged using foreign exchange forward contracts that are designated as cash flow hedging instruments."
        ],
        [
            "We have invested in research and development in markets where we have a limited operating history, which may not produce meaningful revenue for several years, if at all"
        ],
    ]
    # Run the queries and print the results
    for query, golden_texts in zip(queries, golden_texts):
        result = await query_gdrive(agent, sa_info, session, query)
        results = [res["text"] for res in result]
        sources = [res["title"] for res in result]
        print(f"Query: {query}")
        print("\n--\n".join(sources))
        print("\n--\n".join(results))

        # calculate recall@k
        for k in [5]:
            recall = calculate_recall_at_k(results, golden_texts, k)
            print(f"Recall@{k}: {recall}")

            assert recall > 0.0
