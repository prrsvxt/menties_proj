from uuid import UUID
import logging
from redis.exceptions import RedisError

from src.mappers.user_mapper import UserMapper
from src.schemas.user import UserCreate, UserUpdate, UserResponse
from src.exceptions.general_errors import NotFoundError
from src.models.users import UserModel
from src.services.service import Service
from src.cache.redis_cache import RedisCache
from src.UoW.user_UoW import UserUoW

logger = logging.getLogger(__name__)

class UserService(Service):
    CACHE_VERSION = 'v1'

    def __init__(self, unit_of_work: UserUoW, mapper: UserMapper, redis: RedisCache):
        self.unit_of_work = unit_of_work
        self.mapper = mapper
        self.redis = redis

    @classmethod
    def user_key(cls, user_id: UUID) -> str:
        return f'{cls.CACHE_VERSION}:user:{user_id}'

    async def _get_user_by_id(self, user_id: UUID) -> UserModel:

        async with self.unit_of_work as uow:
            user = await uow.user_repository.get_user_by_id(user_id)

        if user is None:
            # эта ошибка уже логгируется в exception_handlers.py 
            raise NotFoundError(f"User with ID={user_id} not found")

        return user

    async def get_user_by_id(self, user_id: UUID) -> UserResponse:

        try:
            cached_user = await self.redis.get(self.user_key(user_id))
        except RedisError:
            logger.exception(f'Redis error occured at {__name__}, method: redis.get')
            cached_user = None

        if cached_user:
            return UserResponse.model_validate_json(cached_user)
        user = await self._get_user_by_id(user_id=user_id)
        user_response = self.mapper.user_response_map(user)
        try:
            await self.redis.set(
                self.user_key(user_id),
                user_response.model_dump_json()
            )
        except RedisError:
            logger.exception(f'Redis error occured at {__name__}, method: redis.set')
        return user_response

    async def create_user(self, data: UserCreate) -> UserResponse:
        user_data = self.mapper.user_create_map(data)
        async with self.unit_of_work as uow:
            user = await uow.user_repository.create_user(user_data)
        return self.mapper.user_response_map(user)

    async def update_user(self, user_id: UUID, data: UserUpdate) -> UserResponse:
        async with self.unit_of_work as uow:
            user = await uow.user_repository.get_user_with_lock(user_id=user_id)

            if user is None:
                raise NotFoundError(f'User with ID={user_id} not found')

            user = self.mapper.user_update_map(data, user)

            user = await uow.user_repository.update_user(user)
        try:
            await self.redis.delete([self.user_key(user_id)])
        except RedisError:
            logger.exception(f'Redis error occured at {__name__}, method: redis.delete')
        return self.mapper.user_response_map(user)

    async def delete_user(self, user_id: UUID) -> None:
        async with self.unit_of_work as uow:
            user = await uow.user_repository.get_user_by_id(user_id)
            if user:
                await uow.user_repository.delete_user(user)
        try:
            await self.redis.delete([self.user_key(user_id)])
        except RedisError:
            logger.exception(f'Redis error occured at {__name__}, method: redis.delete')
