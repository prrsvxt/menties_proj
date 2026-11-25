from uuid import UUID

from fastapi import APIRouter, Query, status

from src.dependencies.project_deps import (
    GetProjectService,
)
from src.schemas.project import (
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
    ProjectPaginationResponse)


router = APIRouter(
    prefix='/projects',
    tags=['projects'],
)


@router.get(
    '/',
    response_model=ProjectPaginationResponse,
    status_code=status.HTTP_200_OK,
)
async def get_projects(
        service: GetProjectService,
        limit: int = Query(default=10, ge=1, le=100),
        cursor: str | None = Query(default=None),
):
    return await service.list_projects(limit=limit, cursor=cursor)


@router.get(
    '/{project_id}',
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
)
async def get_project_by_id(
        project_id: UUID,
        service: GetProjectService,
):
    return await service.get_project_by_id(project_id)


@router.post(
    '/',
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_project(
        data: ProjectCreate,
        service: GetProjectService,
):
    return await service.create_project(data)


@router.put(
    '/{project_id}',
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
)
async def update_project(
        project_id: UUID,
        data: ProjectUpdate,
        service: GetProjectService,
):
    return await service.update_project(project_id, data)


@router.delete(
    '/{project_id}',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_project(
        project_id: UUID,
        service: GetProjectService,
):
    await service.delete_project(project_id)
