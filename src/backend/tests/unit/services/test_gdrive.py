# %%
import requests
from backend.tests.unit.factories import get_factory
import json
import random
import pandas as pd

VERBOSE = True
BASE_URL = "http://localhost:8000"
# BASE_URL = "http://nginx:80"
BASE_QUERY = "./"
QUERIES_FILE = BASE_QUERY + "eno_finqa_queries.jsonl"
# FILE_BASE_PATH = "/Users/trushant/playground/fde/compass/docs/flat/wally/"
FILE_BASE_PATH = "/Users/trushant/playground/fde/compass/docs/flat/"


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


def query_files(query, golden_docs):
    chat_url = f"{BASE_URL}/v1/chat-stream"

    headers = {"User-Id": "user-id", "Deployment-Name": "Cohere Platform", "Content-Type": "application/json"}

    data = {
        "message": query,
        # "conversation_id": "192b3f59-915d-464e-ba81-e90d10c6c362",
        # "agent_id": "192b3f59-915d-464e-ba81-e90d10c6c362",
        "temperature": 0.3,
        "tools": [{"name": "google_drive"}],
    }
    response = requests.post(chat_url, headers=headers, json=data)
    print(f"Response: {response.text}") if VERBOSE else None
    if response.status_code == 200:
        # Extract the documents from the response
        for line in response.iter_lines():
            if line:
                data = line.decode("utf-8")
        print(f"Data: {data}") if VERBOSE else None
        try:
            documents = "[" + data.split('"documents": [')[1].split("]")[0] + "]"
            documents = json.loads(documents)
            results = []
            # Extract the text from the documents
            for i in range(len(documents)):
                results.append(documents[i]["text"])
            # Calculate recall@k
            recall = calculate_recall_at_k(results, golden_docs, k=10)
        except Exception as e:
            print(f"Error: {e}")
            recall = 0
        return recall
    else:
        print(f"Failed to get chat stream response. Status code: {response.status_code}")
        return None


with open(QUERIES_FILE, "r") as f:
    queries = f.readlines()

queries_list = []
recall_list = []
for _, query_line in enumerate(queries):
    print("--" * 20)
    query = json.loads(query_line)["query"]
    golden_docs = json.loads(query_line)["golden_text"]
    filepath = json.loads(query_line)["metadata"]
    print(f"Query: {query}")
    recall = query_files(query, golden_docs)
    print(f"Recall: {recall}")
    queries_list.append(query)
    recall_list.append(recall)

df = pd.DataFrame({"query": queries_list, "recall": recall_list})
print(df)
df.to_csv("recall_results.csv", index=False)
