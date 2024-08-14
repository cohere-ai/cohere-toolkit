import os

import pytest
import pandas as pd
from backend.config.deployments import ModelDeploymentName
from backend.config.tools import ToolName
from backend.crud import agent as agent_crud
from backend.database_models.agent import Agent
from backend.tools import GoogleDrive
from tqdm import tqdm
import datetime
import json

# create time stamp
timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
QUERIES_FILE = "eno_manual_queries.jsonl"
DEBUG = True
VERBOSE = True


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
            print(f"Ground Truth: {ground_truth}\nResult: {results[i]}") if VERBOSE else None
            if ground_truth in results[i]:
                num_relevant += 1
                break

    return min(1, num_relevant / len(ground_truths))


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

    json_file = "/Users/trushant/playground/cohere-toolkit/debug.jsonl" if DEBUG else QUERIES_FILE
    # Read the queries and golden texts from the json file which has the format {"query": "query text", "golden_text": "golden text"}
    with open(json_file, "r") as f:
        data = f.readlines()
        queries = []
        golden_texts = []
        for line in data:
            json_data = json.loads(line)
            queries.append(json_data["query"])
            golden_texts.append(json_data["golden_text"])

    assert len(queries) == len(golden_texts)

    df = pd.DataFrame()
    for k in [10]:
        # Run the queries and print the results
        # show tqdm progress bar
        recall_scores = []

        for query, golden_text in tqdm(zip(queries, golden_texts), total=len(queries)):
            result = await query_gdrive(agent, sa_info, session, query)
            # print(f"TK: {result}")
            results = [res["text"] for res in result]
            print(f"Query: {query}") if VERBOSE else None
            try:
                sources = [res["title"] for res in result]
                # print("\n--\n".join([f"{source}: {result}" for source, result in zip(sources, results)]))
            except:
                #
                # print("\n--\n".join(results))
                pass

            # calculate recall@k
            recall = calculate_recall_at_k(results, golden_text, k)
            print(f"Recall@{k}: {recall}")

            recall_scores.append(recall)
            # store query, results, golden texts  and recall in a dataframe
            # do not use df.append
            df = pd.concat(
                [
                    df,
                    pd.DataFrame(
                        {
                            "Query": [query],
                            "Results": [results],
                            "Golden Texts": [golden_text],
                            f"Recall@{k}": [recall],
                        }
                    ),
                ]
            )

        # Calculate the average recall@k
        avg_recall = sum(recall_scores) / len(recall_scores)
        print(f"Average Recall@{k}: {avg_recall}")
        print(df)
        df.to_csv(f"gdrive_results_{k}_{timestamp}.csv", index=False)
