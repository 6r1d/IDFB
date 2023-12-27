from github import Github
from github import Auth

"""
GitHub interface library.
"""

class GitHubSender:

    def __init__(self, token, repository):
        """
        Args:
            token (str): GitHub application token
            repository (str): a string pointing to the GitHub account and repo,
                              like "username/some_repository"
        """
        self.token = token
        self.repository = repository

    def create_issue(self, title, text):
        """
        Create a GitHub issue

        Args:
            title (str): issue title
            text (str): issue text
        
        Returns:
            (issue): GitHub issue instance
        """
        auth = Auth.Token(self.token)
        g = Github(auth=auth)
        repo = g.get_repo(self.repository)
        issue_inst = repo.create_issue(title=title, body=text)
        return f'https://github.com/{self.repository}/issues/{issue_inst.number}'
