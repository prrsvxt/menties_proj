from src.UoW.abstract_UoW import AbstractUnitOfWork
from src.repositories.project_repository import ProjectRepository


class ProjectUoW(AbstractUnitOfWork):
    def __init__(self, session_factory):
        super().__init__(session_factory)

    def init_repositories(self):
        self.project_repository = ProjectRepository(self.session)