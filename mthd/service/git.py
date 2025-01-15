from mthd.domain.commit import CommitMessage


class GitService:
    def stage_and_commit(self, message: CommitMessage): ...
