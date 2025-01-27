from github import Auth, Github


class GithubClient:
    def __init__(self, auth_token, search_limit=20):
        auth = Auth.Token(auth_token)
        self.client = Github(auth=auth, per_page=search_limit)

    def search_all(self, query):
        return self.client.search_code(query, sort="indexed", order="desc")


    def search_code(self, query):
        return self.client.search_code(query, sort="indexed", order="desc")

    def search_repositories(self, query):
        return self.client.search_repositories(query, sort="indexed", order="desc")

    def search_issues(self, query):
        return self.client.search_issues(query, sort="indexed", order="desc")

    def search_commits(self, query):
        return self.client.search_commits(query, sort="indexed", order="desc")

    def get_user(self):
        return self.client.get_user()

    def get_user_repositories(self, user):
        return user.get_repos()


