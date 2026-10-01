from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_session, get_transactional_session
from src.mappers.tag_mapper import TagMapper
from src.repositories.tag_repository import TagRepository
from src.services.tag_service import TagService


def get_tag_repository(
        db: AsyncSession = Depends(get_session),
) -> TagRepository:
    return TagRepository(db)


def get_transactional_tag_repository(
        db: AsyncSession = Depends(get_transactional_session),
) -> TagRepository:
    return TagRepository(db)


def get_tag_mapper() -> TagMapper:
    return TagMapper()


def get_tag_service(
        repository: TagRepository = Depends(get_tag_repository),
        mapper: TagMapper = Depends(get_tag_mapper),
) -> TagService:
    return TagService(repository, mapper)


def get_transactional_tag_service(
        repository: TagRepository = Depends(
            get_transactional_tag_repository,
        ),
        mapper: TagMapper = Depends(get_tag_mapper),
) -> TagService:
    return TagService(repository, mapper)


GetTagService = Annotated[
    TagService,
    Depends(get_tag_service),
]

TransactionalTagService = Annotated[
    TagService,
    Depends(get_transactional_tag_service),
]
