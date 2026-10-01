import logging
from uuid import UUID

from src.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from src.repositories.project_repository import ProjectRepository
from src.repositories.tag_repository import TagRepository
from src.mappers.project_mapper import ProjectMapper
from src.models.project import Project
from src.exceptions.general_errors import NotFoundError


logger = logging.getLogger(__name__)

class ProjectService:
    def __init__(
            self, 
            project_repository: ProjectRepository, 
            tag_repository: TagRepository,
            mapper: ProjectMapper
        ):
        self.project_repository = project_repository
        self.tag_repository = tag_repository
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
            offset: int
    ) -> list[ProjectResponse]:
        projects = await self.project_repository.get_paginated_projects(
            limit=limit,
            offset=offset
        )

        projects = [self.mapper.project_response_map(project) for project in projects]
        return projects

    async def create_project(
            self,
            data: ProjectCreate
    ) -> ProjectResponse:
        tags = await self.tag_repository.get_tags_by_ids(data.tag_ids)
        project_model = self.mapper.project_create_map(data, tags)
        project = await self.project_repository.create_project(project_model)
        return self.mapper.project_response_map(project)

    async def update_project(
            self,
            project_id: UUID,
            data: ProjectUpdate
    ) -> ProjectResponse:
        project = await self._get_project_by_id(project_id)

        if data.tag_ids is None:
            tags = project.tags
        else:
            tags = await self.tag_repository.get_tags_by_ids(data.tag_ids)

        project = self.mapper.project_update_map(data, tags, project)
        project = await self.project_repository.update_project(project)
        return self.mapper.project_response_map(project)

    async def delete_project(
            self, 
            project_id: UUID
    ) -> None:
        project = await self._get_project_by_id(project_id)
        await self.project_repository.delete_project(project)
