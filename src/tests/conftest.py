import pytest
from redis import asyncio as redis
import pytest_asyncio
from testcontainers.community.postgres import PostgresContainer
from testcontainers.community.redis import RedisContainer
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from httpx import ASGITransport, AsyncClient


from src.models.base import Base
from src.cache.redis_cache import RedisCache
from src.application import get_app
from src.db import get_session, get_transactional_session
from src.dependencies.cache_deps import get_redis

@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def async_postgres():
    """Start PostgreSQL for async tests"""
    with PostgresContainer("postgres:14") as postgres:
        yield postgres

@pytest_asyncio.fixture(scope="function", loop_scope="function")
async def async_session(async_postgres):
    database_url = (
        f"postgresql+asyncpg://"
        f"{async_postgres.username}:{async_postgres.password}"
        f"@{async_postgres.get_container_host_ip()}:"
        f"{async_postgres.get_exposed_port(5432)}/"
        f"{async_postgres.dbname}"
    )

    engine = create_async_engine(database_url)

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with session_factory() as session:
        yield session
        await session.rollback()

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)

    await engine.dispose()

@pytest_asyncio.fixture(scope='session', loop_scope='session')
async def async_redis():
    with RedisContainer('redis:7-alpine') as redis:
        yield redis


@pytest_asyncio.fixture(scope='function', loop_scope='function')
async def redis_cache(async_redis):
    redis_url = (
        f"redis://"
        f"{async_redis.get_container_host_ip()}:"
        f"{async_redis.get_exposed_port(6379)}"
    )
    redis_client = redis.from_url(redis_url)

    cache = RedisCache(redis_client=redis_client, ttl=3600)

    await redis_client.flushdb()

    yield cache

    await redis_client.flushdb()
    await cache.close()


@pytest_asyncio.fixture(scope='function', loop_scope='function')
async def app(async_session, redis_cache):
    app = get_app()

    async def override_get_session():
        yield async_session

    async def override_get_transactional_session():
        async with async_session.begin():
            yield async_session

    async def override_get_redis():
        return redis_cache

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_transactional_session] = override_get_transactional_session
    app.dependency_overrides[get_redis] = override_get_redis

    yield app

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope='function', loop_scope='function')
async def client(app):
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url='http://test') as client:
        yield client