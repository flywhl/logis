import os

from dataclasses import dataclass
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


@dataclass
class Run:
    """Tracks experiment hyperparameters and metrics."""

    _hypers: dict = None
    _metrics: dict = None

    def set_hyperparameters(self, **kwargs) -> None:
        """Set hyperparameters manually."""
        self._hypers = kwargs

    def set_metrics(self, **kwargs) -> None:
        """Set metrics manually."""
        self._metrics = kwargs

    @property
    def hyperparameters(self) -> Optional[dict]:
        return self._hypers

    @property
    def metrics(self) -> Optional[dict]:
        return self._metrics


def commit(
    fn: Optional[Callable] = None,
    *,
    hypers: str = "hypers",
    template: str = "run {experiment}",
    strategy: StageStrategy = StageStrategy.ALL,
    use_context: bool = False,
) -> Callable:
    """Decorator to auto-commit experimental code with scientific metadata.

    Can be used as @commit or @commit(message="Custom message")
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            di = DI()
            run = Run()
            git_service = di[GitService]

            # Run experiment
            metrics = func(*args, run=run, **kwargs)

            # Get experiment data from either the Run object or function args/return
            if run.hyperparameters is not None:
                hyper_dict = run.hyperparameters
            else:
                hyperparameters = cast(BaseModel, kwargs.get(hypers, None))
                if not hyperparameters:
                    raise MthdError("Hyperparameters must be provided either via Run object or function arguments")
                hyper_dict = hyperparameters.model_dump()

            if run.metrics is not None:
                metric_dict = run.metrics
            else:
                if not isinstance(metrics, BaseModel):
                    raise MthdError("Metrics must be provided either via Run object or as BaseModel return value")
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
    def test1(hypers: Hyperparameters, run: Run):
        print("\n<Experiment 1 goes here>\n")
        return Metrics(a=1, b=2.0, c="3")

    # Example using Run object
    @commit
    def test2(run: Run):
        print("\n<Experiment 2 goes here>\n")
        run.set_hyperparameters(a=1, b=2.0, c="3")
        run.set_metrics(a=1, b=2.0, c="3")
        return None

    test1(hypers=Hyperparameters(a=1, b=2.0, c="3"))
    test2()
