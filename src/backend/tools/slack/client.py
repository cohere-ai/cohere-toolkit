from slack_sdk import WebClient


class SlackClient:
    def __init__(self, auth_token, search_limit=20):
        self.client = WebClient(token=auth_token)
        self.search_limit = search_limit

    def search_all(self, query):
        return self.client.search_all(query=query, count=self.search_limit)
