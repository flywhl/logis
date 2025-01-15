from functools import wraps

from typing import Callable, Optional

from mthd.domain.commit import CommitMessage
from mthd.domain.repository import Repository
from mthd.service.repository import RepositoryService
from mthd.util.di import DI


def commit(fn: Optional[Callable] = None) -> Callable:
    """Decorator to auto-commit experimental code with scientific metadata.

    Can be used as @commit or @commit(message="Custom message")
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            repository_service = DI().container.get(RepositoryService)
            # Set up services

            # Generate commit message
            commit_msg = CommitMessage(
                summary=f"Experiment: {func.__name__}",
                parameters=...,  # exp_service.extract_parameters(func, args, kwargs),
                annotations=...,  # exp_service.extract_annotations(),
            )

            # Run experiment
            result = func(*args, **kwargs)

            # Commit changes
            repository_service.commit_changes(commit_msg)

            return result

        return wrapper

    if fn is None:
        return decorator
    return decorator(fn)


if __name__ == "__main__":

    @commit
    def test():
        print("Hello")

    test()
