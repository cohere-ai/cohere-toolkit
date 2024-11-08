from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


class GmailClient:
    def __init__(self, auth_token, search_limit=20):
        creds = Credentials(auth_token)
        self.service = build("gmail", "v1", credentials=creds, cache_discovery=False)
        self.search_limit = search_limit

    def search_all(self, query):
        return (
            self.service.users()
            .messages()
            .list(userId="me", q=query, maxResults=self.search_limit)
            .execute()
        )

    def retrieve_messages(self, message_ids):
        messages = []

        for message_id in message_ids:
            message = (
                self.service.users()
                .messages()
                .get(userId="me", id=message_id)
                .execute()
            )
            messages.append(message)

        return messages
