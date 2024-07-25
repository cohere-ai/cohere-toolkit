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

# create time stamp
timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")


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
            # print(f"Ground Truth: {ground_truth}\nResult: {results[i]}")
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
        "apple operating expenses q1 2023",
        "In Amazon's Q2 2023 10-Q, how does the discussion on employee compensation and benefits in the human resources section relate to the reported financial expenses",  # pg 25/51
        "For Microsoft's Q2 2023 report, assess the connection between Microsoft's earnings from international markets and the discussion on currency risk in the financial section.",  # pg 14/80
        "For NVIDIA's Q1 2023 10-Q, what is the relationship between R&D spending and the development of new GPU technologies or services?",  # pg 33/49
        "Microsoft's Q1 2023 10-Q management's discussion on debt management",  # pg 20/72
        "What were the sales figures for NVIDIA's gaming and professional GPU segments in Q3 2023?",  # pg 24/52
        "How did Apple's operating expenses for Q1 2023 compare to its revenue for the same quarter?",  # pg 4/46
        "What is the recommended engine oil for the Audi R8?",  # pg 188/260
        "How does the Electronic Stabilization Program (ESP) function in the Audi R8?",  # pg 166/260
        "jump start Audi R8",  # pg 235/260
        "What is the ground clearance between the axles at kerb weight for my Volkswagan?",  # table pg 676/683
        "How often should I check my tyre tread depth for my Volkswagan?",  # pg 559/683
        "What are the data transfer functions available for my Volkswagan?",  # pg 369/683
        "Cuomo executive order restrictions on gatherings at synagogues",  # PR-NY-0010
        "JP Morgan Chase Bank legal action City of Los Angeles",  # FH-CA-0015
        "Zubik v. Burwell",  # FA-PA-0010
        "2013 redistricting plan of Jefferson County, Florida",  # VR-FL-0171
        "Black Voters Matter Fund and an individual voter had with the state of Georgia's handling of mail-in ballots",  # VR-GA-0170
        "What laws were cited in the case against Plaza Home Mortgage, Inc.?",  # FH-CA-0013
        "phone number for the aetna concierge for Amazon employees",  # ekm single doc amazon
        "impact of 5by20 women initiative",  # ekm coco cola 5by20
        "salary for promo auxiliary to regular BC",  # ekm bc
    ]
    golden_texts = [
        [
            "The decrease in AWS operating income in absolute dollars in Q2 2023 and for the six months ended June 30, 2023, compared to the comparable prior year periods, is primarily due to increased payroll and related expenses and spending on technology infrastructure"
        ],
        [
            "Foreign currency risks related to certain non-U.S. dollar-denominated investments are hedged using foreign exchange forward contracts that are designated as fair value hedging instruments. Foreign currency risks related to certain Euro-denominated debt are hedged using foreign exchange forward contracts that are designated as cash flow hedging instruments."
        ],
        [
            "We have invested in research and development in markets where we have a limited operating history, which may not produce meaningful revenue for several years, if at all"
        ],
        [
            "The obligations under our senior fixed rate notes rank equally in the right of payment with all of our other existing and future senior unsecured indebtedness and effectively rank junior to all liabilities of our subsidiaries"
        ],
        [
            "Total revenue  14,514 $ 2,856",
        ],
        ["Total operating expenses  14,316"],
        [
            "VW 502 00 specifications",
        ],
        [
            "It red uces the risk of skidding under all road cond itions and at a ll speeds and improves vehicle stability"
        ],
        [
            "the battery can be connected to the battery of another vehicle, using a pair of jumper cables to start the engine"
        ],
        ["197 – 216"],
        ["check the tread depth every 5,000 to 10,000"],
        ["Media playback"],
        ["Governor Cuomo issued Executive Order 202.68"],
        [
            "Specifically, Los Angeles seeks injunctive relief and damages for the injuries caused 20 by foreclosures on JPMorgan’s loans in minority neighborhoods and to minority 21 borrowers"
        ],
        [
            "Affordable Care Act and related regulations pending final disposition of their petition for certiorari. Nothing in this interim order affects the ability of the applicants’ or their organizations’ employees to obtain, without cost, the full range of FDA approved contraceptives"
        ],
        [
            "as a violation of their Fourteenth Amendment right to equal representation under the “one person, one vote” principle of the Equal Protection Clause"
        ],
        [
            "requirement that voters affix their own postage to mail-in absentee ballots and mail-in absentee ballot applications is unconstitutiona"
        ],
        ["violation of the Fair Housing Act (FHA), 42 U.S.C. §§ 3601-3619, and the Equal Credit 2 Opportunity Act"],
        ["1-866-574-9124"],
        [
            "The Coca-Cola Company  announced a global initiative to enable the  # economic empowerment of 5 million women  # entrepreneurs across our value chain by the  year 2020"
        ],
        [
            "an auxiliary who has in-service status prior to the closing date of the competition, shall receive a maximum reduction which is the closest step to 8%"
        ],
    ]

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
            # print(f"Query: {query}")
            try:
                sources = [res["title"] for res in result]
                print("\n--\n".join([f"{source}: {result}" for source, result in zip(sources, results)]))
            except:
                print("\n--\n".join(results))
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
