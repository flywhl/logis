from enum import Enum, auto

from mthd.util.model import Model


class CommitMessage(Model):
    summary: str
    hyperparameters: dict
    # annotations: set[Annotation]  # @todo: fix anot

    def format(self) -> str:
        return (
            f"{self.summary}\n\n{self.model_dump_json(indent=2, exclude={'summary'})}"
        )


class StageStrategy(Enum):
    ALL = auto()
