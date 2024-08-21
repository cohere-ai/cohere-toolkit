import os
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()
BASE_URL = "https://api.carbon.ai"
CUSTOMER_ID = "tanzim_test_gmail_test4"
API_KEY = os.getenv("CARBON_API_KEY", "")
GMAIL_TOOL = "GMAIL"


def get_headers() -> Dict[str, str]:
    return {
        "authorization": "Bearer " + API_KEY,
        "customer-id": CUSTOMER_ID,
        "Content-Type": "application/json",
    }


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


class EmailStats(BaseModel):
    file_format: str
    file_size: int
    mime_type: Optional[str] = None


class EmailMetadata(BaseModel):
    sender: str
    recipient: str
    cc: Optional[str] = None
    is_message: bool
    start_of_thread: bool = False
    root_external_file_id: Optional[str] = None
    parent_external_file_id: Optional[str] = None


class EmailsToIndex(BaseModel):
    id: int
    parent_id: Optional[int] = None
    name: str
    source_created_at: str
    external_file_id: str
    external_url: Optional[str] = None
    presigned_url: str
    meta: Optional[EmailMetadata] = None
    stats: Optional[EmailStats] = None


def get_email_stats(item: Dict[str, Any]) -> Optional[EmailStats]:
    if item.get("file_statistics") is not None:
        return EmailStats(
            file_format=item.get("file_statistics").get("file_format"),
            file_size=item.get("file_statistics").get("file_size"),
            mime_type=item.get("file_statistics").get("mime_type"),
        )
    return


def get_email_meta(item: Dict[str, Any]) -> EmailMetadata:
    return EmailMetadata(
        start_of_thread=item.get("file_metadata", {}).get("start_of_thread", False),
        is_message=item.get("file_metadata", {}).get("is_message", False),
        root_external_file_id=item.get("file_metadata", {}).get(
            "root_external_file_id"
        ),
        sender=item.get("tags", {}).get("sender"),
        recipient=item.get("tags", {}).get("recipient"),
        cc=item.get("tags", {}).get("cc"),
        parent_external_file_id=item.get("file_metadata", {}).get(
            "parent_external_file_id"
        ),
    )


def get_emails_to_index(item: Dict[str, Any]) -> List[EmailsToIndex]:
    return EmailsToIndex(
        id=item.get("id"),
        parent_id=item.get("parent_id"),
        name=item.get("name"),
        source_created_at=item.get("source_created_at"),
        external_file_id=item.get("external_file_id"),
        presigned_url=item.get("presigned_url"),
        stats=get_email_stats(item),
        meta=get_email_meta(item),
    )


def list_emails_v2() -> List[EmailsToIndex]:
    url = f"{BASE_URL}/user_files_v2"
    payload = {
        "include_raw_file": True,
        "include_parsed_text_file": True,
        "include_additional_files": True,
        "order_by": "created_at",
        "filters": {"sync_statuses": ["READY"]},
        "pagination": {"limit": 100, "offset": 0},
    }
    headers = get_headers()
    response = requests.request("POST", url, json=payload, headers=headers)
    # print(response.text)
    if response.status_code != 200:
        return []
    res = response.json()
    items = res.get("results", [])
    rv: List[EmailsToIndex] = []
    errs: List[str] = []
    for item in items:
        try:
            v = get_emails_to_index(item)
            if v.meta.is_message:
                rv.append(v)
        except Exception as e:
            errs.append(str(e))
    return rv, errs


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


def index_on_compass(items: List[EmailsToIndex]):
    for item in items:
        print(
            f"indexing id {item.id}, {item.name} with presigned url {item.presigned_url}"
        )


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


def main_gmail():
    def list_all():
        emails, errs = list_emails_v2()
        if errs:
            print("Errors: ", errs)
        print()
        index_on_compass(emails)

    def sync():
        source_ids = user_sources(GMAIL_TOOL)
        print(source_ids)
        sync_gmail(source_ids[0])

    # auth()
    # setup_auto_sync(GMAIL_TOOL)
    # source_ids = user_sources(GMAIL_TOOL)
    # list_items(source_ids[0])
    # sync_gmail(source_ids[0])
    # gmail_labels()
    list_all()




if __name__ == "__main__":
    # list_webhook()
    # add_webhook()
    main_gmail()
