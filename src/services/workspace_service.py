from uuid import UUID
import logging

from src.exceptions.general_errors import NotFoundError
from src.repositories.workspace_repository import WorkspaceRepository
from src.schemas.workspace import WorkspaceCreate, WorkspaceResponse, WorkspaceUpdate
from src.models.workspace import WorkspaceModel
from src.mappers.workspace_mapper import WorkspaceMapper

logger = logging.getLogger(__name__)

class WorkspaceService:
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
            offset: int,
    ) -> list[WorkspaceResponse]:
        workspaces = await self.repository.get_paginated_workspaces(
            limit=limit,
            offset=offset,
        )
        return [
            self.mapper.workspace_response_map(workspace)
            for workspace in workspaces
        ]
    
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
        workspace = await self._get_workspace_by_id(workspace_id)
        workspace = self.mapper.workspace_update_map(data, workspace)

        workspace = await self.repository.update_workspace(workspace)
        return self.mapper.workspace_response_map(workspace)
    
