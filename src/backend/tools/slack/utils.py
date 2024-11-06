
from backend.database_models.database import get_session
from backend.services.logger.utils import LoggerFactory
from backend.tools.base import ToolAuthException
from backend.tools.slack import SlackAuth
from backend.tools.slack.client import SlackClient
from backend.tools.slack.constants import SEARCH_LIMIT, SLACK_TOOL_ID

logger = LoggerFactory().get_logger()


class SlackService:
    def __init__(self, user_id: str, auth_token: str, search_limit=SEARCH_LIMIT):
        self.user_id = user_id
        self.auth_token = auth_token
        self.client = SlackClient(auth_token=auth_token, search_limit=search_limit)

    def search_all(self, query: str):
        return self.client.search_all(query=query)

    def serialize_results(self, response):
        results = []
        for match in response["messages"]["matches"]:
            document = self.extract_message_data(match)
            results.append(document)
        for match in response["files"]["matches"]:
            document = self.extract_files_data(match, response["query"])
            results.append(document)

        return results

    @staticmethod
    def extract_message_data(message_json):
        document = {}
        document["type"] = "message"
        if "text" in message_json:
            document["text"] = str(message_json.pop("text"))
        if "permalink" in message_json:
            document["url"] = str(message_json.pop("permalink"))
        if "channel" in message_json and "name" in message_json["channel"]:
            document["title"] = str(message_json["channel"]["name"])

        return document

    @staticmethod
    def extract_files_data(message_json, query=""):
        document = {}
        document["type"] = "file"
        if "permalink" in message_json:
            document["url"] = str(message_json.pop("permalink"))
        if "title" in message_json:
            document["title"] = str(message_json["title"])
            document["text"] = f"{query} in {str(message_json['title'])}"

        return document


def get_slack_service(user_id: str, search_limit=SEARCH_LIMIT) -> SlackService:
    slack_auth = SlackAuth()
    auth_token = None
    session = next(get_session())
    if slack_auth.is_auth_required(session, user_id=user_id):
        session.close()
        raise ToolAuthException(
            "Slack Tool auth Error: Agent creator credentials need to re-authenticate",
            SLACK_TOOL_ID,
        )

    auth_token = slack_auth.get_token(session=session, user_id=user_id)
    if auth_token is None:
        session.close()
        raise Exception("Slack Tool Error: No credentials found")

    service = SlackService(user_id=user_id, auth_token=auth_token, search_limit=search_limit)
    session.close()
    return service


