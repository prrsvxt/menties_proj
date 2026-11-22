from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_session, get_transactional_session
from src.mappers.project_mapper import ProjectMapper
from src.repositories.project_repository import ProjectRepository
from src.services.project_service import ProjectService
from src.cache.redis_cache import RedisCache
from src.dependencies.cache_deps import get_redis


def get_project_mapper() -> ProjectMapper:
    return ProjectMapper()


def get_project_repository(
        db: AsyncSession = Depends(get_session),
) -> ProjectRepository:
    return ProjectRepository(db)


def get_transactional_project_repository(
        db: AsyncSession = Depends(get_transactional_session),
) -> ProjectRepository:
    return ProjectRepository(db)


def get_project_service(
        project_repository: ProjectRepository = Depends(get_project_repository),
        mapper: ProjectMapper = Depends(get_project_mapper),
        redis: RedisCache = Depends(get_redis),
) -> ProjectService:
    return ProjectService(project_repository, mapper, redis)


def get_transactional_project_service(
        project_repository: ProjectRepository = Depends(
            get_transactional_project_repository,
        ),
        mapper: ProjectMapper = Depends(get_project_mapper),
        redis: RedisCache = Depends(get_redis),
) -> ProjectService:
    return ProjectService(project_repository, mapper, redis)


GetProjectService = Annotated[
    ProjectService,
    Depends(get_project_service),
]

TransactionalProjectService = Annotated[
    ProjectService,
    Depends(get_transactional_project_service),
]
