from backend.database_models.database import get_session
from backend.services.logger.utils import LoggerFactory
from backend.tools.base import ToolAuthException
from backend.tools.github.auth import GithubAuth
from backend.tools.github.client import GithubClient
from backend.tools.github.constants import GITHUB_TOOL_ID, SEARCH_LIMIT

logger = LoggerFactory().get_logger()


class GithubService:
    def __init__(self, user_id: str, auth_token: str, search_limit=SEARCH_LIMIT):
        self.user_id = user_id
        self.auth_token = auth_token
        self.client = GithubClient(auth_token=auth_token, search_limit=search_limit)
        self.github_user = self.client.get_user()
        self.repositories = self.client.get_user_repositories(self.github_user)
        # self.organizations = self.github_user.get_orgs()

    def _prepare_repo_query(self, query: str, repo_name: str):
        return f"{query} repo:{repo_name}"

    def search(self, query: str):
        results = []
        for repo in self.repositories:
            prepared_query = self._prepare_repo_query(query, repo.full_name)
            results.extend(self.client.search_all(query=prepared_query))
        return results


    def serialize_results(self, response):
        results = []
        for item in response:
            if "message" in item:
                results.append(self.extract_message_data(item["message"]))
            if "file" in item:
                results.append(self.extract_files_data(item["file"], query=item["query"]))
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


def get_github_service(user_id: str, search_limit=SEARCH_LIMIT) -> GithubService:
    github_auth = GithubAuth()
    session = next(get_session())
    if github_auth.is_auth_required(session, user_id=user_id):
        session.close()
        raise ToolAuthException(
            "Github Tool auth Error: Agent creator credentials need to re-authenticate",
            GITHUB_TOOL_ID,
        )

    auth_token = github_auth.get_token(session=session, user_id=user_id)
    if auth_token is None:
        session.close()
        raise Exception("Github Tool Error: No credentials found")

    service = GithubService(user_id=user_id, auth_token=auth_token, search_limit=search_limit)
    session.close()
    return service



