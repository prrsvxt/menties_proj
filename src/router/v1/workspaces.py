from fastapi import APIRouter, Query, status
from uuid import UUID

from src.dependencies.workspace_deps import GetWorkspaceService
from src.schemas.workspace import (
    WorkspaceResponse, 
    WorkspaceCreate, 
    WorkspaceUpdate, 
    WorkspacePaginationResponse
)


router = APIRouter(
    prefix='/workspaces',
    tags=['workspaces']
)


@router.get(
    '/',
    response_model=WorkspacePaginationResponse,
    status_code=status.HTTP_200_OK,
)
async def get_workspaces(
    service: GetWorkspaceService,
    limit: int = Query(default=10, ge=1, le=100),
    cursor: str | None = None,
):
    return await service.list_workspaces(limit=limit, cursor=cursor)

@router.get(
    '/{workspace_id}', 
    response_model=WorkspaceResponse, 
    status_code=status.HTTP_200_OK
)
async def get_workspace_by_id(
    workspace_id: UUID,
    service: GetWorkspaceService
):
    return await service.get_workspace_by_id(workspace_id)


@router.post(
    '/',
    response_model=WorkspaceResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_workspace(
    data: WorkspaceCreate,
    service: GetWorkspaceService
):
    workspace = await service.create_workspace(data)

    return workspace

@router.put(
    '/{workspace_id}',
    response_model=WorkspaceResponse,
    status_code=status.HTTP_200_OK
)
async def update_workspace(
    workspace_id: UUID,
    data: WorkspaceUpdate,
    service: GetWorkspaceService
):
    return await service.update_workspace(
        workspace_id,
        data
    )

@router.delete(
    '/{workspace_id}',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_workspace(
    workspace_id: UUID,
    service: GetWorkspaceService
):
    await service.delete_workspace(workspace_id)
