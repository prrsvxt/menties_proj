from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_session, get_transactional_session
from src.mappers.workspace_mapper import WorkspaceMapper
from src.repositories.workspace_repository import WorkspaceRepository
from src.services.workspace_service import WorkspaceService
from src.cache.redis_cache import RedisCache
from src.dependencies.cache_deps import get_redis


def get_workspace_mapper() -> WorkspaceMapper:
    return WorkspaceMapper()


def get_workspace_repository(
        db: AsyncSession = Depends(get_session),
) -> WorkspaceRepository:
    return WorkspaceRepository(db)


def get_transactional_workspace_repository(
        db: AsyncSession = Depends(get_transactional_session),
) -> WorkspaceRepository:
    return WorkspaceRepository(db)


def get_workspace_service(
        repository: WorkspaceRepository = Depends(get_workspace_repository),
        mapper: WorkspaceMapper = Depends(get_workspace_mapper),
        redis: RedisCache = Depends(get_redis),
) -> WorkspaceService:
    return WorkspaceService(repository, mapper, redis)


def get_transactional_workspace_service(
        repository: WorkspaceRepository = Depends(
            get_transactional_workspace_repository,
        ),
        mapper: WorkspaceMapper = Depends(get_workspace_mapper),
        redis: RedisCache = Depends(get_redis),
) -> WorkspaceService:
    return WorkspaceService(repository, mapper, redis)


GetWorkspaceService = Annotated[
    WorkspaceService,
    Depends(get_workspace_service),
]

TransactionalWorkspaceService = Annotated[
    WorkspaceService,
    Depends(get_transactional_workspace_service),
]
