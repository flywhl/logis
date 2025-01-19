import git

from mthd.domain.git import Commit, StageStrategy


class GitService:
    def __init__(self, repo: git.Repo):
        self._repo = repo

    def get_all_commits(self) -> list[Commit]:
        """Get all commits in the repository.

        Returns:
            List of Commit objects representing the git history
        """
        commits = []
        for commit in self._repo.iter_commits():
            commits.append(Commit.from_git(commit))
        return commits

    def stage_and_commit(self, message: str):
        """Stage all changes and create a commit with the given message.

        Args:
            message: CommitMessage object containing commit metadata
        """
        self._repo.git.add(A=True)

        self._repo.index.commit(message)

    def should_commit(self, strategy: StageStrategy) -> bool:
        """Determine if the repo state can be staged and committed

        Returns:
            @todo: decide if the unstaged files are suitable for committing
        """
        if strategy == StageStrategy.ALL:
            return True
