import os
from typing import List

import requests
from dotenv import load_dotenv

from carbon_gmail_test.utils import (
    EmailsToIndex,
    get_headers,
)

load_dotenv()
BASE_URL = os.getenv("BASE_CARBON_URL", "")
API_KEY = os.getenv("CARBON_API_KEY", "")
GMAIL_TOOL = "GMAIL"
SEARCH_LIMIT = 5


def auth(tool: str, customer_id: str):
    url = f"{BASE_URL}/integrations/oauth_url"
    payload = {"service": tool}
    headers = get_headers(customer_id)
    response = requests.request("POST", url, json=payload, headers=headers)
    print(response.text)


def user_sources(tool: str, customer_id: str) -> List[int]:
    url = f"{BASE_URL}/user_data_sources"
    payload = {"filters": {"source": tool}}
    headers = get_headers(customer_id)
    response = requests.request("POST", url, json=payload, headers=headers)
    result_ids = []
    print(response.text)
    if response.status_code == 200:
        json = response.json()
        results = json.get("results", [])
        for r in results:
            result_ids.append(r.get("id", None))
    return [rid for rid in result_ids if rid is not None]


def list_items(source_id: int, customer_id: str):
    url = f"{BASE_URL}/integrations/items/list"
    payload = {"data_source_id": source_id}
    headers = get_headers(customer_id)
    response = requests.request("POST", url, json=payload, headers=headers)
    print(response.text)


def gmail_labels(customer_id: str):
    url = f"{BASE_URL}/integrations/gmail/user_labels"
    headers = get_headers(customer_id)
    response = requests.request("GET", url, headers=headers)
    print(response.text)


def sync_gmail(source_id: int, customer_id: str):
    url = f"{BASE_URL}/integrations/gmail/sync"
    payload = {
        "filters": {
            "AND": [
                {"key": "after", "value": "2024/01/01"},
                # {
                #     "OR": [
                #         {"key": "label", "value": "SENT"},
                #         {"key": "label", "value": "INBOX"},
                #         {"key": "in", "value": "SENT"},
                #     ]
                # },
            ]
        },
        "sync_attachments": True,
        "data_source_id": source_id,
    }
    response = requests.request(
        "POST", url, json=payload, headers=get_headers(customer_id)
    )
    print(response.text)


def setup_auto_sync(tool: str, customer_id: str):
    url = f"{BASE_URL}/organization/update"
    payload = {"global_user_config": {"auto_sync_enabled_sources": [tool]}}
    response = requests.request(
        "POST", url, json=payload, headers=get_headers(customer_id)
    )
    print(response.text)


def mock_index_on_compass(items: List[EmailsToIndex]):
    for item in items:
        print(
            f"indexing id {item.id}, {item.name} with presigned url {item.presigned_url}"
        )


def download_web_link(url: str) -> bytes:
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    raise Exception(f"Failed to download {url}")
