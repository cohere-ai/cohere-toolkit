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
        self.repositories = [repo for repo in self.repositories if repo.full_name == "cohere-ai/cohere-toolkit"]
        # self.organizations = self.github_user.get_orgs()

    def _prepare_repo_query(self, query: str, repo_name: str):
        return f"{query} repo:{repo_name}"

    def search(self, query: str):
        results = {"code": [], "commits": [], "pull_requests": []}
        for repo in self.repositories:
            prepared_query = self._prepare_repo_query(query, repo.full_name)
            if repo.fork:
                prepared_query += " fork:true"
            repo_results = self.client.search_all(query=prepared_query)
            results["code"].extend(repo_results["code"])
            results["commits"].extend(repo_results["commits"])
            results["pull_requests"].extend(repo_results["pull_requests"])
        return results

    def transform_response(self, response):
        results = []
        for code in response["code"]:
            results.append(self._extract_code_data(code))
        for commit in response["commits"]:
            results.append(self._extract_commit_data(commit))
        for pr in response["pull_requests"]:
            results.append(self._extract_pull_request_data(pr))
        return results

    @staticmethod
    def _extract_code_data(code):
        return {
            "title": code.path,
            "text": code.decoded_content.decode("utf-8"),
            "url": code.html_url,
            "type": "code",
        }

    @staticmethod
    def _extract_commit_data(commit):
        return {
            "title": commit.commit.message,
            "description": commit.commit.author.name,
            "url": commit.html_url,
            "type": "commit",
        }


    @staticmethod
    def _extract_pull_request_data(pr):
        return {
            "title": pr.title,
            "description": pr.body,
            "url": pr.html_url,
            "type": "pull_request",
        }


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



