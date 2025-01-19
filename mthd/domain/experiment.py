from datetime import datetime
from typing import Optional

from mthd.config import METADATA_SEPARATOR
from mthd.util.model import Model


class ExperimentResult(Model):
    """Represents the outcome of an experiment run"""
    metrics: dict
    artifacts: Optional[dict] = None  # Any generated files/data


class ExperimentRun(Model):
    """Represents a single run of an experiment"""
    hyperparameters: dict
    metrics: Optional[dict] = None  # Results/metrics from the run
    annotations: Optional[dict] = None  # Code annotations/metadata
    timestamp: datetime = datetime.now()
    
    def record_results(self, metrics: dict, artifacts: Optional[dict] = None) -> None:
        """Record the results of this experiment run"""
        self.metrics = metrics
        if artifacts:
            self.artifacts = artifacts

    def as_commit_message(self) -> str:
        """Formats the experiment run as a semantic commit message"""
        from mthd.domain.git import CommitMessage
        return CommitMessage.from_experiment(self).format()

    @staticmethod
    def parse(message: str) -> "ExperimentRun":
        """Parse an experiment run from a commit message"""
        from mthd.domain.git import CommitMessage
        commit_msg = CommitMessage.parse(message)
        return ExperimentRun(**commit_msg.metadata)
