from typing import Type, TypeVar

from dishka import Provider, Scope, make_container, provide
from git import Repo

from mthd.service.codebase import CodebaseService
from mthd.service.experiment import ExperimentService
from mthd.service.git import GitService
from mthd.service.query import QueryService

T = TypeVar("T")


class GitProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_repo(self) -> Repo:
        try:
            return Repo()
        except Exception as e:
            print(e)
            raise RuntimeError(f"Failed to initialize Git repository: {e}")


class DI:
    def __init__(self):
        self._container = make_container(self.services, self.git)

    @property
    def container(self):
        return self._container

    @property
    def core(self) -> Provider: ...

    @property
    def git(self) -> Provider:
        return GitProvider()

    @property
    def services(self) -> Provider:
        provider = Provider(scope=Scope.APP)
        provider.provide(GitService)
        provider.provide(ExperimentService)
        provider.provide(CodebaseService)
        provider.provide(QueryService)

        return provider

    def __getitem__(self, item: Type[T]) -> T:
        return self._container.get(item)
