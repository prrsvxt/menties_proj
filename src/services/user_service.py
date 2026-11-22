from uuid import UUID
import logging

from src.repositories.user_repository import UserRepository
from src.mappers.user_mapper import UserMapper
from src.schemas.user import UserCreate, UserUpdate, UserResponse
from src.exceptions.general_errors import NotFoundError
from src.models.users import UserModel
from src.services.service import Service
from src.cache.redis_cache import RedisCache
from src.cache.keys import user_key

logger = logging.getLogger(__name__)

class UserService(Service):
    def __init__(self, repository: UserRepository, mapper: UserMapper, redis: RedisCache):
        super().__init__(redis)
        self.repository = repository
        self.mapper = mapper

    async def _get_user_by_id(self, user_id: UUID) -> UserModel:
        user = await self.repository.get_user_by_id(user_id)

        if user is None:
            # эта ошибка уже логгируется в exception_handlers.py 
            raise NotFoundError(f"User with ID={user_id} not found")

        return user

    async def get_user_by_id(self, user_id: UUID) -> UserResponse:

        cached_user = await self.redis.get(user_key(user_id))

        if cached_user is None:
            user = await self._get_user_by_id(user_id=user_id)
            user_response = self.mapper.user_response_map(user)
            await self.redis.set(
                user_key(user_id),
                user_response.model_dump_json()
            )
            return user_response
        
        return UserResponse.model_validate_json(cached_user)

    async def create_user(self, data: UserCreate) -> UserResponse:
        user_data = self.mapper.user_create_map(data)
        user = await self.repository.create_user(user_data)
        return self.mapper.user_response_map(user)

    async def update_user(self, user_id: UUID, data: UserUpdate) -> UserResponse:
        user = await self.repository.get_user_with_lock(user_id=user_id)

        if user is None:
            raise NotFoundError(f'User with ID={user_id} not found')

        user = self.mapper.user_update_map(data, user)

        user = await self.repository.update_user(user)
        await self.redis.delete([user_key(user_id)])
        return self.mapper.user_response_map(user)

    async def delete_user(self, user_id: UUID) -> None:
        user = await self._get_user_by_id(user_id)
        await self.repository.delete_user(user)
        await self.redis.delete([user_key(user_id)])
