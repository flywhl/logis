from datetime import datetime
from enum import Enum, StrEnum, auto
from typing import Optional

import git

from mthd.util.model import Model


class CommitKind(StrEnum):
    EXP = "exp"
    FIX = "fix"
    FEAT = "feat"
    CHORE = "chore"
    TOOLING = "tooling"
    REFACTOR = "refactor"


class Commit(Model):
    sha: str
    message: str
    date: datetime
    kind: Optional[CommitKind]
    metadata: dict

    @staticmethod
    def from_git(commit: git.Commit) -> "Commit":
        message = commit.message if isinstance(commit.message, str) else commit.message.decode()
        return Commit(
            sha=commit.hexsha,
            message=message,
            date=commit.committed_datetime,
            kind=Commit._parse_kind(message),
            metadata={},
        )

    @staticmethod
    def _parse_kind(message: str) -> Optional[CommitKind]:
        if message.startswith("exp:"):
            return CommitKind.EXP
        if message.startswith("fix:"):
            return CommitKind.FIX
        if message.startswith("feat:"):
            return CommitKind.FEAT
        if message.startswith("chore:"):
            return CommitKind.CHORE
        if message.startswith("tooling:"):
            return CommitKind.TOOLING
        if message.startswith("refactor:"):
            return CommitKind.REFACTOR
        return None


class StageStrategy(Enum):
    ALL = auto()
