from typing import Annotated

from fastapi import Depends, Request

from src.mappers.workspace_mapper import WorkspaceMapper
from src.services.workspace_service import WorkspaceService
from src.cache.redis_cache import RedisCache
from src.dependencies.cache_deps import get_redis
from src.UoW.workspace_UoW import WorkspaceUoW


def get_workspace_mapper() -> WorkspaceMapper:
    return WorkspaceMapper()

def get_workspace_uow(request: Request) -> WorkspaceUoW:
    session_factory = request.app.state.session_factory
    return WorkspaceUoW(session_factory)


def get_workspace_service(
        unit_of_work: WorkspaceUoW = Depends(get_workspace_uow),
        mapper: WorkspaceMapper = Depends(get_workspace_mapper),
        redis: RedisCache = Depends(get_redis),
) -> WorkspaceService:
    return WorkspaceService(unit_of_work, mapper, redis)


GetWorkspaceService = Annotated[
    WorkspaceService,
    Depends(get_workspace_service),
]
