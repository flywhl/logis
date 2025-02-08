import json
import logging

from datetime import datetime
from enum import StrEnum
from typing import Any, Optional
from uuid import uuid4

from pydantic import UUID4, Field

from mthd.config import BODY_METADATA_SEPARATOR, SUMMARY_BODY_SEPARATOR
from mthd.domain.git import Commit
from mthd.util.model import Model

logger = logging.getLogger(__name__)


class ExperimentRun(Model):
    """The core data from an experiment run"""

    experiment: str
    hyperparameters: dict
    metrics: dict
    uuid: UUID4 = Field(default_factory=uuid4)
    artifacts: Optional[dict] = None  # Any generated files/data
    annotations: Optional[dict] = None
    timestamp: datetime = datetime.now()

    def as_commit_message(self, template: str) -> "SemanticMessage":
        """Convert this experiment run into a commit"""
        return SemanticMessage(
            kind=CommitKind.EXP,
            summary=template.format(**self.model_dump(include={"experiment", "timestamp"})),
            metadata=self.model_dump(mode="json"),
        )

    @staticmethod
    def from_commit(commit: Commit) -> Optional["ExperimentRun"]:
        message = SemanticMessage.from_commit(commit)
        # if not message:
        #     # @todo: is :20s the right syntax to truncate?
        #     logger.debug(f"Could not parse semantic message: '{commit.message:.20s}'")
        #     return None

        return ExperimentRun.model_validate(message.metadata)


class CommitKind(StrEnum):
    """Types of semantic commits"""

    EXP = "exp"
    FIX = "fix"
    FEAT = "feat"
    CHORE = "chore"
    TOOLING = "tooling"
    REFACTOR = "refactor"

    @property
    def has_metadata(self) -> bool:
        return self is CommitKind.EXP

    @staticmethod
    def from_header(header: str) -> Optional["CommitKind"]:
        """Parse a commit kind from a header string"""
        try:
            kind = header.split(":")[0].strip()
            return CommitKind(kind)
        except Exception:
            return None


class SemanticMessage(Model):
    """Base class for our semantic commit formats"""

    kind: CommitKind
    summary: str
    body: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None

    def render(self, with_metadata: bool = False) -> str:
        msg = f"{self.kind.value}: {self.summary}"
        if self.body:
            msg += f"\n\n{self.body}"
        if with_metadata and self.metadata:
            msg += f"\n\n{BODY_METADATA_SEPARATOR}\n\n{json.dumps(self.metadata, indent=2)}"
        return msg

    @classmethod
    def from_commit(cls, commit: Commit) -> "SemanticMessage":
        kind, summary, body, metadata = cls._parse_semantic_parts(commit)

        return cls(kind=kind, summary=summary.strip(), body=body, metadata=metadata)

    @staticmethod
    def _parse_semantic_parts(commit: Commit) -> tuple[CommitKind, str, Optional[str], Optional[dict]]:
        # we only want to split on the first separator
        parts = commit.message.split(SUMMARY_BODY_SEPARATOR, maxsplit=1)
        header = parts[0]
        kind_str, summary = header.split(":", 1)
        kind = CommitKind(kind_str)

        if len(parts) == 2:
            body = parts[1]
            if kind.has_metadata:
                body, raw_metadata = body.split(BODY_METADATA_SEPARATOR)
                metadata = json.loads(raw_metadata)
                assert isinstance(metadata, dict)
            else:
                metadata = None
        else:
            body = metadata = None

        return kind, summary, body, metadata
