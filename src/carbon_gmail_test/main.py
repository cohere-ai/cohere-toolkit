import os
from typing import List

import requests
from dotenv import load_dotenv

from carbon_gmail_test.utils import (
    EmailsToIndex,
    get_headers,
    index_on_compass,
    init_compass,
    list_emails_v2,
    query_compass,
)

load_dotenv()
BASE_URL = "https://api.carbon.ai"
CUSTOMER_ID = "tanzim_test_gmail_test4"
API_KEY = os.getenv("CARBON_API_KEY", "")
GMAIL_TOOL = "GMAIL"
SEARCH_LIMIT = 5


def auth(tool: str):
    url = f"{BASE_URL}/integrations/oauth_url"
    payload = {"service": tool}
    headers = get_headers()
    response = requests.request("POST", url, json=payload, headers=headers)
    print(response.text)


def user_sources(tool: str) -> List[int]:
    url = f"{BASE_URL}/user_data_sources"
    payload = {"filters": {"source": tool}}
    headers = get_headers()
    response = requests.request("POST", url, json=payload, headers=headers)
    result_ids = []
    print(response.text)
    if response.status_code == 200:
        json = response.json()
        results = json.get("results", [])
        for r in results:
            result_ids.append(r.get("id", None))
    return [rid for rid in result_ids if rid is not None]


def list_items(source_id: int):
    url = f"{BASE_URL}/integrations/items/list"
    payload = {"data_source_id": source_id}
    headers = get_headers()
    response = requests.request("POST", url, json=payload, headers=headers)
    print(response.text)


def gmail_labels():
    url = f"{BASE_URL}/integrations/gmail/user_labels"
    headers = get_headers()
    response = requests.request("GET", url, headers=headers)
    print(response.text)


def sync_gmail(source_id: int):
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
    response = requests.request("POST", url, json=payload, headers=get_headers())
    print(response.text)


def setup_auto_sync(tool: str):
    url = f"{BASE_URL}/organization/update"
    payload = {"global_user_config": {"auto_sync_enabled_sources": [tool]}}
    response = requests.request("POST", url, json=payload, headers=get_headers())
    print(response.text)


def add_webhook():
    url = f"{BASE_URL}/add_webhook"
    payload = {"url": "https://ba55-206-223-169-46.ngrok-free.app"}
    response = requests.request("POST", url, json=payload, headers=get_headers())
    print(response.text)


def list_webhook():
    url = f"{BASE_URL}/webhooks"
    response = requests.request("POST", url, json={}, headers=get_headers())
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


def main_query_compass():
    compass = init_compass()
    index_name = CUSTOMER_ID
    query = "putin"
    results = query_compass(compass, index_name, query)
    print(results)


def main_gmail():
    def list_all():
        emails, errs = list_emails_v2()
        if errs:
            print("Errors: ", errs)
        print()
        res = index_on_compass(init_compass(), CUSTOMER_ID, emails)
        print(res)

    def auth_and_check():
        setup_auto_sync(GMAIL_TOOL)
        gmail_labels()

    def sync():
        source_ids = user_sources(GMAIL_TOOL)
        print(source_ids)
        sync_gmail(source_ids[0])

    # auth(GMAIL_TOOL)
    # setup_auto_sync(GMAIL_TOOL)
    # sync()
    # gmail_labels()
    list_all()


if __name__ == "__main__":
    # list_webhook()
    # add_webhook()
    main_gmail()
    # main_query_compass()
