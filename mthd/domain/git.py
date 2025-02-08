from datetime import datetime
from enum import Enum, auto

import git

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


class StageStrategy(Enum):
    """Strategy for staging files in git"""

    ALL = auto()
