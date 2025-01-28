from github import Auth, Github


class GithubClient:
    def __init__(self, auth_token, search_limit=20):
        auth = Auth.Token(auth_token)
        self.client = Github(auth=auth, per_page=search_limit)

    def search_all(self, query: str):
        code_results =  self.search_code(query)
        commits_results = self.search_commits(query)
        pr_results = self.search_pull_requests(query)
        all_results = []
        all_results.extend(code_results)
        all_results.extend(commits_results)
        all_results.extend(pr_results)
        return all_results


    def search_code(self, query: str):
        return self.client.search_code(query, sort="indexed", order="desc")

    def search_repositories(self, query: str):
        return self.client.search_repositories(query)

    def search_pull_requests(self, query: str):
        return self.client.search_issues(f"{query} is:pr")

    def search_commits(self, query: str):
        return self.client.search_commits(query)

    def get_user(self):
        return self.client.get_user()

    def get_user_repositories(self, user):
        return user.get_repos(type="all")


