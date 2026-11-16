import logging
from uuid import UUID

from src.schemas.project import (
    ProjectCreate,
    ProjectPaginationResponse,
    ProjectResponse,
    ProjectUpdate,
)
from src.repositories.project_repository import ProjectRepository
from src.mappers.project_mapper import ProjectMapper
from src.models.project import Project
from src.exceptions.general_errors import NotFoundError
from src.services.service import Service


logger = logging.getLogger(__name__)

class ProjectService(Service):
    def __init__(
            self, 
            project_repository: ProjectRepository, 
            mapper: ProjectMapper
        ):
        self.project_repository = project_repository
        self.mapper = mapper

    async def _get_project_by_id(
            self, 
            project_id: UUID
    ) -> Project:
        project = await self.project_repository.get_project_by_id(project_id)

        if project is None:
            raise NotFoundError(f'Project with ID={project_id} not found')

        return project

    async def get_project_by_id(
            self,
            project_id: UUID
    ) -> ProjectResponse:
        project = await self._get_project_by_id(project_id)
        return self.mapper.project_response_map(project)

    async def list_projects(
            self,
            limit: int,
            cursor: str | None
    ) -> ProjectPaginationResponse:
        cursor_project_id, cursor_timestamp = None, None
        if cursor:
            cursor_project_id, cursor_timestamp = self.cursor_decode(cursor)

        projects = await self.project_repository.get_paginated_projects(
            limit=limit,
            cursor_project_id=cursor_project_id,
            cursor_timestamp=cursor_timestamp,
        )

        next_cursor = None
        if len(projects) > limit:
            last_project = projects[limit - 1]
            projects = projects[:limit]
            next_cursor = self.cursor_encode(last_project)

        return self.mapper.project_pagination_response_map(
            projects,
            next_cursor,
        )

    async def create_project(
            self,
            data: ProjectCreate
    ) -> ProjectResponse:
        project_model = self.mapper.project_create_map(data)
        project = await self.project_repository.create_project(project_model)
        return self.mapper.project_response_map(project)

    async def update_project(
            self,
            project_id: UUID,
            data: ProjectUpdate
    ) -> ProjectResponse:
        project = await self.project_repository.get_project_with_lock(project_id)

        if project is None:
            raise NotFoundError(f'Project with ID={project_id} not found')

        project, tags = self.mapper.project_update_map(data, project)
        project = await self.project_repository.update_project(project, tags)
        return self.mapper.project_response_map(project)

    async def delete_project(
            self, 
            project_id: UUID
    ) -> None:
        project = await self._get_project_by_id(project_id)
        await self.project_repository.delete_project(project)
