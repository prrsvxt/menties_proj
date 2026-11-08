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

logger = logging.getLogger(__name__)

class WorkspaceService(Service):
    def __init__(self, repository: WorkspaceRepository, mapper: WorkspaceMapper):
        self.repository = repository
        self.mapper = mapper

    async def _get_workspace_by_id(self, workspace_id: UUID) -> WorkspaceModel:
        workspace = await self.repository.get_workspace_by_id(workspace_id)

        if workspace is None:
            raise NotFoundError(f'Workspace with id={workspace_id} not found.')

        return workspace

    async def get_workspace_by_id(self, workspace_id: UUID) -> WorkspaceResponse:
        workspace = await self._get_workspace_by_id(workspace_id)

        return self.mapper.workspace_response_map(workspace)

    async def list_workspaces(
            self,
            limit: int,
            cursor: str | None, 
    ) -> WorkspacePaginationResponse:
        cursor_workspace_id, cursor_timestamp = None, None
        if cursor:
            cursor_workspace_id, cursor_timestamp = self.cursor_decode(cursor)

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

        return self.mapper.workspace_pagination_response_map(workspaces, next_cursor)
    
    async def create_workspace(self, data: WorkspaceCreate) -> WorkspaceResponse:
        workspace_data = self.mapper.workspace_create_map(data)
        workspace = await self.repository.create_workspace(workspace_data)

        return self.mapper.workspace_response_map(workspace)

    async def delete_workspace(self, workspace_id: UUID) -> None:
        workspace = await self._get_workspace_by_id(workspace_id)
        await self.repository.delete_workspace(workspace)

    async def update_workspace(
            self,
            workspace_id: UUID,
            data: WorkspaceUpdate,
    ) -> WorkspaceResponse:
        workspace = await self.repository.get_workspace_for_update(workspace_id)

        if workspace is None:
            raise NotFoundError(f'Workspace with id={workspace_id} not found.')

        workspace = self.mapper.workspace_update_map(data, workspace)

        workspace = await self.repository.update_workspace(workspace)
        return self.mapper.workspace_response_map(workspace)
    
