from typing import Annotated

from fastapi import Depends, Request

from src.mappers.project_mapper import ProjectMapper
from src.services.project_service import ProjectService
from src.cache.redis_cache import RedisCache
from src.dependencies.cache_deps import get_redis
from src.UoW.project_UoW import ProjectUoW  


def get_project_mapper() -> ProjectMapper:
    return ProjectMapper()


def get_project_unit_of_work(
        request: Request
) -> ProjectUoW:
    session_factory = request.app.state.session_factory
    return ProjectUoW(session_factory)


def get_project_service(
        unit_of_work: ProjectUoW = Depends(get_project_unit_of_work),
        mapper: ProjectMapper = Depends(get_project_mapper),
        redis: RedisCache = Depends(get_redis),
) -> ProjectService:
    return ProjectService(unit_of_work, mapper, redis)


GetProjectService = Annotated[
    ProjectService,
    Depends(get_project_service),
]
