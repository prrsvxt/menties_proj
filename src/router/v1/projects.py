from uuid import UUID

from fastapi import APIRouter, Query, status

from src.dependencies.project_deps import (
    GetProjectService,
    TransactionalProjectService,
)
from src.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate


router = APIRouter(
    prefix='/projects',
    tags=['projects'],
)


@router.get(
    '/',
    response_model=list[ProjectResponse],
    status_code=status.HTTP_200_OK,
)
async def get_projects(
        service: GetProjectService,
        limit: int = Query(default=10, ge=1, le=100),
        offset: int = Query(default=0, ge=0),
):
    return await service.list_projects(limit=limit, offset=offset)


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
        service: TransactionalProjectService,
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
        service: TransactionalProjectService,
):
    return await service.update_project(project_id, data)


@router.delete(
    '/{project_id}',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_project(
        project_id: UUID,
        service: TransactionalProjectService,
):
    await service.delete_project(project_id)
