from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_session, get_transactional_session
from src.mappers.project_mapper import ProjectMapper
from src.repositories.project_repository import ProjectRepository
from src.repositories.tag_repository import TagRepository
from src.services.project_service import ProjectService
from src.dependencies.tag_deps import (
    get_tag_repository,
    get_transactional_tag_repository,
)


def get_project_mapper() -> ProjectMapper:
    return ProjectMapper()


def get_project_repository(
        db: AsyncSession = Depends(get_session),
) -> ProjectRepository:
    return ProjectRepository(db)


def get_transactional_project_repository(
        db: AsyncSession = Depends(get_transactional_session),
) -> ProjectRepository:
    return ProjectRepository(db)


def get_project_service(
        project_repository: ProjectRepository = Depends(get_project_repository),
        tag_repository: TagRepository = Depends(get_tag_repository),
        mapper: ProjectMapper = Depends(get_project_mapper),
) -> ProjectService:
    return ProjectService(project_repository, tag_repository, mapper)


def get_transactional_project_service(
        project_repository: ProjectRepository = Depends(
            get_transactional_project_repository,
        ),
        tag_repository: TagRepository = Depends(
            get_transactional_tag_repository,
        ),
        mapper: ProjectMapper = Depends(get_project_mapper),
) -> ProjectService:
    return ProjectService(project_repository, tag_repository, mapper)


GetProjectService = Annotated[
    ProjectService,
    Depends(get_project_service),
]

TransactionalProjectService = Annotated[
    ProjectService,
    Depends(get_transactional_project_service),
]
