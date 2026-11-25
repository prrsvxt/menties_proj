from abc import ABC, abstractmethod


class AbstractUnitOfWork(ABC):
    def __init__(self, session_factory):
        self.session_factory = session_factory
        self.session = None

    async def __aenter__(self):
        self.session = self.session_factory()
        await self.session.begin()
        self.init_repositories()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        try:
            if exc_type is not None:
                await self.session.rollback()
            else:
                await self.session.commit()
        finally:
            await self.session.close()

    @abstractmethod
    def init_repositories(self):
        raise NotImplementedError()