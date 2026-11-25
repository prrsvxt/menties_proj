import logging
from uuid import UUID
from redis.exceptions import RedisError

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
from src.cache.redis_cache import RedisCache
from src.UoW.project_UoW import ProjectUoW


logger = logging.getLogger(__name__)

class ProjectService(Service):
    CACHE_VERSION = 'v1'
    PROJECTS_LIST_VERSION_KEY = 'projects:list:version'

    def __init__(
            self, 
            unit_of_work: ProjectUoW, 
            mapper: ProjectMapper,
            redis: RedisCache
        ):
        self.unit_of_work = unit_of_work
        self.mapper = mapper
        self.redis = redis

    @classmethod
    def project_key(cls, project_id: UUID) -> str:
        return f'{cls.CACHE_VERSION}:project:{project_id}'

    @classmethod
    def project_list_version(
            cls,
            version: int,
            limit: int,
            cursor: str | None,
    ) -> str:
        page = cursor if cursor else 'first'
        return f'{cls.CACHE_VERSION}:projects:list:v{version}:limit{limit}:{page}'

    async def _get_project_by_id(
            self, 
            project_id: UUID
    ) -> Project:

        async with self.unit_of_work as uow:
            project = await uow.project_repository.get_project_by_id(project_id)

        if project is None:
            raise NotFoundError(f'Project with ID={project_id} not found')

        return project

    async def get_project_by_id(
            self,
            project_id: UUID
    ) -> ProjectResponse:

        try:
            cached_project = await self.redis.get(self.project_key(project_id))
        except RedisError:
            logger.exception(f'Redis error occured at {__name__}, method: redis.get')
            cached_project = None

        if cached_project:
            return ProjectResponse.model_validate_json(cached_project)
        
        project = await self._get_project_by_id(project_id)
        project_response = self.mapper.project_response_map(project)

        try:
            await self.redis.set(
                self.project_key(project_id),
                project_response.model_dump_json()
            )
        except RedisError:
            logger.exception(f'Redis error occured at {__name__}, method: redis.set')
        return project_response


    async def list_projects(
            self,
            limit: int,
            cursor: str | None
    ) -> ProjectPaginationResponse: 
        
        cursor_project_id, cursor_timestamp = None, None
        if cursor:
            cursor_project_id, cursor_timestamp = self.cursor_decode(cursor)

        cache_version = await self.redis.get_list_version(self.PROJECTS_LIST_VERSION_KEY)

        if cache_version:
            try:
                cached_data = await self.redis.get(
                    self.project_list_version(cache_version, limit, cursor)
                )
            except RedisError:
                logger.exception(f'Redis error occured at {__name__}, method: redis.get')
                cached_data = None

            if cached_data:
                return ProjectPaginationResponse.model_validate_json(cached_data)
                   
        async with self.unit_of_work as uow:
            projects = await uow.project_repository.get_paginated_projects(
                    limit=limit,
                    cursor_project_id=cursor_project_id,
                    cursor_timestamp=cursor_timestamp,
                )

        next_cursor = None
        if len(projects) > limit:
            last_project = projects[limit - 1]
            projects = projects[:limit]
            next_cursor = self.cursor_encode(last_project)

        project_pagination_response = self.mapper.project_pagination_response_map(
            projects,
            next_cursor,
        )

        if cache_version:
            try:
                await self.redis.set(
                    self.project_list_version(
                        int(cache_version),
                        limit,
                        cursor
                    ),
                    project_pagination_response.model_dump_json()
                )
            except RedisError:
                logger.exception(f'Redis error occured at {__name__}, method: redis.set')
        return project_pagination_response

    async def create_project(
            self,
            data: ProjectCreate
    ) -> ProjectResponse:
        project_model = self.mapper.project_create_map(data)
        async with self.unit_of_work as uow:
            project = await uow.project_repository.create_project(project_model)
        project_response = self.mapper.project_response_map(project)
        try:
            await self.redis.set(
                self.project_key(project.id),
                project_response.model_dump_json()
            )
        except RedisError:
            logger.exception(f'Redis error occured at {__name__}, method: redis.set')
        try:
            await self.redis.incr(self.PROJECTS_LIST_VERSION_KEY)
            
        except RedisError:
            logger.exception(f'Redis error occured at {__name__}, method: redis.incr')
        return project_response

    async def update_project(
            self,
            project_id: UUID,
            data: ProjectUpdate
    ) -> ProjectResponse:

        async with self.unit_of_work as uow:
            project = await uow.project_repository.get_project_with_lock(project_id)

            if project is None:
                raise NotFoundError(f'Project with ID={project_id} not found')

            project, tags = self.mapper.project_update_map(data, project)
            project = await uow.project_repository.update_project(project, tags)

        project_response = self.mapper.project_response_map(project)
        try:
            await self.redis.set(
                self.project_key(project_id),
                project_response.model_dump_json()
            )
        except RedisError:
            logger.exception(f'Redis error occured at {__name__}, method: redis.set')

        try:
            await self.redis.incr(self.PROJECTS_LIST_VERSION_KEY)
        except RedisError:
            logger.exception(f'Redis error occured at {__name__}, method: redis.incr')

        return project_response

    async def delete_project(
            self, 
            project_id: UUID
    ) -> None:
        async with self.unit_of_work as uow:
            project = await uow.project_repository.get_project_by_id(project_id)
            if project:
                await uow.project_repository.delete_project(project)
        try:
            await self.redis.delete([self.project_key(project_id)])
        except RedisError:
            logger.exception(f'Redis error occured at {__name__}, method: redis.delete')

        try:
            await self.redis.incr(self.PROJECTS_LIST_VERSION_KEY)
        except RedisError:
            logger.exception(f'Redis error occured at {__name__}, method: redis.incr')
