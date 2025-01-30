from github import Auth, Github

from backend.tools.github.constants import SEARCH_LIMIT


class GithubClient:
    def __init__(self, auth_token, search_limit=SEARCH_LIMIT):
        auth = Auth.Token(auth_token)
        self.client = Github(auth=auth, per_page=search_limit)

    def search_all(self, query: str):
        code_results =  self.search_code(query)
        all_results = {"code": code_results}
        return all_results


    def search_code(self, query: str):
        return self.client.search_code(query).get_page(0)

    def search_repositories(self, query: str):
        return self.client.search_repositories(query).get_page(0)

    def search_pull_requests(self, query: str):
        return self.client.search_issues(f"{query} is:pr").get_page(0)

    def search_commits(self, query: str):
        return self.client.search_commits(query).get_page(0)

    def get_user(self):
        return self.client.get_user()

    def get_user_repositories(self, user):
        return user.get_repos(type="all")


