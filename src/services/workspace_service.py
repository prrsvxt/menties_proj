from uuid import UUID
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
from src.cache.keys import workspace_key, WORKSPACES_LIST_VERSION_KEY, workspace_list_version

logger = logging.getLogger(__name__)

class WorkspaceService(Service):
    def __init__(self, repository: WorkspaceRepository, mapper: WorkspaceMapper, redis: RedisCache):
        super().__init__(redis)
        self.repository = repository
        self.mapper = mapper

    async def _get_workspace_by_id(self, workspace_id: UUID) -> WorkspaceModel:
        workspace = await self.repository.get_workspace_by_id(workspace_id)

        if workspace is None:
            raise NotFoundError(f'Workspace with id={workspace_id} not found.')

        return workspace

    async def get_workspace_by_id(self, workspace_id: UUID) -> WorkspaceResponse:

        cached_workspace = await self.redis.get(workspace_key(workspace_id))

        if cached_workspace is None:
            workspace = await self._get_workspace_by_id(workspace_id)
            workspace_response = self.mapper.workspace_response_map(workspace)
            await self.redis.set(
                workspace_key(workspace_id),
                workspace_response.model_dump_json()
            )
            return workspace_response

        return WorkspaceResponse.model_validate_json(cached_workspace)

    async def list_workspaces(
            self,
            limit: int,
            cursor: str | None, 
    ) -> WorkspacePaginationResponse:
        cursor_workspace_id, cursor_timestamp = None, None
        if cursor:
            cursor_workspace_id, cursor_timestamp = self.cursor_decode(cursor)

        cache_version = await self.redis.get(WORKSPACES_LIST_VERSION_KEY)
        if cache_version is None:
            await self.redis.set(
                WORKSPACES_LIST_VERSION_KEY,
                '1',
                nx=True,
                use_ttl=False,
            )
            cache_version = await self.redis.get(WORKSPACES_LIST_VERSION_KEY)

        cached_data = await self.redis.get(workspace_list_version(cache_version, limit, cursor))

        if cached_data:
            return WorkspacePaginationResponse.model_validate_json(cached_data)

        workspaces = await self.repository.get_paginated_workspaces(
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

        await self.redis.set(
            workspace_list_version(cache_version, limit, cursor),
            workspaces_pagination_response.model_dump_json()
        )

        return workspaces_pagination_response
    
    async def create_workspace(self, data: WorkspaceCreate) -> WorkspaceResponse:
        workspace_data = self.mapper.workspace_create_map(data)
        workspace = await self.repository.create_workspace(workspace_data)

        await self.redis.incr(WORKSPACES_LIST_VERSION_KEY)
        return self.mapper.workspace_response_map(workspace)

    async def delete_workspace(self, workspace_id: UUID) -> None:
        workspace = await self._get_workspace_by_id(workspace_id)
        await self.repository.delete_workspace(workspace)
        await self.redis.delete([workspace_key(workspace_id)])

        await self.redis.incr(WORKSPACES_LIST_VERSION_KEY)

    async def update_workspace(
            self,
            workspace_id: UUID,
            data: WorkspaceUpdate,
    ) -> WorkspaceResponse:
        workspace = await self.repository.get_workspace_with_lock(workspace_id)

        if workspace is None:
            raise NotFoundError(f'Workspace with id={workspace_id} not found.')

        workspace = self.mapper.workspace_update_map(data, workspace)

        workspace = await self.repository.update_workspace(workspace)
        await self.redis.delete([workspace_key(workspace_id)])

        await self.redis.incr(WORKSPACES_LIST_VERSION_KEY)
        return self.mapper.workspace_response_map(workspace)
    
