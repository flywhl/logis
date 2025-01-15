from dishka import Provider, Scope, make_container

from mthd.service.experiment import ExperimentService
from mthd.service.git import GitService
from mthd.service.repository import RepositoryService


class DI:
    def __init__(self):
        self._container = make_container(self.services)

    @property
    def container(self):
        return self._container

    @property
    def core(self) -> Provider: ...

    @property
    def services(self) -> Provider:
        provider = Provider(scope=Scope.APP)
        provider.provide(GitService)
        provider.provide(RepositoryService)
        provider.provide(ExperimentService)

        return provider
