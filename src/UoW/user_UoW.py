from src.UoW.abstract_UoW import AbstractUnitOfWork
from src.repositories.user_repository import UserRepository


class UserUoW(AbstractUnitOfWork):
    def __init__(self, session_factory):
        super().__init__(session_factory)

    def init_repositories(self):
        self.user_repository = UserRepository(self.session)