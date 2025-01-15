from mthd.domain.commit import CommitMessage
from mthd.service.git import GitService


class RepositoryService:
    def __init__(self, git_service: GitService):
        self._git_service = git_service

    def commit(self, message: CommitMessage): ...
