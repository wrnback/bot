from azure.devops.connection import Connection
from azure.devops.v5_1.git.models import GitPullRequestSearchCriteria
from msrest.authentication import BasicAuthentication

from .base import Base
from .exceptions import (
    ProjectNotFoundError, TeamNotFoundError, RepositoryNotFoundError,
    TeamMembersListEmpty
)


class Azure(Base):

    def __init__(self, debug=False):
        super().__init__(module_path=__name__, debug=debug)
        self.connection = self._get_connection()
        self.project = self._get_project()
        self.team = self._get_team()
        self.team.repositories = self._get_repositories()
        self.team.members = self._get_filtered_team_members()
        self.team.get_pull_requests = self._get_team_pull_requests

    def _get_connection(self):
        credentials = BasicAuthentication("", self.config["azure"]["token"])
        return Connection(
            base_url=f"{self.config['azure']['host']}/{self.config['azure']['organization']}", 
            creds=credentials
        )

    @property
    def core_client(self):
        return self.connection.clients.get_core_client()

    @property
    def git_client(self):
        return self.connection.clients.get_git_client()
    
    def _get_project(self):
        for project in self.core_client.get_projects().value:
            if project.name == self.config["azure"]["project"]:
                return project
        raise ProjectNotFoundError(f"Project '{project_name}' not founded")

    def _get_team(self, team_name = None):
        if not team_name:
            team_name = self.config["azure"]["team"]
        for team in self.core_client.get_teams(self.project.id):
            if team.name == team_name:
                return team
        raise TeamNotFoundError(f"Team '{team_name}' not founded")

    def _get_team_members(self, *, team = None):
        result = []
        if not team:
            team = self.team
        members = self.core_client.get_team_members_with_extended_properties(
            self.project.id, team.id)
        if not members:
            raise TeamMembersListEmpty(f"List of team members is empty")
        members = list(filter(lambda member: not member.identity.is_container, members))
        return [member.identity for member in members]

    def _get_repositories(self):
        result = []
        repositories = self.git_client.get_repositories(self.project.id)
        for repo_name in self.config["azure"]["repositories"]:
            for repository in repositories:
                if repository.name == repo_name:
                    result.append(repository)
                    break
            else:
                raise RepositoryNotFoundError(f"Repository '{repo_name}' not founded")
        return result

    def _get_filtered_team_members(self):
        exclude_members = []
        filtered_members = []
        for team_name in self.config["azure"]["exclude_teams"]:
            exclude_team = self._get_team(team_name)
            exclude_members.extend(self._get_team_members(team=exclude_team))
        members = self._get_team_members()
        for member in members:
            if not member.id in [member.id for member in exclude_members]:
                filtered_members.append(member)
        return filtered_members

    def _update_team_pull_requests(self):
        for member in self.team.members:
            member.pull_requests = []
            repo_pull_requests = []
            for repo in self.team.repositories:
                search_criteria = GitPullRequestSearchCriteria(creator_id=member.id)
                repo_pull_requests = self.git_client.get_pull_requests(repo.id, search_criteria)
                if repo_pull_requests:
                    member.pull_requests.extend(repo_pull_requests)

    def _get_team_pull_requests(self):
        self._update_team_pull_requests()
        pull_requests = []
        for member in self.team.members:
            for pull_request in member.pull_requests:
                pull_requests.append({
                    "author": pull_request.created_by.display_name,
                    "status": pull_request.status,
                    "title": pull_request.title,
                    "id": pull_request.pull_request_id,
                    "reviewers": [],
                })
                for reviewer in pull_request.reviewers:
                    pull_requests[len(pull_requests)-1]["reviewers"].append({
                        "name": reviewer.display_name,
                        "approved": reviewer.vote == 10,
                        "is_required": reviewer.is_required == True,
                    })
        return pull_requests
