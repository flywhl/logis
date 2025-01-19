import json

from mthd.config import METADATA_SEPARATOR
from mthd.domain.git import CommitKind
from mthd.util.model import Model


class ExperimentState(Model):
    hyperparameters: dict
    # annotations: set[Annotation]  # @todo: fix anot

    def as_commit_message(self) -> str:
        return f"{self.summary}\n\n{self.body}\n\n{METADATA_SEPARATOR}\n\n{self.model_dump_json(indent=2, exclude={'summary'})}"

    @property
    def summary(self) -> str:
        return f"{CommitKind.EXP.value}: TODO"

    @property
    def body(self) -> str:
        return "TODO"

    @staticmethod
    def parse(message: str) -> "ExperimentState":
        # @todo: test this
        metadata = message.split(METADATA_SEPARATOR)[1].strip()
        return ExperimentState(hyperparameters=json.loads(metadata))
