import os
import time
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv
from pydantic import BaseModel

from backend.config.settings import Settings
from backend.services.compass import Compass

load_dotenv()
BASE_URL = "https://api.carbon.ai"
CUSTOMER_ID = "tanzim_test_gmail_test4"
API_KEY = os.getenv("CARBON_API_KEY", "")
GMAIL_TOOL = "GMAIL"
SEARCH_LIMIT = 5


# copy pasta main script code, setup modules later
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


BASE_URL = "https://api.carbon.ai"
CUSTOMER_ID = "tanzim_test_gmail_test4"
API_KEY = os.getenv("CARBON_API_KEY", "")
GMAIL_TOOL = "GMAIL"
SEARCH_LIMIT = 5


def get_headers() -> Dict[str, str]:
    return {
        "authorization": "Bearer " + API_KEY,
        "customer-id": CUSTOMER_ID,
        "Content-Type": "application/json",
    }


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


# TODO: this is different
def list_email_by_ids(ids: List[int]) -> List[EmailsToIndex]:
    url = f"{BASE_URL}/user_files_v2"
    payload = {
        "include_raw_file": True,
        "include_parsed_text_file": True,
        "include_additional_files": True,
        "order_by": "created_at",
        "filters": {
            "sync_statuses": ["READY"],
            "ids": ids,
        },
        "pagination": {"limit": 1, "offset": 0},
    }
    headers = get_headers()
    response = requests.request("POST", url, json=payload, headers=headers)
    print(response.text)
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
    print(rv)
    return rv, errs


def init_compass():
    return Compass(
        compass_api_url=Settings().compass.api_url,
        compass_parser_url=Settings().compass.parser_url,
        compass_username=Settings().compass.username,
        compass_password=Settings().compass.password,
    )


def index_on_compass(
    compass: Compass, index_name: str, items: List[EmailsToIndex]
) -> List[Any]:
    compass.invoke(
        compass.ValidActions.CREATE_INDEX,
        {
            "index": index_name,
        },
    )
    print("index created")
    statuses = []
    for item in items:
        print("indexing", item)
        try:
            bs = download_web_link(item.presigned_url)
            file_id_str = f"carbonID:{item.id}"
            compass.invoke(
                compass.ValidActions.CREATE,
                {
                    "index": index_name,
                    "file_id": file_id_str,
                    # "filename": item.name,
                    "file_bytes": bs,
                    "file_extension": item.stats.file_format,
                    "custom_context": {
                        **item.meta.model_dump(),
                        **item.stats.model_dump(),
                    },
                },
            )
            compass.invoke(
                compass.ValidActions.ADD_CONTEXT,
                {
                    "index": index_name,
                    "file_id": file_id_str,
                    "context": {
                        "title": item.name,
                        "last_updated": int(time.time()),
                        "source_created_at": item.source_created_at,
                    },
                },
            )
            statuses.append({"id": item.id, "status": "Success"})
        except Exception as e:
            print(e)
            statuses.append({"id": item.id, "status": "Fail", "error": str(e)})
    return statuses


def download_web_link(url: str) -> bytes:
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    raise Exception(f"Failed to download {url}")


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


# copied from toolkit code
def query_compass(
    compass: Compass, index_name: str, query: str, top_k=SEARCH_LIMIT
) -> List[Dict[str, Any]]:
    hits = compass.invoke(
        action=Compass.ValidActions.SEARCH,
        parameters={
            "index": index_name,
            "query": query,
            "top_k": top_k,
        },
    ).result["hits"]
    chunks = sorted(
        [
            {
                "text": chunk["content"]["text"],
                "score": chunk["score"],
                "title": hit["content"].get("title", ""),
            }
            for hit in hits
            for chunk in hit["chunks"]
        ],
        key=lambda x: x["score"],
        reverse=True,
    )[:top_k]

    return chunks


# example that will trigger the webhook
# "payload": "{\"webhook_type\": \"FILE_READY\", \"obj\": {\"object_type\": \"FILE\", \"object_id\": \"10794291\", \"additional_information\": {\"is_resync\": \"False\", \"request_id\": null}}, \"customer_id\": \"tanzim_test_gmail_test4\", \"timestamp\": \"1724273081\"}
