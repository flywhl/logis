import git
from mthd.domain.commit import CommitMessage


class GitService:
    def __init__(self):
        self.repo = git.Repo(".")
        
    def stage_and_commit(self, message: CommitMessage):
        """Stage all changes and create a commit with the given message.
        
        Args:
            message: CommitMessage object containing commit metadata
        """
        # Stage all changes
        self.repo.git.add(A=True)
        
        # Create commit with formatted message
        commit_text = (
            f"{message.summary}\n\n"
            f"Hyperparameters:\n{message.hyperparameters.model_dump_json(indent=2)}\n\n"
            f"Annotations:\n{sorted(message.annotations)}"
        )
        self.repo.index.commit(commit_text)
