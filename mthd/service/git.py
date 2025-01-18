import git

from mthd.domain.commit import CommitMessage, StageStrategy


class GitService:
    def __init__(self, repo: git.Repo):
        self._repo = repo

    def stage_and_commit(self, message: CommitMessage):
        """Stage all changes and create a commit with the given message.

        Args:
            message: CommitMessage object containing commit metadata
        """
        # Stage all changes
        self._repo.git.add(A=True)

        # Create commit with formatted message
        self._repo.index.commit(message.format())

    def should_commit(self, strategy: StageStrategy) -> bool:
        """Determine if the repo state can be staged and committed

        Returns:
            @todo: decide if the unstaged files are suitable for committing
        """
        if strategy == StageStrategy.ALL:
            return True
