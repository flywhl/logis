import json

from datetime import datetime
from enum import StrEnum
from typing import Optional

from mthd.config import METADATA_SEPARATOR
from mthd.util.model import Model


class ExperimentRun(Model):
    """Represents a single run of an experiment"""

    hyperparameters: dict
    metrics: dict
    artifacts: Optional[dict] = None  # Any generated files/data
    annotations: Optional[dict] = None
    timestamp: datetime = datetime.now()

    def as_commit_message(self) -> str:
        """Formats the experiment run as a semantic commit message"""
        return str(CommitMessage.from_experiment(self))

    @staticmethod
    def parse(message: str) -> "ExperimentRun":
        """Parse an experiment run from a commit message"""
        commit_msg = CommitMessage.parse(message)
        return ExperimentRun(**commit_msg.metadata)


class CommitKind(StrEnum):
    """Types of semantic commits"""

    EXP = "exp"
    FIX = "fix"
    FEAT = "feat"
    CHORE = "chore"
    TOOLING = "tooling"
    REFACTOR = "refactor"

    @staticmethod
    def from_header(header: str) -> Optional["CommitKind"]:
        """Parse a commit kind from a header string"""
        try:
            kind = header.split(":")[0].strip()
            return CommitKind(kind)
        except Exception:
            return None


class CommitMessage(Model):
    """Formats and parses semantic commit messages"""

    kind: CommitKind
    summary: str
    body: Optional[str] = None
    metadata: dict

    def __str__(self) -> str:
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

        return cls(kind=CommitKind(kind_str.strip()), summary=summary.strip(), body=body, metadata=metadata)

    @classmethod
    def from_experiment(cls, experiment: ExperimentRun) -> "CommitMessage":
        """Create a commit message from an experiment run"""
        return cls(
            kind=CommitKind.EXP,
            summary="experiment run",  # TODO: Generate better summary
            body="TODO: Generate experiment description",
            metadata=experiment.model_dump(exclude={"summary"}),
        )
