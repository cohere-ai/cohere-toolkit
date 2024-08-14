import asyncio
import base64
import os.path
import re
import time
from pprint import pprint
from typing import Any, Dict, List, Tuple

import cohere
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pydantic import BaseModel

from backend.config.settings import Settings
from backend.services.compass import Compass

COHERE_API_KEY_ENV_VAR = "COHERE_API_KEY"
DEFAULT_RERANK_MODEL = "rerank-english-v2.0"
load_dotenv()


api_key = Settings().deployments.cohere_platform.api_key
compass = Compass()


class SimpleCohere:
    client_name = "cohere-toolkit"

    def __init__(self) -> None:
        self.client = cohere.Client(api_key, client_name=self.client_name)

    async def invoke_chat_stream(self, docs, message) -> Any:
        stream = self.client.chat_stream(
            model="command-r-plus",
            documents=docs,
            message=message,
        )
        for event in stream:
            if event.event_type == "text-generation":
                print(event.text)
            elif event.event_type == "stream-end":
                print(event.finish_reason)


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

LABEL_IDS = ["STARRED"]
# LABEL_IDS = ["IMPORTANT", "STARRED"]
# https://developers.google.com/gmail/api/reference/rest/v1/Format
EMAIL_FORMAT = "full"
MAX_RESULTS = 10


def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=53091)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)
        # labels = service.users().labels().list(userId="me").execute()
        results = (
            service.users()
            .messages()
            .list(
                userId="me",
                maxResults=MAX_RESULTS,
                # labelIds=LABEL_IDS,
                q="label:inbox has:attachment ",
            )
            .execute()
        )
        messages = results.get("messages", [])

        if not messages:
            print("No messages found.")
            return

        docs: List[GmailDocument] = [
            process_message(message, service) for message in messages
        ]
        compass_index_name = "gmail_tanzim_test"
        place_on_compass(docs, compass_index_name)
        compass_docs = query_compass(compass_index_name, "what did rod say?", 5)
        cleaned_docs = [d.copy() for d in compass_docs]
        for d in cleaned_docs:
            del d["score"]
        cohere_client = SimpleCohere()
        asyncio.run(
            cohere_client.invoke_chat_stream(
                docs=cleaned_docs, message="summarize what rod said"
            )
        )

    except HttpError as error:
        print(f"An error occurred: {error}")


class GmailDocument(BaseModel):
    id: str
    thread_id: str
    title: str
    email_from: str
    email_to: str
    subject: str
    snippet: str
    content: str
    attachment_ids: List[str] = []


def query_compass(index_name: str, query: str, top_k: int) -> List[Dict[str, Any]]:
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


def place_on_compass(docs: List[GmailDocument], index_name: str):
    # idempotent create index
    compass.invoke(
        action=Compass.ValidActions.CREATE_INDEX,
        parameters={"index": index_name},
    )
    for d in docs:
        compass.invoke(
            action=Compass.ValidActions.CREATE,
            parameters={
                "index": index_name,
                "file_id": d.id,
                "file_text": d.content,
            },
        )
        compass.invoke(
            action=Compass.ValidActions.ADD_CONTEXT,
            parameters={
                "index": index_name,
                "file_id": d.id,
                "context": {
                    "title": d.title,
                    "snippet": d.snippet,
                    "email_from": d.email_from,
                    "email_to": d.email_to,
                    "last_updated": int(time.time()),
                },
            },
        )
        compass.invoke(
            action=Compass.ValidActions.REFRESH,
            parameters={"index": index_name},
        )


def process_message(message: Dict[str, Any], service: Any) -> List[GmailDocument]:
    message_id = message["id"]
    thread_id = message["threadId"]
    email = (
        service.users()
        .messages()
        .get(userId="me", id=message_id, format=EMAIL_FORMAT)
        .execute()
    )
    important_headers = process_email_headers(email["payload"]["headers"])
    title = f"""
    Subject:{important_headers['Subject']}
    Snippet:{email['snippet']}"""

    # parallelize this
    all_parts, attachment_ids = process_email_payload(email["payload"])
    content = "\n".join(all_parts)
    print("====================================")
    print("Id:", message_id)
    print("Title:", title)
    print("Content\n", content)
    return GmailDocument(
        id=message_id,
        thread_id=thread_id,
        title=title,
        content=content,
        snippet=email["snippet"],
        email_from=important_headers["From"],
        email_to=important_headers["To"],
        subject=important_headers["Subject"],
        attachment_ids=attachment_ids,
    )


def decode_base64(data: bytes) -> str:
    return base64.urlsafe_b64decode(data).decode("utf-8")


def process_email_raw(bs: bytes) -> str:
    return decode_base64(bs)


def process_email_headers(headers: List[dict]) -> dict:
    important_headers = ["From", "To", "Subject", "Date"]
    return {
        header["name"]: header["value"]
        for header in headers
        if header["name"] in important_headers
    }


def process_email_payload(payload: Any) -> Tuple[List[str], List[str]]:
    all_parts = []
    attachment_ids = []
    if payload.get("body", {}).get("attachmentId", None):
        attachment_ids.append(payload["body"]["attachmentId"])
    match payload["mimeType"]:
        # TODO: allow compass to handle the parsing of html
        case "text/plain":
            text_b64 = payload.get("body", {}).get("data", None)
            all_parts.append(decode_base64(text_b64)) if text_b64 else None
        # TODO, what to do with images?
        case "image/jpeg":
            pass
        case "text/html":
            html_content_b64 = payload.get("body", {}).get("data", None)
            if html_content_b64:
                soup = BeautifulSoup(decode_base64(html_content_b64), "html.parser")
                text = soup.get_text(separator="\n")
                # remove redundant newlines
                text = re.sub(r"\n+", "\n", text)
                all_parts.append(text)
        case "multipart/alternative" | "multipart/related":
            for p in payload.get("parts", []):
                inner_parts, inner_attachment_ids = process_email_payload(p)
                all_parts.extend(inner_parts)
                attachment_ids.extend(inner_attachment_ids)
        case _:
            pass
    cleaned_parts = [p for p in all_parts if p]
    return (cleaned_parts, attachment_ids)


if __name__ == "__main__":
    main()
