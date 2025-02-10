from datetime import datetime
from enum import Enum, auto
from typing import Optional

import git

from mthd.domain.experiment import ExperimentRun, SemanticMessage
from mthd.util.model import Model


class Commit(Model):
    """Represents a git commit"""

    sha: str
    message: str
    date: datetime

    @staticmethod
    def from_git(commit: git.Commit) -> "Commit":
        message = commit.message if isinstance(commit.message, str) else commit.message.decode()
        return Commit(
            sha=commit.hexsha,
            message=message,
            date=commit.committed_datetime,
        )

    def startswith(self, value: str) -> bool:
        return self.message.startswith(value)

    def to_semantic(self) -> "SemanticMessage":
        return SemanticMessage.from_commit(self)


class ExperimentCommit(Commit):
    """A commit that contains experiment data"""

    experiment_run: ExperimentRun

    @classmethod
    def from_commit(cls, commit: Commit) -> Optional["ExperimentCommit"]:
        try:
            exp = ExperimentRun.from_commit(commit)
            if exp:
                return cls(sha=commit.sha, message=commit.message, date=commit.date, experiment_run=exp)
        except ValueError:
            return None
        return None


class StageStrategy(Enum):
    """Strategy for staging files in git"""

    ALL = auto()
