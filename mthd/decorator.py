import os

from dataclasses import dataclass
from functools import wraps
from typing import Callable, Optional, ParamSpec, TypeVar, cast

from pydantic import BaseModel
from rich.console import Console
from rich.padding import Padding

from mthd.domain.experiment import ExperimentRun
from mthd.domain.git import StageStrategy
from mthd.error import MthdError
from mthd.service.git import GitService
from mthd.util.di import DI


@dataclass
class Context:
    """Tracks experiment hyperparameters and metrics."""

    _hypers: Optional[dict] = None
    _metrics: Optional[dict] = None

    def set_hyperparameters(self, hypers: dict) -> None:
        """Set hyperparameters manually."""
        self._hypers = hypers

    def set_metrics(self, metrics: dict) -> None:
        """Set metrics manually."""
        self._metrics = metrics

    @property
    def hyperparameters(self) -> Optional[dict]:
        return self._hypers

    @property
    def metrics(self) -> Optional[dict]:
        return self._metrics


P = ParamSpec("P")
R = TypeVar("R")
T = TypeVar("T")

def commit(
    fn: Optional[Callable[..., R]] = None,
    *,
    hypers: str = "hypers",
    template: str = "run {experiment}",
    strategy: StageStrategy = StageStrategy.ALL,
    use_context: bool = False,
) -> Callable[..., R]:
    """Decorator to auto-commit experimental code with scientific metadata.

    Can be used as @commit or @commit(message="Custom message")
    """

    def decorator(func: Callable[..., R]) -> Callable[..., R]:
        @wraps(func)
        def wrapper(*args, **kwargs):
            di = DI()
            git_service = di[GitService]

            if use_context:
                run = Context()
                metrics = func(*args, run=run, **kwargs)

                if run.hyperparameters is None:
                    raise MthdError("When using context, hyperparameters must be set via the Run object")
                if run.metrics is None:
                    raise MthdError("When using context, metrics must be set via the Run object")

                hyper_dict = run.hyperparameters
                metric_dict = run.metrics
            else:
                metrics = func(*args, **kwargs)

                hyperparameters = cast(BaseModel, kwargs.get(hypers, None))
                if not hyperparameters:
                    raise MthdError("When not using context, hyperparameters must be provided as function arguments")
                if not isinstance(metrics, BaseModel):
                    raise MthdError("When not using context, metrics must be returned as a BaseModel")

                hyper_dict = hyperparameters.model_dump()
                metric_dict = metrics.model_dump()

            experiment = ExperimentRun(
                experiment=func.__name__,
                hyperparameters=hyper_dict,
                metrics=metric_dict,
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

    # Example using function arguments/return
    @commit(hypers="hypers", template="run {experiment} at {timestamp}")
    def test1(hypers: Hyperparameters):
        print("\n<Experiment 1 goes here>\n")
        return Metrics(a=1, b=2.0, c="3")

    # Example using Run context object
    @commit(use_context=True)
    def test2(context: Context):
        print("\n<Experiment 2 goes here>\n")
        context.set_hyperparameters({"a": 1, "b": 2.0, "c": "3"})
        context.set_metrics({"a": 1, "b": 2.0, "c": "3"})

    test1(hypers=Hyperparameters(a=1, b=2.0, c="3"))
    test2()
