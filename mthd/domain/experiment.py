import json
from datetime import datetime
from typing import Literal, Optional

from mthd.config import METADATA_SEPARATOR
from mthd.domain.change_type import ChangeType
from mthd.util.model import Model


class ExperimentRun(Model):
    """The core data from an experiment run"""
    hyperparameters: dict
    metrics: Optional[dict] = None
    artifacts: Optional[dict] = None  # Any generated files/data
    annotations: Optional[dict] = None
    timestamp: datetime = datetime.now()


class SemanticCommit(Model):
    """Base class for our semantic commit formats"""
    type: ChangeType
    summary: str
    body: Optional[str] = None

    def format_message(self) -> str:
        msg = f"{self.type.value}: {self.summary}"
        if self.body:
            msg += f"\n\n{self.body}"
        return msg


class ExperimentCommit(SemanticCommit):
    """A commit specifically representing an experiment run"""
    type: Literal[ChangeType.EXPERIMENT]  # Must be EXPERIMENT
    experiment: ExperimentRun

    def format_message(self) -> str:
        msg = super().format_message()
        msg += f"\n\n{METADATA_SEPARATOR}\n\n{json.dumps(self.experiment.model_dump(), indent=2)}"
        return msg

    @classmethod
    def parse(cls, message: str) -> "ExperimentCommit":
        """Parse a git commit message into an ExperimentCommit"""
        parts = message.split(METADATA_SEPARATOR)
        if len(parts) != 2:
            raise ValueError("Invalid experiment commit - missing metadata section")
            
        header = parts[0].strip()
        lines = header.split("\n")
        first_line = lines[0]
        type_str, summary = first_line.split(":", 1)
        
        if ChangeType(type_str.strip()) != ChangeType.EXPERIMENT:
            raise ValueError("Invalid experiment commit - wrong type")
            
        body = "\n".join(lines[1:]).strip() if len(lines) > 1 else None
        metadata = json.loads(parts[1].strip())
        experiment = ExperimentRun(**metadata)

        return cls(
            type=ChangeType.EXPERIMENT,
            summary=summary.strip(),
            body=body,
            experiment=experiment
        )
