import os

from functools import wraps
from typing import Callable, Optional, cast

from pydantic import BaseModel
from rich.console import Console
from rich.padding import Padding

from mthd.domain.experiment import ExperimentRun
from mthd.domain.git import StageStrategy
from mthd.error import MthdError
from mthd.service.git import GitService
from mthd.util.di import DI


def commit(
    fn: Optional[Callable] = None,
    *,
    hypers: str = "hypers",
    template: str = "run {experiment}",
    strategy: StageStrategy = StageStrategy.ALL,
) -> Callable:
    """Decorator to auto-commit experimental code with scientific metadata.

    Can be used as @commit or @commit(message="Custom message")
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            di = DI()
            # @todo: handle this better (eg. positional args)
            hyperparameters = cast(BaseModel, kwargs.get(hypers, None))
            if not hyperparameters:
                raise MthdError("Hyperparameters must be provided in the function call.")
            git_service = di[GitService]
            # codebase_service = di[CodebaseService]

            # Generate commit message

            # Run experiment
            metrics = func(*args, **kwargs)

            experiment = ExperimentRun(
                experiment=func.__name__,
                hyperparameters=hyperparameters.model_dump(),
                metrics=metrics.model_dump(),
                # annotations=codebase_service.get_all_annotations(),
            )
            message = experiment.as_commit_message(template=template)

            # Commit changes
            if git_service.should_commit(strategy):
                console = Console()
                console.print("Generating commit with message:\n")
                console.print(Padding(message.render(), pad=(0, 0, 0, 4)))  # Indent by 4 spaces.
                if os.getenv("MTHD_DRY_RUN") == "1":
                    console.print("\nDry run enabled. Not committing changes.")
                else:
                    git_service.stage_and_commit(message.render())

            return metrics

        return wrapper

    if fn is None:
        return decorator
    return decorator(fn)


if __name__ == "__main__":
    os.environ["MTHD_DRY_RUN"] = "1"

    class Hyperparameters(BaseModel):
        a: int
        b: float
        c: str

    class Metrics(BaseModel):
        a: int
        b: float
        c: str

    @commit(hypers="hypers", template="run {experiment} at {timestamp}")
    def test(hypers: Hyperparameters):
        print("\n<Experiment goes here>\n")
        return Metrics(a=1, b=2.0, c="3")

    test(hypers=Hyperparameters(a=1, b=2.0, c="3"))
