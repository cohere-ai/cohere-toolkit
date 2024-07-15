from concurrent import futures
from typing import List

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from backend.tools.google_drive.constants import DOC_FIELDS


def perform(file_ids: List[str], creds: Credentials) -> List[str]:
    results = []

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures_list = [
            executor.submit(_get_file, file_id, creds) for file_id in file_ids
        ]
        for future in futures.as_completed(futures_list):
            try:
                results.append(future.result())
            except Exception as e:
                raise e
    return results


def _get_file(file_id: str, creds: Credentials):
    service = build("drive", "v3", credentials=creds)
    return (
        service.files()
        .get(
            fileId=file_id,
            fields=DOC_FIELDS,
            supportsAllDrives=True,
        )
        .execute()
    )
