import pytest
from redis import asyncio as redis
import pytest_asyncio
from testcontainers.community.postgres import PostgresContainer
from testcontainers.community.redis import RedisContainer
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from httpx import ASGITransport, AsyncClient
from alembic import command
from alembic.config import Config
import asyncio
import os


from src.cache.redis_cache import RedisCache
from src.application import get_app
from src.dependencies.cache_deps import get_redis
from src.dependencies.project_deps import get_project_unit_of_work
from src.dependencies.users_deps import get_user_unit_of_work
from src.dependencies.workspace_deps import get_workspace_uow
from src.UoW.project_UoW import ProjectUoW
from src.UoW.user_UoW import UserUoW
from src.UoW.workspace_UoW import WorkspaceUoW

@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def async_postgres():
    """Start PostgreSQL for async tests"""
    with PostgresContainer("postgres:14") as postgres:
        yield postgres

@pytest_asyncio.fixture(scope='session', loop_scope='session')
async def run_migrations(async_postgres):
    database_url = (
        f"postgresql+asyncpg://"
        f"{async_postgres.username}:{async_postgres.password}"
        f"@{async_postgres.get_container_host_ip()}:"
        f"{async_postgres.get_exposed_port(5432)}/"
        f"{async_postgres.dbname}"
    )

    database_old_url = os.environ.get('POSTGRES_URL')
    os.environ['POSTGRES_URL'] = database_url

    try:
        alembic_config = Config('alembic.ini')
        await asyncio.to_thread(
            command.upgrade,
            alembic_config,
            'head',
        )
    finally:
        if database_old_url is None:
            os.environ.pop('POSTGRES_URL', None)
        else:
            os.environ['POSTGRES_URL'] = database_old_url

@pytest_asyncio.fixture(scope="function", loop_scope="function")
async def session_factory(async_postgres, run_migrations):
    database_url = (
        f"postgresql+asyncpg://"
        f"{async_postgres.username}:{async_postgres.password}"
        f"@{async_postgres.get_container_host_ip()}:"
        f"{async_postgres.get_exposed_port(5432)}/"
        f"{async_postgres.dbname}"
    )

    engine = create_async_engine(database_url)

    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    yield session_factory

    await engine.dispose()


@pytest_asyncio.fixture(scope='function', loop_scope='function', autouse=True)
async def clean_database(session_factory):
    async with session_factory() as session:
        await session.execute(text(
            'TRUNCATE TABLE access_grant, project_tag, tags, projects, '
            'workspace_settings, workspaces, users RESTART IDENTITY CASCADE'
        ))
        await session.commit()


@pytest_asyncio.fixture(scope='function', loop_scope='function')
async def async_session(async_postgres, run_migrations):
    database_url = (
        f"postgresql+asyncpg://"
        f"{async_postgres.username}:{async_postgres.password}"
        f"@{async_postgres.get_container_host_ip()}:"
        f"{async_postgres.get_exposed_port(5432)}/"
        f"{async_postgres.dbname}"
    )

    engine = create_async_engine(database_url)

    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with session_factory() as session:
        async with session.begin():
            yield session

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
async def app(session_factory, redis_cache):
    app = get_app()

    def override_get_project_uow():
        return ProjectUoW(session_factory)

    def override_get_workspace_uow():
        return WorkspaceUoW(session_factory)

    def override_get_user_uow():
        return UserUoW(session_factory)

    async def override_get_redis():
        return redis_cache

    app.dependency_overrides[get_project_unit_of_work] = override_get_project_uow
    app.dependency_overrides[get_workspace_uow] = override_get_workspace_uow
    app.dependency_overrides[get_user_unit_of_work] = override_get_user_uow
    app.dependency_overrides[get_redis] = override_get_redis

    yield app

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope='function', loop_scope='function')
async def client(app):
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url='http://test') as client:
        yield client
