from uuid import UUID
import logging

from src.repositories.user_repository import UserRepository
from src.mappers.user_mapper import UserMapper
from src.schemas.user import UserCreate, UserUpdate, UserResponse
from src.exceptions.general_errors import NotFoundError
from src.models.users import UserModel

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, repository: UserRepository, mapper: UserMapper):
        self.repository = repository
        self.mapper = mapper

    async def _get_user_by_id(self, user_id: UUID) -> UserModel:
        user = await self.repository.get_user_by_id(user_id)

        if user is None:
            # эта ошибка уже логгируется в exception_handlers.py 
            raise NotFoundError(f"User with ID={user_id} not found")

        return user

    async def get_user_by_id(self, user_id: UUID) -> UserResponse:
        user = await self._get_user_by_id(user_id=user_id)
        
        return self.mapper.user_response_map(user)

    async def create_user(self, data: UserCreate) -> UserResponse:
        user_data = self.mapper.user_create_map(data)
        user = await self.repository.create_user(user_data)
        return self.mapper.user_response_map(user)

    async def update_user(self, user_id: UUID, data: UserUpdate) -> UserResponse:
        user = await self._get_user_by_id(user_id=user_id)
        user = self.mapper.user_update_map(data, user)

        user = await self.repository.update_user(user)
        return self.mapper.user_response_map(user)

    async def delete_user(self, user_id: UUID) -> None:
        user = await self._get_user_by_id(user_id)
        await self.repository.delete_user(user)

    