from fastapi import Depends, Request
from typing import Annotated

from src.services.user_service import UserService
from src.mappers.user_mapper import UserMapper
from src.cache.redis_cache import RedisCache
from src.dependencies.cache_deps import get_redis
from src.UoW.user_UoW import UserUoW


def get_user_mapper() -> UserMapper:
    return UserMapper()

def get_user_unit_of_work(request: Request) -> UserUoW:
    session_factory = request.app.state.session_factory
    return UserUoW(session_factory)

def get_user_service(
    unit_of_work: UserUoW = Depends(get_user_unit_of_work),
    mapper: UserMapper = Depends(get_user_mapper),
    redis: RedisCache = Depends(get_redis),
) -> UserService:
    return UserService(unit_of_work, mapper, redis)


GetUserService = Annotated[
    UserService,
    Depends(get_user_service),
]
