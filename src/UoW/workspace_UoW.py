from src.UoW.abstract_UoW import AbstractUnitOfWork
from src.repositories.workspace_repository import WorkspaceRepository


class WorkspaceUoW(AbstractUnitOfWork):
    def __init__(self, session_factory):
        super().__init__(session_factory)

    def init_repositories(self):
        self.workspace_repository = WorkspaceRepository(self.session)