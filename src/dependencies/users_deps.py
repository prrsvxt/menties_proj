from fastapi import Depends
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.user_service import UserService
from src.repositories.user_repository import UserRepository
from src.db import get_session, get_transactional_session
from src.mappers.user_mapper import UserMapper


def get_user_mapper() -> UserMapper:
    return UserMapper()

def get_user_repository(
    db: AsyncSession = Depends(get_session),
) -> UserRepository:
    return UserRepository(db)

def get_transactional_user_repository(
    db: AsyncSession = Depends(get_transactional_session),
) -> UserRepository:
    return UserRepository(db)

def get_user_service(
    repository: UserRepository = Depends(get_user_repository),
    mapper: UserMapper = Depends(get_user_mapper)
) -> UserService:
    return UserService(repository, mapper)


def get_transactional_user_service(
    repository: UserRepository = Depends(get_transactional_user_repository),
    mapper: UserMapper = Depends(get_user_mapper)
) -> UserService:
    return UserService(repository, mapper)

GetUserService = Annotated[
    UserService,
    Depends(get_user_service),
]

TransactionalUserService = Annotated[
    UserService,
    Depends(get_transactional_user_service),
]