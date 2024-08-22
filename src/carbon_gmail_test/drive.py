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
GDRIVE_TOOL = "GOOGLE_DRIVE"


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


def get_headers() -> Dict[str, str]:
    return {
        "authorization": "Bearer " + API_KEY,
        "customer-id": CUSTOMER_ID,
        "Content-Type": "application/json",
    }


def get_file_stats(item: Dict[str, Any]) -> Optional[FileStats]:
    if item.get("file_statistics") is not None:
        return FileStats(
            file_format=item.get("file_statistics").get("file_format"),
            file_size=item.get("file_statistics").get("file_size"),
            mime_type=item.get("file_statistics").get("mime_type"),
        )
    return


def get_file_meta(item: Dict[str, Any]) -> FileMetadata:
    return FileMetadata(
        is_folder=item.get("file_metadata", {}).get("is_folder", False),
        is_shortcut=item.get("file_metadata", {}).get("is_shortcut", False),
        root_external_file_id=item.get("file_metadata", {}).get(
            "root_external_file_id"
        ),
        parent_external_file_id=item.get("file_metadata", {}).get(
            "parent_external_file_id"
        ),
    )


def get_files_to_index(item: Dict[str, Any]) -> List[FilesToIndex]:
    return FilesToIndex(
        id=item.get("id"),
        parent_id=item.get("parent_id"),
        name=item.get("name"),
        external_file_id=item.get("external_file_id"),
        external_url=item.get("external_url"),
        presigned_url=item.get("presigned_url"),
        stats=get_file_stats(item),
        meta=get_file_meta(item),
    )


def list_files_v2() -> List[FilesToIndex]:
    url = f"{BASE_URL}/user_files_v2"
    payload = {"include_raw_file": True}
    headers = get_headers()
    response = requests.request("POST", url, json=payload, headers=headers)
    # print(response.text)
    if response.status_code != 200:
        return []
    res = response.json()
    items = res.get("results", [])
    rv: List[FilesToIndex] = []
    errs: List[str] = []
    for item in items:
        try:
            v = get_files_to_index(item)
            rv.append(v)
        except Exception as e:
            errs.append(str(e))
    return rv, errs


def index_on_compass(items: List[FilesToIndex]):
    for item in items:
        print(
            f"indexing id {item.id}, {item.name} with presigned url {item.presigned_url}"
        )


def main_gdrive():
    # auth()
    # source_ids = user_sources(GDRIVE_TOOL)
    # print(source_ids)
    # setup_auto_sync()
    # list_items(source_ids[0])
    files, errs = list_files_v2()
    if errs:
        print("Errors: ", errs)
    index_on_compass(files)


if __name__ == "__main__":
    # list_webhook()
    # add_webhook()
    main_gdrive()
