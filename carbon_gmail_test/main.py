import os
from typing import List, Optional

import requests
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()
BASE_URL = "https://api.carbon.ai"
CUSTOMER_ID = "tanzim_test_gmail"
API_KEY = os.getenv("CARBON_API_KEY")
TOOL = "GOOGLE_DRIVE"


def get_header():
    return {
        "authorization": "Bearer " + API_KEY,
        "customer-id": CUSTOMER_ID,
        "Content-Type": "application/json",
    }


def auth():
    url = f"{BASE_URL}/integrations/oauth_url"
    payload = {"service": TOOL}
    headers = get_header()
    response = requests.request("POST", url, json=payload, headers=headers)

    print(response.text)


def user_sources() -> List[int]:
    url = f"{BASE_URL}/user_data_sources"
    payload = {"filters": {"source": TOOL}}
    headers = get_header()
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
    headers = get_header()
    response = requests.request("POST", url, json=payload, headers=headers)
    print(response.text)


class FileMetadata(BaseModel):
    is_folder: bool
    is_shortcut: bool
    root_external_file_id: Optional[str] = None
    parent_external_file_id: Optional[str] = None


class FileStats(BaseModel):
    file_format: str
    file_size: int
    mime_type: str


class FilesToIndex(BaseModel):
    id: int
    parent_id: Optional[int] = None
    name: str
    external_file_id: str
    external_url: str
    presigned_url: str
    meta: FileMetadata
    stats: Optional[FileStats] = None


def get_file_stats(item) -> Optional[FileStats]:
    if item.get("file_statistics") is not None:
        return FileStats(
            file_format=item.get("file_statistics").get("file_format"),
            file_size=item.get("file_statistics").get("file_size"),
            mime_type=item.get("file_statistics").get("mime_type"),
        )
    return


def list_files_v2() -> List[FilesToIndex]:
    url = f"{BASE_URL}/user_files_v2"
    payload = {"include_raw_file": True}
    headers = get_header()
    response = requests.request("POST", url, json=payload, headers=headers)
    print(response.text)
    if response.status_code != 200:
        return []
    res = response.json()
    items = res.get("results", [])
    rv = []
    for item in items:
        try:
            v = FilesToIndex(
                id=item.get("id"),
                parent_id=item.get("parent_id"),
                name=item.get("name"),
                external_file_id=item.get("external_file_id"),
                external_url=item.get("external_url"),
                presigned_url=item.get("presigned_url"),
                stats=get_file_stats(item),
                meta=FileMetadata(
                    is_folder=item.get("file_metadata", {}).get("is_folder", False),
                    is_shortcut=item.get("file_metadata", {}).get("is_shortcut", False),
                    root_external_file_id=item.get("file_metadata", {}).get(
                        "root_external_file_id"
                    ),
                    parent_external_file_id=item.get("file_metadata", {}).get(
                        "parent_external_file_id"
                    ),
                ),
            )
            rv.append(v)
        except Exception as e:
            print(e)
    return rv


# auth()
source_ids = user_sources()
# list_items(source_ids[0])
list_files_v2()
