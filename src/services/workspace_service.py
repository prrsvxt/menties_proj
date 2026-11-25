from uuid import UUID
from redis.exceptions import RedisError
import logging

from src.exceptions.general_errors import NotFoundError
from src.repositories.workspace_repository import WorkspaceRepository
from src.schemas.workspace import (
    WorkspaceCreate, 
    WorkspaceResponse, 
    WorkspaceUpdate,
    WorkspacePaginationResponse
)
from src.models.workspace import WorkspaceModel
from src.mappers.workspace_mapper import WorkspaceMapper
from src.services.service import Service
from src.cache.redis_cache import RedisCache
from src.UoW.workspace_UoW import WorkspaceUoW

logger = logging.getLogger(__name__)

class WorkspaceService(Service):
    CACHE_VERSION = 'v1'
    WORKSPACES_LIST_VERSION_KEY = 'workspaces:list:version'

    def __init__(self, unit_of_work: WorkspaceUoW, mapper: WorkspaceMapper, redis: RedisCache):
        self.unit_of_work = unit_of_work
        self.mapper = mapper
        self.redis = redis

    @classmethod
    def workspace_key(cls, workspace_id: UUID) -> str:
        return f'{cls.CACHE_VERSION}:workspace:{workspace_id}'

    @classmethod
    def workspace_list_version(
            cls,
            version: int,
            limit: int,
            cursor: str | None,
    ) -> str:
        page = cursor if cursor else 'first'
        return f'{cls.CACHE_VERSION}:workspaces:list:v{version}:limit{limit}:{page}'

    async def _get_workspace_by_id(self, workspace_id: UUID) -> WorkspaceModel:

        async with self.unit_of_work as uow:
            workspace = await uow.workspace_repository.get_workspace_by_id(workspace_id)

        if workspace is None:
            raise NotFoundError(f'Workspace with id={workspace_id} not found.')

        return workspace

    async def get_workspace_by_id(self, workspace_id: UUID) -> WorkspaceResponse:

        try:
            cached_workspace = await self.redis.get(self.workspace_key(workspace_id))
        except RedisError:
            logger.exception(f'Redis error occured at {__name__}, method: redis.get')
            cached_workspace = None

        if cached_workspace:
            return WorkspaceResponse.model_validate_json(cached_workspace)
        
        workspace = await self._get_workspace_by_id(workspace_id)
        workspace_response = self.mapper.workspace_response_map(workspace)
        try:
            await self.redis.set(
                self.workspace_key(workspace_id),
                workspace_response.model_dump_json()
            )
        except RedisError:
            logger.exception(f'Redis error occured at {__name__}, method: redis.set')
        return workspace_response

    async def list_workspaces(
            self,
            limit: int,
            cursor: str | None, 
    ) -> WorkspacePaginationResponse:
        cursor_workspace_id, cursor_timestamp = None, None
        if cursor:
            cursor_workspace_id, cursor_timestamp = self.cursor_decode(cursor)

        cache_version = await self.redis.get_list_version(self.WORKSPACES_LIST_VERSION_KEY)

        if cache_version:
            try:
                cached_data = await self.redis.get(
                    self.workspace_list_version(cache_version, limit, cursor)
                )
            except RedisError:
                logger.exception(f'Redis error occured at {__name__}, method: redis.get')
                cached_data = None

            if cached_data:
                return WorkspacePaginationResponse.model_validate_json(cached_data)


        async with self.unit_of_work as uow:
            workspaces = await uow.workspace_repository.get_paginated_workspaces(
                limit=limit,
                cursor_workspace_id=cursor_workspace_id,
                cursor_timestamp=cursor_timestamp,
            )

        next_cursor = None
        if len(workspaces) > limit:
            last_workspace = workspaces[limit - 1]
            workspaces = workspaces[:limit]
            next_cursor = self.cursor_encode(last_workspace)

        workspaces_pagination_response = self.mapper.workspace_pagination_response_map(workspaces, next_cursor)

        if cache_version:
            try:
                await self.redis.set(
                    self.workspace_list_version(cache_version, limit, cursor),
                    workspaces_pagination_response.model_dump_json()
                )
            except RedisError:
                logger.exception(f'Redis error occured at {__name__}, method: redis.set')

        return workspaces_pagination_response
    
    async def create_workspace(self, data: WorkspaceCreate) -> WorkspaceResponse:
        workspace_data = self.mapper.workspace_create_map(data)
        async with self.unit_of_work as uow:
            workspace = await uow.workspace_repository.create_workspace(workspace_data)
        workspace_response = self.mapper.workspace_response_map(workspace)
        try:
            await self.redis.set(
                self.workspace_key(workspace.id),
                workspace_response.model_dump_json()
            )
        except RedisError:
            logger.exception(f'Redis error occured at {__name__}, method: redis.set')

        try:
            await self.redis.incr(self.WORKSPACES_LIST_VERSION_KEY)
        except RedisError:
            logger.exception(f'Redis error occured at {__name__}, method: redis.incr')
        return workspace_response

    async def delete_workspace(self, workspace_id: UUID) -> None:
        async with self.unit_of_work as uow:
            workspace = await uow.workspace_repository.get_workspace_by_id(workspace_id)
            if workspace:
                await uow.workspace_repository.delete_workspace(workspace)
        try:
            await self.redis.delete([self.workspace_key(workspace_id)])
        except RedisError:
            logger.exception(f'Redis error occured at {__name__}, method: redis.delete')

        try:
            await self.redis.incr(self.WORKSPACES_LIST_VERSION_KEY)
        except RedisError:
            logger.exception(f'Redis error occured at {__name__}, method: redis.incr')

    async def update_workspace(
            self,
            workspace_id: UUID,
            data: WorkspaceUpdate,
    ) -> WorkspaceResponse:

        async with self.unit_of_work as uow:
            workspace = await uow.workspace_repository.get_workspace_with_lock(workspace_id)

            if workspace is None:
                raise NotFoundError(f'Workspace with id={workspace_id} not found.')

            workspace = self.mapper.workspace_update_map(data, workspace)
            workspace = await uow.workspace_repository.update_workspace(workspace)

        workspace_response = self.mapper.workspace_response_map(workspace)
        try:
            await self.redis.set(
                self.workspace_key(workspace_id),
                workspace_response.model_dump_json()
            )
        except RedisError:
            logger.exception(f'Redis error occured at {__name__}, method: redis.set')

        try:
            await self.redis.incr(self.WORKSPACES_LIST_VERSION_KEY)
        except RedisError:
            logger.exception(f'Redis error occured at {__name__}, method: redis.incr')
        return workspace_response
    
