import base64

from backend.database_models.database import get_session
from backend.services.logger.utils import LoggerFactory
from backend.tools.base import ToolAuthException
from backend.tools.gmail import GmailAuth
from backend.tools.gmail.client import GmailClient
from backend.tools.gmail.constants import GMAIL_TOOL_ID, SEARCH_LIMIT

logger = LoggerFactory().get_logger()


def decode_base64_raw(raw):
    return base64.urlsafe_b64decode(raw).decode("utf-8")


class GmailService:
    def __init__(self, user_id: str, auth_token: str, search_limit=SEARCH_LIMIT):
        self.user_id = user_id
        self.auth_token = auth_token
        self.client = GmailClient(auth_token=auth_token, search_limit=search_limit)

    def search_all(self, query: str):
        return self.client.search_all(query=query)

    def retrieve_messages(self, message_ids):
        return self.client.retrieve_messages(message_ids)

    def serialize_results(self, messages):
        results = []

        for message in messages:
            results.append(self.serialize_result(message))

        return results

    def serialize_result(self, message):
        data = {
            "title": "",
            "text": "",
            "type": "message",
            "url": "https://mail.google.com/mail/u/0/#inbox/%s" % message.get('threadId', '')
        }

        payload = message["payload"]

        # Find subject title
        if (headers := payload.get("headers")) is not None:
            # Get miscellaneous header values in K-V format
            headers_dict = {header["name"]: header["value"] for header in headers}
            stripped_headers = {
                key: str(value)
                for key, value in headers_dict.items()
                if isinstance(value, (str, int, bool))
            }

            data.update(stripped_headers)

            if "Subject" in data:
                data["title"] = data.pop("Subject")

        # Build text
        if (part := payload.get("parts")) is not None:
            if (body := part[0].get("body", {}).get("data")) is not None:
                data["text"] = decode_base64_raw(body)

            if not data["text"]:
                part_parts = part[0].get("parts")

                if part_parts:
                    for part_part in part_parts:
                        content_type = self.get_header_value(
                            part_part["headers"],
                            'Content-Type',
                        )

                        if content_type.startswith('text/plain;') and part_part["body"]["size"]:
                            if data["text"]:
                                data["text"] += ' '

                            data["text"] += decode_base64_raw(part_part["body"].get("data", ""))

        # Remove metadata fields
        metadata_prefixes = ["ARC", "DKIM", "X"]

        data = {
            key: value
            for key, value in data.items()
            if key.split("-")[0] not in metadata_prefixes
        }

        data["text"] = data["text"].replace("\r\n", " ")

        return data

    def get_header_value(self, headers, name):
        value = ''

        for header in headers:
            if header.get('name') == name:
                value = header.get('value', '')

        return value

def get_gmail_service(user_id: str, search_limit=SEARCH_LIMIT) -> GmailService:
    gmail_auth = GmailAuth()
    session = next(get_session())

    if gmail_auth.is_auth_required(session, user_id=user_id):
        session.close()
        raise ToolAuthException(
            "[Gmail] Auth Error: Agent creator credentials need to re-authenticate",
            GMAIL_TOOL_ID,
        )

    auth_token = gmail_auth.get_token(session=session, user_id=user_id)
    if auth_token is None:
        session.close()
        raise Exception("[Gmail] Auth Error: No credentials found")

    service = GmailService(user_id=user_id, auth_token=auth_token, search_limit=search_limit)
    session.close()

    return service
