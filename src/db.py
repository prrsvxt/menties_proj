from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from fastapi import Request


def create_engine(postgres_url: str) -> AsyncEngine:
    engine: AsyncEngine = create_async_engine(
        str(postgres_url),
        pool_pre_ping=True,
    )

    return engine


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    SessionFactory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    return SessionFactory

async def get_transactional_session(
        request: Request
) -> AsyncGenerator[AsyncSession, None]:

    SessionFactory = request.app.state.session_factory
    
    async with SessionFactory() as session:
        async with session.begin():
            yield session


async def get_session(
        request: Request
) -> AsyncGenerator[AsyncSession, None]:

    SessionFactory = request.app.state.session_factory
    
    async with SessionFactory() as session:
        yield session
