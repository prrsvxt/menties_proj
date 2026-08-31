from collections.abc import AsyncGenerator
import logging
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from src.config import Settings

logger = logging.getLogger(__name__)

try:
    settings = Settings()
except Exception:
    logger.exception('Couldn\'t read settings config')
    raise

engine: AsyncEngine = create_async_engine(
    str(settings.postgres_url),
    pool_pre_ping=True,
)

SessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_transactional_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionFactory() as session:
        async with session.begin():
            yield session

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionFactory() as session:
        yield session
