import os

from dataclasses import dataclass
from functools import wraps
from typing import Callable, Concatenate, Literal, Optional, ParamSpec, TypeVar, Union, cast, overload

from pydantic import BaseModel
from rich.console import Console
from rich.padding import Padding

from logis.domain.experiment import ExperimentRun
from logis.domain.git import StageStrategy
from logis.error import LogisError
from logis.service.git import GitService
from logis.util.di import DI


@dataclass
class Run:
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
    def hyperparameters(self) -> dict:
        if not self._hypers:
            raise LogisError("Hyperparameters not set")
        return self._hypers

    @property
    def metrics(self) -> dict:
        if not self._metrics:
            raise LogisError("Hyperparameters not set")
        return self._metrics


P = ParamSpec("P")
R = TypeVar("R")
T = TypeVar("T")


@overload
def commit(
    fn: None = None,
    *,
    hypers: str = "hypers",
    template: str = "run {experiment}",
    strategy: StageStrategy = StageStrategy.ALL,
    implicit: Literal[False] = False,
) -> Callable[[Callable[Concatenate[Run, P], R]], Callable[P, R]]: ...


@overload
def commit(
    fn: None = None,
    *,
    hypers: str = "hypers",
    template: str = "run {experiment}",
    strategy: StageStrategy = StageStrategy.ALL,
    implicit: Literal[True],
) -> Callable[[Callable[P, R]], Callable[P, R]]: ...


@overload
def commit(
    fn: Callable[P, R],
) -> Callable[Concatenate[Run, P], R]: ...


def commit(
    fn: Optional[Callable[..., R]] = None,
    *,
    hypers: str = "hypers",
    template: str = "run {experiment}",
    strategy: StageStrategy = StageStrategy.ALL,
    implicit: bool = False,
) -> Union[Callable[[Callable[..., R]], Callable[..., R]], Callable[..., R]]:
    """Decorator to auto-commit experimental code with scientific metadata.

    Can be used as @commit or @commit(message="Custom message")
    """

    def decorator(func: Callable[..., R]) -> Callable[..., R]:
        @wraps(func)
        def wrapper(*args, **kwargs):
            di = DI()
            git_service = di[GitService]
            run = Run()

            if not implicit:
                args = [run] + list(args)
                metrics = func(*args, **kwargs)

                if run.hyperparameters is None:
                    raise LogisError("When using context, hyperparameters must be set via the Context object")
                if run.metrics is None:
                    raise LogisError("When using context, metrics must be set via the Context object")
            else:
                metrics = func(*args, **kwargs)

                hyperparameters = cast(BaseModel, kwargs.get(hypers, None))
                if not hyperparameters:
                    raise LogisError("When not using context, hyperparameters must be provided as function arguments")
                if not isinstance(metrics, BaseModel):
                    raise LogisError("When not using context, metrics must be returned as a BaseModel")

                run.set_hyperparameters(hyperparameters.model_dump())
                run.set_metrics(metrics.model_dump())

            experiment = ExperimentRun(
                experiment=func.__name__,
                hyperparameters=run.hyperparameters,
                metrics=run.metrics,
            )
            message = experiment.as_commit_message(template=template)

            # Commit changes
            if git_service.should_commit(strategy):
                console = Console()
                console.print("Generating commit with message:\n")
                console.print(Padding(message.render(), pad=(0, 0, 0, 4)))  # Indent by 4 spaces.
                if os.getenv("LOGIS_DRY_RUN") == "1":
                    console.print("\nDry run enabled. Not committing changes.")
                else:
                    git_service.stage_and_commit(message.render())

            return metrics

        return wrapper

    if fn is None:
        return decorator
    return decorator(fn)


if __name__ == "__main__":
    os.environ["LOGIS_DRY_RUN"] = "1"

    class Hyperparameters(BaseModel):
        a: int
        b: float
        c: str

    class Metrics(BaseModel):
        a: int
        b: float
        c: str

    # Example using function arguments/return
    @commit(hypers="hypers", implicit=True, template="run {experiment} at {timestamp}")
    def test1(hypers: Hyperparameters):
        print("\n<Experiment 1 goes here>\n")
        return Metrics(a=1, b=2.0, c="3")

    # Example using Context object
    @commit()
    def test2(run: Run, foo: int):
        print("\n<Experiment 2 goes here>\n")
        run.set_hyperparameters({"a": 1, "b": 2.0, "c": "3"})
        run.set_metrics({"a": 1, "b": 2.0, "c": "3"})

    test1(hypers=Hyperparameters(a=1, b=2.0, c="3"))
    test2(5)  # No need to pass context
