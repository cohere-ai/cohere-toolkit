import base64
import os.path
from typing import Any, List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

LABEL_IDS = ["IMPORTANT", "STARRED"]
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
            .list(userId="me", maxResults=MAX_RESULTS, labelIds=LABEL_IDS)
            .execute()
        )
        messages = results.get("messages", [])

        if not messages:
            print("No messages found.")
            return
        for message in messages:
            message_id = message["id"]
            print("\n=================EMAIL=====================\n")
            print(message_id)
            email = (
                service.users()
                .messages()
                .get(userId="me", id=message_id, format=EMAIL_FORMAT)
                .execute()
            )
            print(email["snippet"])

            all_parts = process_email_payload(email["payload"])
            for p in all_parts:
                decoded_data = base64.urlsafe_b64decode(p)
                print(decoded_data.decode("utf-8"))
                print("\n")

    except HttpError as error:
        print(f"An error occurred: {error}")


def decode_base64(data: bytes) -> str:
    return base64.urlsafe_b64decode(data).decode("utf-8")


def process_email_raw(bs: bytes) -> str:
    return decode_base64(bs)


# if not "raw" in message["payload"]:
def process_email_payload(payload: Any) -> List[bytes]:
    all_parts = []
    match payload["mimeType"]:
        case "text/plain":
            all_parts.append(payload.get("body", {}).get("data", None))
        case "image/jpeg":
            # TODO, what to do with images?
            pass
        case "text/html":
            # TODO, scrape text content only somehow with beautifulsoup?
            # There might already be functions for this
            pass
        case "multipart/alternative" | "multipart/related":
            for part in payload.get("parts", []):
                all_parts.extend(process_email_payload(part))
        case _:
            pass
    return all_parts


if __name__ == "__main__":
    main()
