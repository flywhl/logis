import json
from datetime import datetime
from enum import Enum, StrEnum, auto
from typing import Optional

import git

from mthd.config import METADATA_SEPARATOR
from mthd.util.model import Model


class CommitKind(StrEnum):
    """Types of semantic commits"""
    EXP = "exp"
    FIX = "fix"
    FEAT = "feat"
    CHORE = "chore"
    TOOLING = "tooling"
    REFACTOR = "refactor"


class CommitMessage(Model):
    """Formats and parses semantic commit messages"""
    kind: CommitKind
    summary: str
    body: Optional[str] = None
    metadata: dict

    def format(self) -> str:
        """Format as a git commit message"""
        msg = f"{self.kind.value}: {self.summary}"
        if self.body:
            msg += f"\n\n{self.body}"
        msg += f"\n\n{METADATA_SEPARATOR}\n\n{json.dumps(self.metadata, indent=2)}"
        return msg

    @classmethod
    def parse(cls, message: str) -> "CommitMessage":
        """Parse a git commit message into its components"""
        parts = message.split(METADATA_SEPARATOR)
        header = parts[0].strip()
        metadata = json.loads(parts[1].strip()) if len(parts) > 1 else {}
        
        # Parse header
        lines = header.split("\n")
        first_line = lines[0]
        kind_str, summary = first_line.split(":", 1)
        body = "\n".join(lines[1:]).strip() if len(lines) > 1 else None
        
        return cls(
            kind=CommitKind(kind_str.strip()),
            summary=summary.strip(),
            body=body,
            metadata=metadata
        )

    @classmethod
    def from_experiment(cls, experiment: "ExperimentRun") -> "CommitMessage":
        """Create a commit message from an experiment run"""
        return cls(
            kind=CommitKind.EXP,
            summary="Experiment run",  # TODO: Generate better summary
            body="TODO: Generate experiment description",
            metadata=experiment.model_dump(exclude={"summary"})
        )


class Commit(Model):
    """Represents a git commit"""
    sha: str
    message: str
    date: datetime
    kind: Optional[CommitKind]
    metadata: dict

    @staticmethod
    def from_git(commit: git.Commit) -> "Commit":
        message = commit.message if isinstance(commit.message, str) else commit.message.decode()
        commit_msg = CommitMessage.parse(message)
        return Commit(
            sha=commit.hexsha,
            message=message,
            date=commit.committed_datetime,
            kind=commit_msg.kind,
            metadata=commit_msg.metadata,
        )


class StageStrategy(Enum):
    """Strategy for staging files in git"""
    ALL = auto()
